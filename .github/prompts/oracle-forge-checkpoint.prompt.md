---
description: "Run an Oracle Forge checkpoint review for current sprint state, with evidence gaps, risk flags, and next actions across agent, KB, eval, probes, planning, signal, and results."
mode: "agent"
---
Run a checkpoint review for The Oracle Forge challenge.

Inputs:
- Sprint day/date: ${input:sprint_day:Example: Week 8 Day 3}
- Current focus: ${input:focus:Example: Multi-DB routing and KB v2}
- Deadline: ${input:deadline:Example: 2026-04-15 21:00 UTC}

Tasks:
1. Inspect repository status against required directories: agent, kb, eval, probes, planning, utils, signal, results.
2. Identify what is complete, incomplete, or missing.
3. For each incomplete area, list the minimum next artifact needed and why it unblocks progress.
4. Validate evidence quality: traces, score logs, regression outputs, correction entries, and approval records.
5. Map current risks to DAB failure categories (multi-db, key mismatch, unstructured transformation, domain knowledge).
6. Produce a prioritized next-24-hours plan.

Output format:
1. Checkpoint summary
2. Deliverable status table (complete/in progress/missing)
3. Evidence gaps
4. Top 5 risks with mitigations
5. Next 24h execution plan with acceptance checks
