# Batch status

This ledger is refreshed by `harness/update_status.py` after each completed run or judge annotation.

| batch | planned | completed | remaining | state |
|---|---:|---:|---:|---|
| Historical/direct r2 science runs | 246 | 246 | 0 | complete (legacy and B0--B4 evidence) |
| B5 provider-error replacements | 8 | 0 | 8 | protocol committed; sequential concurrency=1 |
| B5 r2 blind LLM judge | 24 | 0 | 24 | newly anonymized packets only |
| L3b dev-validate (not authorized to run) | 72 | 0 | 72 | preregistered; awaiting user confirmation |

Current task: B5 protocol artifacts, provider replacements, and blind judge; no test split is runnable by these scripts.
Estimated remaining after this commit: 8 sequential replacement runs and 24 judge calls; L3b remains excluded until explicit authorization.
