# S7 process and L3b analysis revision

Date: 2026-10-10. This analysis-only revision is committed before generating
any cross-model process snapshot. It changes no locked task, verifier, fixture,
prompt, skill, parser, runner, condition, schedule, seed, concurrency setting,
or model call.

## Process validation definition

The primary validation-after-edit measure is the **validation-intent rule**:
after the final `write_file` call, a run has a `run_command` whose serialized
command includes one or more of `test`, `pytest`, `unittest`, or `py_compile`.
It is chosen because a generic successful shell command can be reading,
formatting, or demonstrating code rather than checking the implementation.

The sensitivity measure is the **transport-execution rule**: after the final
edit, at least one `run_command` has `result.ok == true`, regardless of command
text. It measures successful tool execution, not test success. Both measures
are reported for qwen C0/C1 by condition, task-level direction, and run-level
quantiles; the process conclusion is considered robust only if its descriptive
direction does not depend on choosing one definition.

## L3b interpretation

The S7 L3b trigger is expected to occur infrequently. Its triggered trajectories
will receive counts and their call-32 state distribution only; no hypothesis
test of post-trigger conversion will be performed. Any A-layer final-pass
difference must be decomposed into trajectories that already pass at call 32,
those that do not, and replay-unavailable records. The call-32 partial-score
proxy is audited against the final frozen verifier before being interpreted as
"already passed."

## Cross-model S4 trajectory exploration

The following is a post-hoc, dev-only exploration using only the frozen S4
`dev_diagnose` subset; it does not select a new intervention. Per run it will
measure assistant response count, tool calls per assistant response, and the
indicator that a write occurs before the first successful file-read result.
Models are compared descriptively. The associated S7 analysis statement is
pre-declared now: after all S7 runs complete, report the same metrics by model
and core condition with task as the aggregation unit, without treating the S4
exploration as confirmatory evidence or modifying the locked benchmark.

## Verifier-pass analysis implementation

Formal S7 pass summaries will read `verifier.json.passed` directly. Provider
errors exhausted at request transport are excluded from the primary denominator;
hard timeouts remain denominator failures even when the legacy broad
`provider_error` flag co-occurs. The formal analysis patch will be versioned,
hashed, and unit-tested before formal analysis, while the locked S7 execution
remains untouched.
