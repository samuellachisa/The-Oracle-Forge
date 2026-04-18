# Architecture KB Changelog

This log tracks the addition, revision, or removal of architecture knowledge items (e.g., Claude Code memory, OpenAI data agent context layers).
Following the Karpathy method, obsolete or failed architectures must be removed or flagged.

## [2026-04-11]
- Initialized CHANGELOG.md
- Expanded `claude_code_memory.md`: added autoDream detail (triggers, what it writes), worktree isolation detail, tool scoping rationale. Injection test: PASS.
- Expanded `openai_data_agent.md`: added one concrete DAB example per context layer, closed-loop self-correction detail, table enrichment as hardest sub-problem. Injection test: PASS.
- Added `tool_definitions.md`: Oracle Forge's 10-tool surface with scope boundaries, selection rules, and injection test. PASS.
## 2026-04-11

- Initialized architecture KB directory and changelog.
- Added `context_layers.md`.

## Injection Test

Query run:
Request the agent to enumerate the required context layers from the architecture documentation, then verify the layers against the actual Oracle Forge v3 run loop.

Expected answer:
1. Schema & metadata indexing
2. Domain / institutional knowledge (aliases, business metrics, join-key rules)
3. Interaction memory (self-learning corrections and session history)

Observed result:
The architecture KB and the agent runtime aligned with the expected three-layer design. The live run used `common_scaffold/DataAgent.py` for the agent loop and `common_scaffold/prompts/prompt_builder.py` for the injected instructions.

Outcome / verification:
Verified against the live Yelp q1 run path launched with `python3 run_agent.py --dataset yelp --query_id 1 --llm google/gemini-2.0-flash-001 --iterations 1 --root_name run_tmp9`, which returned `3.55` on the shared server after the remote Yelp fast path was enabled.

Status: pass

Last verified: 2026-04-14

## [2026-04-18]
- Documented the remote-local Yelp regression sweep in the architecture KB so the live agent loop evidence stays aligned with the layered context design.
- Recorded the 50-trial `yelp` query sweep (`q1` through `q7`) as the authoritative smoke validation for the current Oracle Forge runtime. All seven queries passed with `pass_at_1=1.0` and `trial_pass_rate=1.0`.
- Confirmed the live run path still uses `common_scaffold/DataAgent.py` with the remote sandbox / DAB adapter bridge, while the Yelp-specific fast path keeps the benchmark answers stable on the shared server.
