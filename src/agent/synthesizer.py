"""
synthesizer.py

Converts validated execution artifacts into a user-facing answer.
"""

from __future__ import annotations

from typing import Any


class AnswerSynthesizer:
    def synthesize(
        self,
        question: str,
        plan: dict[str, Any],
        context_payload: dict[str, Any],
        execution_result: dict[str, Any],
        validation: dict[str, Any],
    ) -> str:
        if validation.get("status") != "passed":
            return (
                "I could not produce a fully validated answer. "
                f"Failure class: {validation.get('failure_class')}. "
                f"Validation errors: {', '.join(validation.get('errors', []))}"
            )

        benchmark_answer = execution_result.get("artifacts", {}).get("benchmark_answer")
        if benchmark_answer:
            city = benchmark_answer.get("city", "the requested location")
            state_name = benchmark_answer.get("state_name", "")
            location = city if not state_name else f"{city}, {state_name}"
            return (
                f"The average rating of all businesses located in {location} is "
                f"{benchmark_answer['formatted_answer']} based on "
                f"{benchmark_answer['review_count']} reviews across "
                f"{benchmark_answer['matched_business_count']} matching businesses."
            )

        if plan.get("question_type") == "schema_discovery":
            parts = []
            for source, result in execution_result.get("source_results", {}).items():
                tables = result.get("table_names", [])
                parts.append(f"{source} exposes: {', '.join(tables)}")
            return "Schema discovery complete. " + " | ".join(parts)

        if plan.get("expected_output_shape") == "count_summary":
            postgres_rows = execution_result.get("source_results", {}).get("postgres", {}).get("rows", [])
            if postgres_rows:
                row = postgres_rows[0]
                value = next(iter(row.values()))
                return f"Validated count result: {value}."

        segment_rollup = execution_result.get("artifacts", {}).get("segment_rollup", [])
        if segment_rollup:
            top = segment_rollup[0]
            return (
                "Cross-database analysis complete. "
                f"Top segment: {top.get('segment', 'unknown')} "
                f"with {top.get('order_count', 0)} orders and "
                f"{top.get('ticket_count', 0)} tickets."
            )

        evidence = validation.get("evidence", [])
        return "Validated analytical summary complete. Evidence: " + "; ".join(evidence)
