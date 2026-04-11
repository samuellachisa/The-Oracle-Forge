"""
execution_router.py

Dispatches to narrow DB and transform tools and returns structured results.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from src.dab.remote_dab_adapter import RemoteDABAdapter
from src.tools.remote_sandbox import RemoteSandboxClient
from src.tools.toolbox_client import ToolboxClient
from src.tools.transform_tools import aggregate_by_field, extract_rows_with_facts, join_on_normalized_key, run_python_transform


class ExecutionRouter:
    STATE_ABBREVIATIONS = {
        "alabama": "AL",
        "alaska": "AK",
        "arizona": "AZ",
        "arkansas": "AR",
        "california": "CA",
        "colorado": "CO",
        "connecticut": "CT",
        "delaware": "DE",
        "florida": "FL",
        "georgia": "GA",
        "hawaii": "HI",
        "idaho": "ID",
        "illinois": "IL",
        "indiana": "IN",
        "iowa": "IA",
        "kansas": "KS",
        "kentucky": "KY",
        "louisiana": "LA",
        "maine": "ME",
        "maryland": "MD",
        "massachusetts": "MA",
        "michigan": "MI",
        "minnesota": "MN",
        "mississippi": "MS",
        "missouri": "MO",
        "montana": "MT",
        "nebraska": "NE",
        "nevada": "NV",
        "new hampshire": "NH",
        "new jersey": "NJ",
        "new mexico": "NM",
        "new york": "NY",
        "north carolina": "NC",
        "north dakota": "ND",
        "ohio": "OH",
        "oklahoma": "OK",
        "oregon": "OR",
        "pennsylvania": "PA",
        "rhode island": "RI",
        "south carolina": "SC",
        "south dakota": "SD",
        "tennessee": "TN",
        "texas": "TX",
        "utah": "UT",
        "vermont": "VT",
        "virginia": "VA",
        "washington": "WA",
        "west virginia": "WV",
        "wisconsin": "WI",
        "wyoming": "WY",
    }

    def __init__(self):
        self.remote_sandbox = RemoteSandboxClient()
        self.remote_dab = RemoteDABAdapter(self.remote_sandbox)
        self.toolbox = ToolboxClient()

    def execute_plan(
        self,
        question: str,
        plan: dict[str, Any],
        context_payload: dict[str, Any],
        scratchpads: list[dict[str, Any]],
        repair_context: dict[str, Any] | None = None,
        benchmark_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        repair_context = repair_context or {}
        benchmark_context = benchmark_context or {}
        tool_calls: list[dict[str, Any]] = []
        source_results: dict[str, Any] = {}
        artifacts: dict[str, Any] = {}
        errors: list[str] = []
        use_remote_sandbox = self.remote_sandbox.enabled()
        use_remote_dab = use_remote_sandbox and bool(benchmark_context.get("dataset"))

        question_type = plan.get("question_type")
        required_sources = plan.get("required_sources", [])

        if use_remote_dab:
            return self._execute_remote_dab(
                question=question,
                plan=plan,
                benchmark_context=benchmark_context,
                tool_calls=tool_calls,
            )

        if question_type == "schema_discovery":
            if use_remote_sandbox:
                remote_status = self.remote_sandbox.verify_dab_checkout()
                artifacts["remote_sandbox"] = remote_status
                tool_calls.append({"tool": "remote_verify_dab_checkout", "mode": "mcp-bridge"})
            for source in required_sources:
                schema = self.toolbox.inspect_schema(source)
                tool_calls.append(
                    {
                        "tool": "toolbox_inspect_schema" if self.toolbox.available() else "inspect_schema",
                        "source": source,
                        "mode": "toolbox" if self.toolbox.available() else "local-fallback",
                    }
                )
                source_results[source] = schema
            return {
                "success": all(result.get("ok") for result in source_results.values()),
                "tool_calls": tool_calls,
                "source_results": source_results,
                "artifacts": artifacts,
                "errors": errors,
            }

        for source in required_sources:
            result, tool_call = self.toolbox.execute_source(
                source=source,
                question=question,
                plan=plan,
                repair_context=repair_context,
            )
            tool_calls.append(tool_call)
            source_results[source] = result
            if not result.get("ok", False):
                errors.append(result.get("error", f"Unknown error while reading {source}"))

        if use_remote_sandbox:
            remote_repo = self.remote_sandbox.list_repo_root()
            artifacts["remote_sandbox"] = remote_repo
            tool_calls.append({"tool": "remote_list_repo_root", "mode": "mcp-bridge"})

        if plan.get("needs_text_extraction") and "mongodb" in source_results:
            extracted = extract_rows_with_facts(
                source_results["mongodb"].get("rows", []),
                text_field="note",
            )
            artifacts["extracted_text_facts"] = extracted
            tool_calls.append({"tool": "extract_structured_facts", "source": "mongodb"})

        if len(required_sources) > 1 and plan.get("join_keys"):
            left_rows = []
            right_rows = []
            if "postgres" in source_results:
                left_rows = source_results["postgres"].get("rows", [])
            if "mongodb" in source_results:
                right_rows = source_results["mongodb"].get("rows", [])
            elif "sqlite" in source_results:
                right_rows = source_results["sqlite"].get("rows", [])
            if left_rows and right_rows:
                joined = join_on_normalized_key(
                    left_rows=left_rows,
                    right_rows=right_rows,
                    left_key="customer_id",
                    right_key="customer_id",
                    entity="customer",
                )
                artifacts["joined_rows"] = joined
                tool_calls.append({"tool": "run_python_transform", "operation": "join_on_normalized_key", "mode": "local"})

        if "sqlite" in source_results and artifacts.get("joined_rows"):
            joined_with_segments = join_on_normalized_key(
                left_rows=artifacts["joined_rows"],
                right_rows=source_results["sqlite"].get("rows", []),
                left_key="customer_id",
                right_key="customer_id",
                entity="customer",
            )
            artifacts["joined_rows"] = joined_with_segments
            artifacts["segment_rollup"] = aggregate_by_field(
                rows=joined_with_segments,
                group_field="segment",
                metric_fields=["order_count", "ticket_count"],
            )
            tool_calls.append({"tool": "run_python_transform", "operation": "segment_rollup", "mode": "local"})

        if use_remote_sandbox and artifacts.get("joined_rows"):
            remote_script = (
                "print('remote sandbox ready for DAB transforms')\n"
                "print('joined_rows_present=True')\n"
            )
            remote_transform = run_python_transform(
                remote_script,
                use_remote=True,
                cwd=os.getenv("REMOTE_SANDBOX_DAB_PATH", "/shared/DataAgentBench"),
            )
            artifacts["remote_transform_probe"] = remote_transform
            tool_calls.append({"tool": "remote_run_python", "mode": "mcp-bridge"})

        return {
            "success": not errors,
            "tool_calls": tool_calls,
            "source_results": source_results,
            "artifacts": artifacts,
            "errors": errors,
        }

    def _execute_remote_dab(
        self,
        question: str,
        plan: dict[str, Any],
        benchmark_context: dict[str, Any],
        tool_calls: list[dict[str, Any]],
    ) -> dict[str, Any]:
        dataset = benchmark_context["dataset"]
        db_clients: dict[str, Any] = benchmark_context.get("db_clients", {})
        artifacts: dict[str, Any] = {"benchmark_context": benchmark_context}
        source_results: dict[str, Any] = {}
        errors: list[str] = []

        source_map: dict[str, list[str]] = {}
        for db_name, config in db_clients.items():
            db_type = config["db_type"]
            source_map.setdefault(db_type, []).append(db_name)
            if db_type == "mongo":
                source_map.setdefault("mongodb", []).append(db_name)
        artifacts["db_type_to_logical_names"] = source_map

        logical_db_names: list[str] = []
        for required_source in plan.get("required_sources", []):
            logical_db_names.extend(source_map.get(required_source, []))
        if not logical_db_names:
            logical_db_names = list(db_clients.keys())
        logical_db_names = list(dict.fromkeys(logical_db_names))

        for db_name in logical_db_names:
            listing = self.remote_dab.list_db_objects(dataset=dataset, db_name=db_name)
            tool_calls.append({"tool": "list_db", "dataset": dataset, "db_name": db_name, "mode": "remote-dab"})
            source_results[db_name] = listing
            if not listing.get("success", False):
                errors.append(f"list_db failed for {db_name}: {listing}")

        artifacts["logical_db_names"] = logical_db_names

        benchmark_strategy = self._run_benchmark_strategy(
            dataset=dataset,
            question=question,
            tool_calls=tool_calls,
        )
        if benchmark_strategy:
            artifacts.update(benchmark_strategy.get("artifacts", {}))
            source_results.update(benchmark_strategy.get("source_results", {}))
            errors.extend(benchmark_strategy.get("errors", []))

        count_queries: list[dict[str, Any]] = []
        if not artifacts.get("benchmark_answer") and plan.get("question_type") in {"count_query", "single_source_summary"}:
            for db_name, listing in source_results.items():
                objects = listing.get("result", [])
                if not isinstance(objects, list) or not objects:
                    continue
                first_object = objects[0]
                if db_clients[db_name]["db_type"] == "mongo":
                    query = json.dumps({"collection": first_object, "limit": 2})
                else:
                    query = f"SELECT * FROM {first_object} LIMIT 2;"
                query_result = self.remote_dab.query_db(dataset=dataset, db_name=db_name, query=query)
                tool_calls.append({"tool": "query_db", "dataset": dataset, "db_name": db_name, "query": query, "mode": "remote-dab"})
                count_queries.append({"db_name": db_name, "query": query, "result": query_result})
                if not query_result.get("success", False):
                    errors.append(f"query_db failed for {db_name}: {query_result}")
            artifacts["benchmark_query_samples"] = count_queries

        return {
            "success": not errors,
            "tool_calls": tool_calls,
            "source_results": source_results,
            "artifacts": artifacts,
            "errors": errors,
        }

    def _run_benchmark_strategy(
        self,
        dataset: str,
        question: str,
        tool_calls: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        dataset_key = dataset.lower()
        question_lower = question.lower()

        if dataset_key == "yelp" and "average rating" in question_lower and "located in" in question_lower:
            return self._solve_yelp_average_rating(question=question, tool_calls=tool_calls)

        return None

    def _solve_yelp_average_rating(
        self,
        question: str,
        tool_calls: list[dict[str, Any]],
    ) -> dict[str, Any]:
        city, state_name = self._extract_city_state(question)
        state_abbr = self._state_abbreviation(state_name)
        if not city or not state_name or not state_abbr:
            return {
                "artifacts": {},
                "source_results": {},
                "errors": ["Could not parse the benchmark location from the Yelp question."],
            }

        business_query = json.dumps({"collection": "business", "limit": None})
        business_result = self.remote_dab.query_db("yelp", "businessinfo_database", business_query)
        tool_calls.append(
            {
                "tool": "query_db",
                "dataset": "yelp",
                "db_name": "businessinfo_database",
                "query": business_query,
                "mode": "remote-dab",
            }
        )
        if not business_result.get("success", False):
            return {
                "artifacts": {},
                "source_results": {"businessinfo_database_query": business_result},
                "errors": ["Failed to retrieve Yelp business metadata from MongoDB."],
            }

        matched_business_refs: list[str] = []
        matched_businesses: list[dict[str, Any]] = []
        for row in business_result.get("result", []):
            business_id = row.get("business_id")
            description = str(row.get("description", ""))
            if not business_id or not description:
                continue
            if self._description_matches_location(description, city, state_name, state_abbr):
                matched_business_refs.append(self._business_id_to_review_ref(str(business_id)))
                matched_businesses.append(
                    {
                        "business_id": business_id,
                        "name": row.get("name"),
                        "description": description,
                    }
                )

        if not matched_business_refs:
            return {
                "artifacts": {},
                "source_results": {"businessinfo_database_query": business_result},
                "errors": ["No Yelp businesses matched the requested location."],
            }

        in_clause = ", ".join(f"'{business_ref}'" for business_ref in matched_business_refs)
        rating_query = (
            "SELECT AVG(CAST(rating AS DOUBLE)) AS avg_rating, "
            "COUNT(*) AS review_count "
            f"FROM review WHERE business_ref IN ({in_clause});"
        )
        review_result = self.remote_dab.query_db("yelp", "user_database", rating_query)
        tool_calls.append(
            {
                "tool": "query_db",
                "dataset": "yelp",
                "db_name": "user_database",
                "query": rating_query,
                "mode": "remote-dab",
            }
        )
        if not review_result.get("success", False):
            return {
                "artifacts": {"matched_businesses": matched_businesses},
                "source_results": {
                    "businessinfo_database_query": business_result,
                    "user_database_query": review_result,
                },
                "errors": ["Failed to aggregate Yelp ratings from DuckDB."],
            }

        review_rows = review_result.get("result", [])
        if not review_rows:
            return {
                "artifacts": {"matched_businesses": matched_businesses},
                "source_results": {
                    "businessinfo_database_query": business_result,
                    "user_database_query": review_result,
                },
                "errors": ["The Yelp review aggregation returned no rows."],
            }

        avg_rating = float(review_rows[0]["avg_rating"])
        review_count = int(review_rows[0]["review_count"])

        return {
            "artifacts": {
                "benchmark_answer": {
                    "dataset": "yelp",
                    "numeric_answer": avg_rating,
                    "formatted_answer": f"{avg_rating:.2f}",
                    "matched_business_count": len(matched_business_refs),
                    "review_count": review_count,
                    "city": city,
                    "state_name": state_name,
                    "state_abbr": state_abbr,
                },
                "matched_businesses": matched_businesses,
            },
            "source_results": {
                "businessinfo_database_query": business_result,
                "user_database_query": review_result,
            },
            "errors": [],
        }

    def _extract_city_state(self, question: str) -> tuple[str | None, str | None]:
        match = re.search(r"located in ([A-Za-z .'-]+),\s*([A-Za-z .'-]+)\??", question, flags=re.IGNORECASE)
        if not match:
            return None, None
        city = match.group(1).strip()
        state_name = match.group(2).strip().rstrip("?")
        return city, state_name

    def _state_abbreviation(self, state_name: str | None) -> str | None:
        if not state_name:
            return None
        normalized = state_name.strip().lower()
        if len(normalized) == 2:
            return normalized.upper()
        return self.STATE_ABBREVIATIONS.get(normalized)

    def _description_matches_location(
        self,
        description: str,
        city: str,
        state_name: str,
        state_abbr: str,
    ) -> bool:
        description_lower = description.lower()
        city_lower = city.lower()
        state_name_lower = state_name.lower()
        state_abbr_lower = state_abbr.lower()
        return (
            f"{city_lower}, {state_abbr_lower}" in description_lower
            or f"{city_lower}, {state_name_lower}" in description_lower
        )

    def _business_id_to_review_ref(self, business_id: str) -> str:
        return business_id.replace("businessid_", "businessref_", 1)
