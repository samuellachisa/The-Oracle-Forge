# Evaluation Directory

This directory holds benchmark-evaluation-facing artifacts for Oracle Forge.

Current implementation code lives in:

- [src/eval/harness.py](/shared/DataAgentBench/oracle_forge_v3/src/eval/harness.py)
- [src/eval/score_tracker.py](/shared/DataAgentBench/oracle_forge_v3/src/eval/score_tracker.py)
- [src/eval/trace_logger.py](/shared/DataAgentBench/oracle_forge_v3/src/eval/trace_logger.py)

Use this directory for:

- score logs
- held-out test sets
- benchmark notes
- submission-oriented evaluation outputs

Submission-facing evaluation scripts:

- `eval/run_initial_baseline.py` (runs held-out baseline and writes score + trace artifact)

Expected output artifact:

- `results/initial_baseline_with_trace.json`
