# Batch status

This ledger is refreshed by `harness/update_status.py` after each completed run or judge annotation.

| batch | planned | completed | remaining | state |
|---|---:|---:|---:|---|
| Historical/direct r2 science runs | 246 | 246 | 0 | complete (legacy and B0--B4 evidence) |
| B5 provider-error replacements | 8 | 8 | 0 | protocol committed; sequential concurrency=1 |
| B5 r2 blind LLM judge | 24 | 24 | 0 | newly anonymized packets only |
| L3b dev-validate | 72 | 72 | 0 | complete; descriptive analysis committed |
| S7 execution-lock construction | 1 | 1 | 0 | formal runner, prompt manifest, schedules, and analysis entry points prepared; no test run |

Current task: immutable S7 lock is ready to commit and tag; no test run has occurred.
Estimated remaining: execute only the locked schedules after the tag is created.
