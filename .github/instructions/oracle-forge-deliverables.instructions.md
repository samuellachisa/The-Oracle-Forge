---
description: "Use when planning, implementing, or reviewing The Oracle Forge team challenge deliverables, including agent, KB, eval harness, probes, planning logs, signal outputs, and benchmark results packaging."
---
Apply these rules for Oracle Forge work in this repository.

## Deliverable Contract
- Keep artifacts mapped to these directories: agent, kb, eval, probes, planning, utils, signal, results.
- Do not mark a deliverable complete without file-level evidence in the expected directory.
- Prefer incremental commits that preserve traceability from baseline to final benchmark run.

## Evidence Rules
- Any claimed capability must include at least one of: trace, test output, score log delta, or reproducible command sequence.
- For benchmark-impacting changes, document before/after behavior and expected score movement.
- For failure fixes, add a correction entry using the format:
  [query that failed] -> [what was wrong] -> [correct approach] -> [post-fix result]

## DAB Failure Mode Coverage
For planning, probes, and retrospectives, classify work under one or more categories:
- multi-database integration
- ill-formatted join keys
- unstructured text transformation
- domain knowledge gaps

## AI-DLC Governance
- Enforce phase order: Inception -> Construction -> Operations.
- Record explicit mob-session gate approval before crossing phases.
- Definition of done items must be numbered and objectively verifiable.

## Output Quality
- Favor concise, reproducible outputs over narrative summaries.
- Surface risks and blockers with mitigation proposals.
- Keep changelogs current for KB and evaluation artifacts when behavior changes.
