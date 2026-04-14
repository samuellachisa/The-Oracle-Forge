# kb/domain — CHANGELOG

Tracks every change to domain knowledge documents (DAB schemas, join keys, unstructured fields, domain terms). Each entry records date, document, change type, reason, and harness score delta (if any).

## Format

```
## [YYYY-MM-DD] <document>.md — <change type>
- What changed:
- Why:
- Injection test result: pass | fail | revised
- Score delta (if measurable):
```

---

## [2026-04-13] Initial scaffold (stubs only)
- What changed: created four stub documents under `kb/domain/` for Drivers to populate as they work through DAB datasets.
- Why: give Drivers a place to push findings during mob sessions (capture in-session, not after).
- Documents stubbed:
  - `dab_schemas.md`
  - `join_keys_glossary.md`
  - `unstructured_fields.md`
  - `domain_terms.md`
- Injection tests: not yet applicable — stubs are empty awaiting per-dataset content.

## [2026-04-13] Full population from DAB db_description files (all 12 datasets)
- What changed: populated all four domain documents comprehensively from `DataAgentBench-main/query_*/db_description.txt` and `db_description_withhint.txt` for every dataset (agnews, bookreview, crmarenapro, deps_dev_v1, github_repos, googlelocal, music_brainz_20k, pancancer_atlas, patents, stockindex, stockmarket, yelp).
- Why: a Driver asked for complete column-level coverage so queries across any of the 54 DAB tasks have ground-truth schema + join + extraction + terminology references to consult before planning.
- Documents updated:
  - `dab_schemas.md` — every table, every column (with type) for all 12 datasets, including crmarenapro's 27 tables across 6 DBs and stockmarket's 2,753 per-ticker DuckDB tables; each dataset section lists cross-DB joins and domain-hint summary.
  - `join_keys_glossary.md` — every cross-DB and notable within-DB join key, tagged by difficulty (clean / aliased / prefixed / embedded / composite / knowledge-match / table-name-as-key / corrupted); includes full crmarenapro join web (Account/Contact/User/Opportunity/Contract/Lead/Product/Pricebook/Order/Case/Issue/Territory) and Salesforce `WhatId` polymorphic prefix resolver.
  - `unstructured_fields.md` — every free-text, stringified-list/dict, JSON-like, HTML, NL-date, NL-metric, and coded-string field across all datasets; extraction-strategy decision table updated.
  - `domain_terms.md` — every coded-value decode table (stockmarket Financial Status / Listing Exchange / Market Category; Salesforce ID prefixes; CPC/IPC/USPC distinctions; TCGA cancer acronyms & Variant_Classification values; music_brainz fixed country/store set; yelp is_open / elite semantics; etc.) plus global business-term conventions.
- Sources: all 12 `db_description.txt` + `db_description_withhint.txt` files and DAB `README.md`.
- Injection test result: each document carries its own injection-test block at the bottom; self-check was structural (hint coverage) not runtime.
- Score delta: not measurable without a query run.
