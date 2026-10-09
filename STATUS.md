# Batch status

This ledger is refreshed by `harness/update_status.py` after each completed run or judge annotation.

| batch | planned | completed | remaining | state |
|---|---:|---:|---:|---|
| Historical/direct r2 science runs | 246 | 246 | 0 | complete (legacy and B0--B4 evidence) |
| B5 provider-error replacements | 8 | 8 | 0 | protocol committed; sequential concurrency=1 |
| B5 r2 blind LLM judge | 24 | 24 | 0 | newly anonymized packets only |
| L3b dev-validate (not authorized to run) | 72 | 0 | 72 | preregistered; awaiting user confirmation |

Current task: B5 is complete; awaiting explicit user authorization before the preregistered L3b batch. No test split is runnable by these scripts.
Estimated remaining: 72 L3b runs only if explicitly authorized; otherwise the next stage is S7 planning, not execution.
