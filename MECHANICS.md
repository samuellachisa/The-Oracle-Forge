# The Mechanics: Oracle Forge Execution Flow

The Oracle Forge codebase is a sophisticated multi-agent system designed specifically for the DataAgentBench (DAB) challenge. It represents a "Production AI" approach that prioritizes context engineering and self-correction over raw model size.

### 1. High-Level Architecture: The "Executive Layer"
When you execute the agent, you are initializing the `Orchestrator` (the "brain" of Oracle Forge). Unlike a standard chatbot, Oracle Forge follows a structured logic loop:

**`python3 run_agent.py`**
- Starts the `Orchestrator` in [src/agent/orchestrator.py](/shared/DataAgentBench/oracle_forge_v3/src/agent/orchestrator.py).
- The Orchestrator manages several specialized modules:
    - **`Planner`**: Breaks the query into logical steps.
    - **`ContextCortex`**: The "memory retrieval" system that pulls from the Knowledge Base (KB).
    - **`ExecutionRouter`**: Decides which database (PostgreSQL, MongoDB, DuckDB) needs to be queried.
    - **`RepairLoop`**: If a query fails (e.g., a join-key mismatch), this module detects the error and attempts to fix the query logic automatically.

---

### 2. The Execution Path (Behind the Scenes)
Based on the command `python3 run_agent.py --dataset yelp --query_id 1 ...`, here is the internal execution sequence:

1.  **Input Loading**: The agent accesses the benchmark query folder to read the specific question (e.g., [query_yelp/query1/query.json](/shared/DataAgentBench/oracle_forge_v3/query_yelp/query1/query.json)).
2.  **Context Injection**: The `ContextCortex` scans the Knowledge Base (KB), including files like [kb/domain/CHANGELOG.md](/shared/DataAgentBench/oracle_forge_v3/kb/domain/CHANGELOG.md) and [kb/corrections/CHANGELOG.md](/shared/DataAgentBench/oracle_forge_v3/kb/corrections/CHANGELOG.md). It retrieves critical rules, such as mapping `businessid_*` (MongoDB) to `businessref_*` (DuckDB).
3.  **The LLM Loop (`DataAgent.py`)**:
    - The `DataAgent` class in [common_scaffold/DataAgent.py](/shared/DataAgentBench/oracle_forge_v3/common_scaffold/DataAgent.py) acts as the bridge to the LLM (e.g., Gemini 2.0 Flash).
    - It builds a prompt that includes the DB schema, the user question, and the specific domain knowledge retrieved from the KB.
    - The LLM emits "Tool Calls": `query_db` to fetch data or `execute_python` to process it.
4.  **Database Interaction**:
    - Tools like `QueryDBTool` connect to the Yelp databases.
    - Results are returned to the `DataAgent`, which feeds them back to the LLM for the next iterative step.
5.  **Validation**: Once a `final_answer` is produced, it is saved to logs and verified by the benchmark validator. If it matches the ground truth, the "Injection Test" sequence is complete.

---

### 3. Why the "Injection Tests" matter
The adversarial probes are the heartbeat of the **Self-Learning Loop**:
- **The Probe**: A query is run that is known to trigger a failure mode (e.g., a key mismatch).
- **The Failure**: The agent fails to produce a result.
- **The KB Fix**: A rule is added to the Knowledge Base to handle that specific edge case.
- **The Success**: On the next run, the `Planner` reads the updated KB, sees the rule, and generates a valid query plan.

This is what converts a "Demo Agent" into a "Production Agent." It doesn't just run code; it learns from its own execution traces to ensure it never makes the same mistake twice.

### Summary of the Trace

| Component | Responsibility | Shared Path Location |
| :--- | :--- | :--- |
| **Entrypoint** | Launches the runtime | [/shared/DataAgentBench/oracle_forge_v3/run_agent.py](/shared/DataAgentBench/oracle_forge_v3/run_agent.py) |
| **Orchestrator** | Coordinates Plan -> Context -> Execution | [/shared/DataAgentBench/oracle_forge_v3/src/agent/orchestrator.py](/shared/DataAgentBench/oracle_forge_v3/src/agent/orchestrator.py) |
| **Context** | Injects KB findings into the prompt | [/shared/DataAgentBench/oracle_forge_v3/src/kb/context_cortex.py](/shared/DataAgentBench/oracle_forge_v3/src/kb/context_cortex.py) |
| **DataAgent** | Manages LLM turns and tool calling | [/shared/DataAgentBench/oracle_forge_v3/common_scaffold/DataAgent.py](/shared/DataAgentBench/oracle_forge_v3/common_scaffold/DataAgent.py) |
| **Tools** | Runs actual SQL or Python | `/shared/DataAgentBench/oracle_forge_v3/common_scaffold/tools/` |
| **Validator** | Scores the final answer | [/shared/DataAgentBench/oracle_forge_v3/eval/harness_entry.py](/shared/DataAgentBench/oracle_forge_v3/eval/harness_entry.py) |
