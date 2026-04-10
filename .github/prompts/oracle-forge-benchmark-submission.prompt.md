---
description: "Prepare Oracle Forge benchmark submission artifacts for DataAgentBench, including results packaging, AGENT summary, PR checklist, and verification steps."
mode: "agent"
---
Prepare a DataAgentBench submission package for The Oracle Forge.

Inputs:
- Team name: ${input:team_name:Example: Team Helios}
- Trials per query: ${input:trials:Example: 50}
- Results file path: ${input:results_path:Example: results/team_helios_results.json}
- Current pass@1 score: ${input:score:Example: 41.2}
- PR target date: ${input:pr_date:Example: 2026-04-18}

Tasks:
1. Validate required artifacts exist and are internally consistent:
- results JSON
- AGENT architecture summary
- score log with baseline and latest comparison
- trace evidence references
2. Build a submission readiness checklist with pass/fail status.
3. Draft PR title and body using required convention:
- Title: "[Team Name] — TRP1 FDE Programme, April 2026"
4. Draft concise architecture and methodology summary for PR body.
5. Flag blocking issues and provide immediate remediation steps.
6. Output final copy blocks ready to paste into GitHub.

Output format:
1. Submission readiness status
2. Missing/blocking items
3. PR title
4. PR body draft
5. Final pre-submit verification commands/checks
