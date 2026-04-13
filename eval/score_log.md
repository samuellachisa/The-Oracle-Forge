# Score Log

Track score progression from first baseline to final submission.

## Template

```md
## YYYY-MM-DD
Run type:
Command:
Dataset scope:
Trials:
Score:
Notes:
```

## 2026-04-11
Run type: Remote DAB smoke validation
Command: `python run_benchmark_query.py --dataset yelp --query-id 1 --validate-answer`
Dataset scope: `yelp` query 1
Trials: 1
Score: pass (`is_valid: true`)
Notes: Final answer `3.55`; validator reason `Found matching number: 3.55 ~= 3.55`; reported benchmark evidence includes `benchmark_reviews=117`.

## 2026-04-12
Run type: Team `gpt-5` targeted smoke rerun (highest-leverage failures)
Command:
- `python3 run_benchmark_query.py --dataset yelp --query-id 2 --validate-answer`
- `python3 run_benchmark_query.py --dataset yelp --query-id 3 --validate-answer`
- `python3 run_benchmark_query.py --dataset yelp --query-id 6 --validate-answer`
Dataset scope: `yelp` queries 2, 3, 6
Trials: 1 per query
Score: `0/3` pass (`is_valid: false` for all three)
Notes:
- q2 (`timestamp: 20260412_000838`): output `PA, 3.68`; validator reason `Number near 'PA' does not match ≈3.699395770392749`.
- q3 (latest rerun): validator reason `Number 35 not found in LLM output.`
- q6 (`timestamp: 20260412_000840`): output includes `Coffee House Too Cafe` but categories resolve to `Unknown`; validator reason `Missing category: restaurants`.
