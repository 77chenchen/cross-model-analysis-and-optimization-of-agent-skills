# Environment lock (D1 draft)

This records the runner environment, not credentials. Update and commit this
file immediately before the formal pilot freeze.

| Field | Value |
|---|---|
| recorded at | 2026-10-06 (Asia/Singapore) |
| repository commit at capture | `32d3683d2afdcbf2a302152150357293267e9b50` |
| Codex CLI | `0.160.1` |
| Python | `3.14.0` |
| context limit | `65536` |
| max steps | `40` |
| timeout | `20 minutes` |
| temperature | `0` |
| tool schema | `1` |

The SoC LaaS profile obtains its credential only from the local login shell.
No API key, endpoint secret, or credential-bearing configuration belongs in
this repository. Exact requested and returned model IDs are recorded per run.
