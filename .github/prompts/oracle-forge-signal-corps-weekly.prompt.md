---
description: "Generate technically accurate weekly Signal Corps outputs for Oracle Forge, including daily Slack summaries, X thread drafts, community log updates, and article planning tied to engineering evidence."
mode: "agent"
---
Generate weekly Signal Corps deliverables for The Oracle Forge sprint.

Inputs:
- Week focus: ${input:week_focus:Example: Week 9 benchmark and probes}
- Major technical updates: ${input:updates:Example: Added key normalization and improved pass@1 from 33 to 39}
- Evidence links/refs: ${input:evidence:Example: score log, traces, PR links, probe fixes}
- Audience priority: ${input:audience:Benchmark community | Internal cohort | Both}

Tasks:
1. Produce 5 daily internal Slack updates (max 4 bullets each):
- shipped
- stuck
- next
- ask/help needed
2. Draft 2 technically specific X threads for the week.
3. Draft 2 substantive community comments (Reddit/Discord style) grounded in actual findings.
4. Propose one 600+ word article outline:
- one concrete failure
- one fix that worked
- one architecture decision and trade-off
5. Ensure every external draft is evidence-linked and non-promotional.
6. Capture any community intelligence to feed back into kb/corrections or eval plans.

Output format:
1. Weekly messaging strategy
2. Daily Slack posts (Day 1-5)
3. X thread draft A
4. X thread draft B
5. Community comments
6. Article outline
7. Feedback-to-engineering loop items
