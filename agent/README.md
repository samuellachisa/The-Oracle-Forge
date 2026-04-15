# Agent Directory

This directory holds the benchmark-submission-facing agent description.

Current code still lives under [src](/shared/DataAgentBench/oracle_forge_v3/src). This folder exists to satisfy the submission-oriented repo shape expected by the programme manual.

Contents:

- [AGENT.md](/shared/DataAgentBench/oracle_forge_v3/agent/AGENT.md)
- [tools.yaml](/shared/DataAgentBench/oracle_forge_v3/agent/tools.yaml) (submission-facing MCP config covering PostgreSQL, SQLite, MongoDB, DuckDB)
- [requirements.txt](/shared/DataAgentBench/oracle_forge_v3/agent/requirements.txt)
- [SOURCE_INDEX.md](/shared/DataAgentBench/oracle_forge_v3/agent/SOURCE_INDEX.md) (maps to runtime files in `src/`)

Runtime entry points used in practice:

- `run_agent.py`
- `run_benchmark_query.py`
