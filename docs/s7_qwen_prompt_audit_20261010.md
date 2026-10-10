# S7 qwen3.5:9b C0/C1 prompt audit

Date: 2026-10-10. This is a pre-analysis implementation audit, not an outcome
comparison. The deterministic sampling seed is `7102026`. It selected five
completed qwen3.5:9b C0 runs and five completed C1 runs from the 90 completed
runs in each condition.

## Result

All 10 audited runs passed every check. No protocol anomaly was found, so S7
was not paused.

| condition | audited run IDs |
|---|---|
| C0 | `a12_enum-r4`, `a11_duration-r2`, `b08_total-r1`, `c04_policy-r5`, `a09_header-r4` |
| C1 | `c05_metrics-r2`, `a11_duration-r3`, `b07_tags-r5`, `a07_slug-r2`, `c04_policy-r3` |

For every sampled run, the stored prompt hash agreed with run metadata and the
locked serialized-template manifest; the stored prompt exactly matched the
condition/task template; the common final instruction suffix matched; and the
workspace `task.md` hash matched its frozen task-template source.

All C0 prompts had no delimited protocol block and contained no v0 skill text.
All C1 prompts contained the applicable delimited v0 protocol block. The
recorded tool schema version was 2 in every run, and the live `r2_agent.py`
tool-definition source hash matched the execution-lock hash. Thus task text,
tool definition source, and common prompt suffix were held constant under this
audit, with the skill-protocol block as the intended C0/C1 difference.

Machine-readable audit details are
`data/s7_monitoring/qwen_c0_c1_prompt_audit.json`.
