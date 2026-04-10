# Oracle Forge Winning Plan

## Goal

Build a production-grade data analytics agent that beats a naive text-to-SQL baseline on DataAgentBench by treating the system as an engineered runtime, not a single prompt.

The winning strategy is:

1. Use a Claude-Code-style central query engine with strict tool boundaries.
2. Use an OpenAI-style multi-layer context system, with offline enrichment and runtime retrieval.
3. Use a DAB-first evaluation loop that optimizes for the four benchmark failure classes:
   - multi-database integration
   - ill-formatted join keys
   - unstructured text transformation
   - domain knowledge gaps

## What We Should Borrow

### From Claude Code

- A single `QueryEngine` that owns the full turn lifecycle.
- Tool modularity: each tool has a narrow purpose, schema, and permission model.
- Persistent typed memory instead of one giant history blob.
- Background consolidation of corrections into durable memory.
- Sub-agent delegation only for bounded parallel work.

### From OpenAI's in-house data agent

- Context is the main bottleneck, not SQL generation.
- Offline enrichment should prepare context before the user asks a question.
- Memory should capture non-obvious corrections and filters.
- Runtime validation and self-correction should be built into the loop.
- Fewer, clearer tools beat a large overlapping tool set.

### From DataAgentBench

- The agent must solve routing, normalization, extraction, and domain interpretation together.
- Query correctness is not enough; answer traceability and repeated reliability matter.
- The fastest path to score improvement is failure-driven iteration on a held-out set, then full benchmark runs.

## Proposed System

## 1. Core Runtime

Build one orchestrator process with this loop:

`User Question -> Intent Parse -> Context Retrieval -> Plan -> Execute -> Validate -> Repair if Needed -> Synthesize -> Persist Learnings`

Core modules:

- `QueryEngine`
  - owns turn state
  - calls tools
  - enforces max iterations and retry budget
- `Planner`
  - decomposes the question into sub-questions, evidence needs, and expected output shape
- `ContextService`
  - fetches the minimum useful context from schema, KB, corrections, and runtime inspection
- `ExecutionManager`
  - runs subqueries, Python transforms, and database-specific steps
- `Validator`
  - checks row counts, join assumptions, result types, and contract conformance
- `LearningLoop`
  - writes durable corrections and successful patterns after each resolved failure

## 2. Tool Layer

Keep tools small and non-overlapping.

Recommended first tool set:

- `list_data_sources`
- `get_schema_summary`
- `inspect_table_samples`
- `run_sql_postgres`
- `run_sql_sqlite`
- `run_sql_duckdb`
- `run_mongo_pipeline`
- `normalize_join_key`
- `extract_structured_facts`
- `run_python_transform`
- `validate_answer_contract`
- `read_kb_context`
- `write_correction_memory`
- `get_past_failures`

Avoid giving the model multiple ways to do the same thing until the harness proves it helps.

## 3. Context Layers

Implement six layers even though the challenge requires only three.

### Layer 1: Schema and Usage Context

Store:

- table names
- columns and types
- database type
- likely primary keys
- likely foreign keys
- sample joins
- sample query patterns

Output format:

- compact JSON manifests
- one normalized record per table/collection

### Layer 2: Join-Key Intelligence

Store:

- canonical entity names
- format mappings like `12345 <-> CUST-12345`
- normalization regexes
- examples of successful reconciliations

This layer should be first-class, not hidden inside prompt text.

### Layer 3: Unstructured Field Intelligence

Store:

- which fields contain free text
- extraction recipes per field
- target structured outputs
- known keywords and patterns by dataset

### Layer 4: Domain and Institutional Knowledge

Store:

- definitions like "active customer", "repeat purchase", "churn"
- authoritative table preferences
- deprecated tables
- fiscal calendar rules
- benchmark-specific hints discovered during testing

### Layer 5: Corrections Memory

Store structured entries:

- failed query
- failure class
- root cause
- successful fix
- datasets involved
- confidence
- date added

### Layer 6: Runtime Context

Store per turn:

- live schema inspections
- sample values
- failed attempts
- current assumptions
- temporary intermediate results

## 4. DAB-Specific Execution Strategy

### A. Multi-Database Routing

Do not start with SQL generation.

First predict:

- which databases are needed
- which entities must be reconciled across them
- whether results can be joined in-database or must be joined in Python

Recommended approach:

- produce a typed execution plan before any query runs
- execute one worker per database when subqueries are independent
- merge in Python after normalization

### B. Ill-Formatted Join Keys

Always run a join-key analysis before any cross-database join.

Pipeline:

1. inspect sample values from both sources
2. classify format mismatch
3. pick a canonical form
4. normalize both sides
5. validate overlap before doing the final join

### C. Unstructured Text Transformation

Treat text extraction as a separate stage, not as a side effect.

Pipeline:

