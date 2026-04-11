"""
validator.py

Structured validation for execution results.
"""

from __future__ import annotations

from typing import Any


class Validator:
    def validate_execution(
        self,
        question: str,
        plan: dict[str, Any],
        execution_result: dict[str, Any],
        context_payload: dict[str, Any],
        benchmark_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        benchmark_context = benchmark_context or {}
        errors: list[str] = []
        evidence: list[str] = []
        failure_class = ""

        if not execution_result.get("success", False):
            failure_class = "execution_failure"
            errors.extend(execution_result.get("errors", ["Execution failed."]))

        required_sources = plan.get("required_sources", [])
        if benchmark_context.get("dataset"):
            logical_db_names = execution_result.get("artifacts", {}).get("logical_db_names", [])
            if not logical_db_names:
                failure_class = failure_class or "benchmark_source_resolution_failure"
                errors.append("No logical DAB databases were resolved for the benchmark dataset.")
            else:
                evidence.append(f"logical_db_names={','.join(logical_db_names)}")
            benchmark_answer = execution_result.get("artifacts", {}).get("benchmark_answer")
            if plan.get("expected_output_shape") == "benchmark_answer":
                if not benchmark_answer:
                    failure_class = failure_class or "benchmark_answer_missing"
                    errors.append("The benchmark execution did not produce a validated answer artifact.")
                else:
                    evidence.append(f"benchmark_answer={benchmark_answer['formatted_answer']}")
                    evidence.append(f"benchmark_reviews={benchmark_answer['review_count']}")
        for source in required_sources:
            if source not in execution_result.get("source_results", {}):
                if not benchmark_context.get("dataset"):
                    failure_class = failure_class or "routing_failure"
                    errors.append(f"Required source {source} was not executed.")

        if plan.get("question_type") == "schema_discovery":
            for source, result in execution_result.get("source_results", {}).items():
                table_names = result.get("table_names", [])
                if not table_names:
                    failure_class = failure_class or "schema_missing"
                    errors.append(f"No tables or collections were surfaced for {source}.")
                else:
                    evidence.append(f"{source}: {', '.join(table_names)}")

        if plan.get("expected_output_shape") == "ranked_segments_plus_explanation":
            segment_rollup = execution_result.get("artifacts", {}).get("segment_rollup", [])
            if not segment_rollup:
                failure_class = failure_class or "join_or_aggregation_failure"
                errors.append("Expected a segment rollup artifact for a cross-database analytical query.")
            else:
                evidence.append(f"segment_rollup_rows={len(segment_rollup)}")

        if plan.get("needs_text_extraction"):
            extracted = execution_result.get("artifacts", {}).get("extracted_text_facts", [])
            if not extracted:
                failure_class = failure_class or "extraction_failure"
                errors.append("Expected extracted text facts but none were produced.")
            else:
                evidence.append(f"extracted_rows={len(extracted)}")

        if not errors:
            for source, result in execution_result.get("source_results", {}).items():
                if result.get("row_count") is not None:
                    evidence.append(f"{source}_rows={result['row_count']}")

        return {
            "status": "passed" if not errors else "failed",
            "errors": errors,
            "failure_class": failure_class or "none",
            "evidence": evidence,
        }
