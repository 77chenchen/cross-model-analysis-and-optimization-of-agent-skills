# Batch status

This ledger is refreshed by `harness/update_status.py` after each completed run or judge annotation.

| batch | planned | completed | remaining | state |
|---|---:|---:|---:|---|
| Historical/direct r2 science runs | 246 | 246 | 0 | complete (legacy and B0--B4 evidence) |
| B5 provider-error replacements | 8 | 8 | 0 | protocol committed; sequential concurrency=1 |
| B5 r2 blind LLM judge | 24 | 24 | 0 | newly anonymized packets only |
| L3b dev-validate | 72 | 72 | 0 | complete; analysis pending |
| S7 locked formal benchmark | 870 | 870 | 0 | complete; formal analysis complete |

Current task: S7 execution and gated formal analysis are complete; await the owner's S8 decision.
Estimated remaining: no authorized model calls; formal S7 tables and figures are available.
