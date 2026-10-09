# Batch status

This ledger is refreshed by `harness/update_status.py` after each completed run or judge annotation.

| batch | planned | completed | remaining | state |
|---|---:|---:|---:|---|
| Historical/direct r2 science runs | 246 | 246 | 0 | complete (legacy and B0--B4 evidence) |
| B5 provider-error replacements | 8 | 8 | 0 | protocol committed; sequential concurrency=1 |
| B5 r2 blind LLM judge | 24 | 24 | 0 | newly anonymized packets only |
| L3b dev-validate | 72 | 72 | 0 | complete; descriptive analysis committed |
| S7 documentation-only preflight | 1 | 1 | 0 | revised 870-run protocol and lock template committed; awaiting lock authorization |

Current task: S7 remains planning-only; no test split is authorized.
Estimated remaining: implement/review the formal runner and analysis artifacts, then create the immutable S7 lock only after user authorization.