1. identify the free-text field
2. define the target structured signal
3. extract with a constrained schema
4. validate on samples
5. aggregate only after extraction succeeds

### D. Domain Knowledge

When a business term is ambiguous:

1. check KB definitions
2. check corrections memory
3. if still ambiguous, ask a clarifying question or apply a documented default

## 5. Validation and Self-Correction

Every run should pass through validation gates:

- syntax valid
- read-only safe
- non-empty where expected
- join cardinality plausible
- result types match expected question shape
- answer grounded in executed evidence

Repair triggers:

- zero rows after an expected join
- suspiciously large row explosion
- null-heavy key columns
- unsupported dialect pattern
- answer unsupported by query trace

The repair loop should classify the error before retrying:

- routing error
- schema misunderstanding
- join-key mismatch
- text extraction failure
- domain definition miss
- aggregation/logic bug

## 6. Output Contract

The agent should never return only prose.

Return:

- final answer
- confidence
- assumptions used
- databases touched
- executed query trace
- validation summary
- notes on repairs performed

This makes debugging and benchmark analysis much easier.

## 7. Evaluation Harness

Build the harness as a first-class product.

Per run, record:

- dataset
- query id
- trial id
- retrieved context
- plan
- tool calls
- raw queries
- intermediate outputs
- validator outcomes
- final answer
- pass/fail
- failure class

Metrics to track:

- overall pass@1
- per-dataset pass@1
- per-failure-class pass rate
- average retries per successful query
- percentage of failures caught by validation before final answer
- improvement after corrections-memory updates

## 8. Benchmark Strategy

Use a four-stage benchmark plan.

### Stage 1: Skeleton Baseline

Goal:

- run on at least 2 DB types
- produce traceable outputs
- establish the first score quickly

### Stage 2: Failure Taxonomy

Run a subset of DAB and label every miss by cause:

- wrong database
- wrong join
- wrong extraction
- wrong definition
- wrong synthesis

### Stage 3: Targeted Fixes

Prioritize fixes in this order:

1. join-key normalization
2. database routing
3. domain KB coverage
4. text extraction recipes
5. retry policy tuning

### Stage 4: Full Submission Runs

Run full benchmark only after:

- regression suite is stable
- answer contract is stable
- corrections memory has stopped changing daily

## 9. Team Execution Model

### Drivers

- implement the runtime, tools, and harness
- keep the system deployable at all times
- own benchmark runs

### Intelligence Officers

- build KB layers
- maintain corrections memory
- run adversarial probes
- turn every repeated failure into reusable context

### Signal Corps

- document real technical findings
- publish failure-driven lessons, not marketing
- bring back external ideas that change the build

## 10. Highest-Leverage Utilities

Build these first:

1. `schema_manifest_builder`
2. `join_key_profiler`
3. `text_field_inventory_builder`
4. `trace_logger`
5. `answer_contract_validator`
6. `corrections_memory_store`

## 11. Two-Week Build Sequence

### Days 1-2

- load DAB environments
- define tool interfaces
- build `QueryEngine` skeleton
- create KB v1 architecture docs
- create harness skeleton

### Days 3-4

- support PostgreSQL + SQLite first
- implement schema retrieval and basic planner
- generate first baseline score
- start corrections log

### Days 5-6

- add MongoDB + DuckDB
- implement join-key resolver
- implement Python merge path
- add output contract validation

### Days 7-8

- implement unstructured extraction pipeline
- deepen domain KB
- add repair policies and failure classification
- run adversarial probes

### Days 9-10

- optimize context retrieval and retry loop
- run larger benchmark sweeps
- lock regression suite
- prepare submission artifacts

## 12. What Will Actually Move the Score

Most likely score drivers:

1. explicit join-key normalization
2. strong domain KB retrieval
3. validation before answer synthesis
4. limited tool ambiguity
5. durable corrections memory
6. Python-based merge/cleanup for cross-DB results

Least likely score drivers:

- adding more generic tools
- making prompts longer
- forcing rigid chain-of-thought templates
- relying on the model to infer provenance or normalization by itself

## 13. Immediate Next Actions

1. Scaffold repository structure: `agent/`, `kb/`, `eval/`, `utils/`, `probes/`, `results/`, `planning/`, `signal/`.
2. Implement the `QueryEngine` and the trace schema first.
3. Build schema manifests for one DAB dataset end-to-end.
4. Implement only four execution tools at first: PostgreSQL, SQLite, Python, KB retrieval.
5. Get a baseline score quickly.
6. Add join-key intelligence before adding more prompt complexity.
7. Only then expand to MongoDB and DuckDB.
8. Turn every benchmark miss into either a KB addition, a validator rule, or a tool/runtime fix.

## Working Thesis

The agent that wins will not be the one with the most clever prompt.

It will be the one with:

- the cleanest query engine
- the narrowest tool surface
- the strongest context retrieval
- the best failure classification
- the fastest correction-to-memory loop
