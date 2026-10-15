# Batch status

This ledger is refreshed by `harness/update_status.py` after each completed run or judge annotation.

| batch | planned | completed | remaining | state |
|---|---:|---:|---:|---|
| Historical/direct r2 science runs | 246 | 246 | 0 | complete (legacy and B0--B4 evidence) |
| B5 provider-error replacements | 8 | 8 | 0 | protocol committed; sequential concurrency=1 |
| B5 r2 blind LLM judge | 24 | 24 | 0 | newly anonymized packets only |
| L3b dev-validate | 72 | 72 | 0 | complete; analysis pending |
| S7 locked formal benchmark | 1086 | 1086 | 0 | complete; formal analysis complete |
| S8-b fresh-task mechanism study | 192 | live | live | running; see `S8B_STATUS.md` |

Current task: S7 execution and gated formal analysis are complete; S8-b is running under its locked interleaved schedule. Live counts are maintained in `S8B_STATUS.md`.
Estimated remaining: no authorized model calls; formal S7 tables and figures are available.
