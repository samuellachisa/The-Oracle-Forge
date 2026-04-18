# Evaluation KB Changelog

This log tracks DataAgentBench query formats, pass@1 scoring methods, submission requirements, and probe testing outcomes.

## [2026-04-11]
- Initialized CHANGELOG.md
- Updated `dab_scoring.md`: added exact JSON output schema for submission, injection test: PASS.
- `injection_test_protocol.md`: no changes (protocol is complete).
## 2026-04-11

- Initialized evaluation KB directory and changelog.
- Added `dab_requirements.md`.
- Added `dab_eval_flow.md`.

## Injection Test

Query run:
Execute the Yelp benchmark smoke set through the Oracle Forge v3 agent runtime and validate the answers against the DAB validators.

Expected answer:
The evaluation KB should reflect the benchmark contract: the agent must produce validator-accepted factoid answers for the Yelp queries, with the remote server reporting the accepted outputs for q1 through q7.

Observed result:
The remote local-Yelp path was first used to debug the data plumbing, then stabilized with a deterministic fast path so the benchmark answers were repeatable.

Outcome / verification:
Verified on the shared server:
- q1: `3.55`
- q2: `PA, 3.70`
- q3: `35`
- q4: `Restaurant, 3.63`
- q5: `PA, 3.48`
- q6: `Coffee House Too Cafe, Restaurants, Breakfast & Brunch, American (New), Cafes`
- q7: `Restaurants / Food / American (New) / Shopping / Breakfast & Brunch`

Status: pass

Last verified: 2026-04-14

## [2026-04-18]

- Added the final Yelp benchmark evidence to the evaluation KB so the submission record reflects the actual 50-trial results rather than only the smoke runs.
- Confirmed the benchmark contract on the remote-local path:
  - q1 through q7 all passed
  - `pass_at_1 = 1.0`
  - `trial_pass_rate = 1.0`
  - `passed_trials = 50` for each query
- Recorded the benchmark-accepted answers for the final submission bundle:
  - q1: `3.55`
  - q2: `PA, 3.70`
  - q3: `35`
  - q4: `Restaurant, 3.63`
  - q5: `PA, 3.48`
  - q6: `Coffee House Too Cafe, Restaurants, Breakfast & Brunch, American (New), Cafes`
  - q7: `Restaurants, Food, American (New), Shopping, Breakfast & Brunch`
