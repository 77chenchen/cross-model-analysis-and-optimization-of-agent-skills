# S8 execution start

Date: 2026-10-11. The owner authorized the dev-only S8 candidate-mechanism
study after S7 completion and formal analysis. This record operationalizes,
but does not rewrite, the earlier S8 plan.

The frozen schedule contains 192 sequential qwen3.5:9b runs: six
`dev_validate` pilot tasks, four arms, and eight repetitions per cell. The
arms are a fresh v0 C1 reference, externalized candidate behaviors, an abstract
trajectory-imitation instruction, and a word-count-matched generic control.
All non-C1 candidate guidance blocks contain 51 whitespace-delimited words;
this is an audit count rather than a provider-tokenizer claim.

The S8 wrapper can address only the six pilot tasks in the frozen schedule. It
uses the unchanged r2 direct chat-completions loop, 0.5 requested temperature,
deterministic request seeds, 40 tool calls, a 65,536-token context budget, and
20-minute process and verifier limits. It records raw local responses and
never sends S8 artifacts into the S7 result tree.

The execution lock is [config/s8_execution_lock.yaml](../config/s8_execution_lock.yaml).
S8 is dev-only; its results cannot revise S7 or support a held-out transfer
claim without a separately designed new holdout.
