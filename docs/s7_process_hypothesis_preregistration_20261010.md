# S7 process-metric hypothesis and independent-check plan

Date: 2026-10-10. This document is committed before generating any new
monitoring snapshot or analysis for models other than qwen3.5:9b. It changes
no S7 condition, parser, prompt, schedule, seed, tool, concurrency setting,
or formal-analysis plan.

## Hypothesis

For qwen3.5:9b, relative to C0, C1 will show: (1) lower validation after the
last edit, (2) more `write_file` rewrites, and (3) more repeated-action loops.
Relative to C1, v1 will show the reverse directional pattern: higher
validation-after-last-edit and fewer rewrites and loops.

The completed qwen3.5:9b S7 trajectory snapshot is the source that generated
this hypothesis. It is therefore not an independent test of it. The remaining
five models (`gemma4:26b`, `qwen3.8:27b`, `qwen3-coder-next`, `llama3.1:8b`,
and the uncontrolled GPT-5.6 Sol reference anchor) are independent checks
after their own locked schedules complete. No new other-model monitoring
snapshot is generated before this document's commit.

## Analysis boundaries

All forthcoming work is monitoring and audit only until all 870 scheduled
cells finish. The locked `skill-activation-heuristic-v1` remains unchanged.
Explicit skill reference is the only activation stratum used in any
activation-stratified descriptive view; behavior-only activation remains a
process metric. Legacy `empty_termination` is retained without reinterpretation.
No interim value can alter any locked S7 condition or support an effect claim.
