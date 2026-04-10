---
description: "Author or review Oracle Forge adversarial probes for DataAgentBench with standardized structure, failure categorization, fix workflow, and post-fix evidence."
mode: "agent"
---
Create or audit adversarial probes for The Oracle Forge challenge.

Inputs:
- Goal: ${input:goal:Create new probes | Audit existing probes | Expand category coverage}
- Current probe count: ${input:probe_count:Example: 9}
- Target count: ${input:target_count:Example: 15}
- Priority categories: ${input:categories:multi-database integration, ill-formatted join keys, unstructured text transformation, domain knowledge gaps}
- Deadline: ${input:deadline:Example: 2026-04-18 21:00 UTC}

Tasks:
1. Assess current category coverage and identify gaps.
2. Propose or refine probes to close gaps with realistic business-style query wording.
3. Ensure every probe follows this schema:
- query
- failure_category
- expected_failure
- observed_failure
- fix_applied
- post_fix_score_or_result
4. Enforce minimum category breadth (at least 3 of 4 categories covered).
5. Prioritize probes with highest expected score impact and highest risk reduction.
6. Produce copy-ready content for probes/probes.md.

Output format:
1. Coverage snapshot
2. New/updated probes (standard schema)
3. High-impact probes first (top 5)
4. Validation checklist before merge
5. Next actions for Drivers and Intelligence Officers
