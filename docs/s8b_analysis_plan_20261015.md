# S8-b locked analysis plan

Date: 2026-10-15 (Asia/Singapore). This plan was written before the first
S8-b provider request. S8-b is a fresh-task, development-only mechanism study;
it does not revise or replace the held-out S7 result.

## Design

The locked matrix is 24 newly authored and admitted development tasks × four
conditions × two repetitions = 192 runs of `qwen3.5:9b`. Conditions are a
fresh v0 skill reference (`C1`), an externalized process instruction, an
abstract trajectory-imitation instruction, and a 51-word generic control.
All runs use runner r2, temperature request 0.5, deterministic request seeds,
40 tool calls, a 65,536-token context budget, 20-minute hard timeout, and
worker concurrency one. The schedule is randomly interleaved with fixed seed
20261015 and is resumed idempotently in that order.

## Outcomes and denominator

The primary outcome is `verifier.json.passed`. Retry-exhausted transport
provider errors are excluded from the primary numerator and denominator and
are included as failures in a scheduled-run sensitivity. Timeouts and
max-steps outcomes remain in the primary denominator. The task is the
inferential unit; repetitions estimate within-task instability and are first
aggregated inside task-condition cells.

Each of `C1`, `externalized`, and `imitation` is compared with
`generic_control` by a 10,000-draw paired task bootstrap with seed 20261016
(deterministic offsets for additional contrasts). Wilson intervals describe
single pass proportions only. All three contrasts are reported; multiplicity
is not hidden, and this development study is not presented as held-out
confirmation.

## Mechanism and process measures

The explicit-activation parser searches stored assistant content and reasoning,
never the supplied prompt. Activation requires an assistant response to name a
candidate action before or in the response that executes the matching tool
action: reading/inspection, targeted minimal editing, focused validation, or
post-edit rereading. Behavior-only measures are reported separately:
read-before-edit, validation after the last edit, reread-after-edit, whole-file
rewrite count, repeated-action loop count, tool steps, partial score,
`final_empty`, timeout, and `max_steps_reached`.

## Interpretation rule

No condition is described as effective unless explicit activation is observed
in at least half of usable runs and at least 12 of 24 tasks, its task-paired
pass-rate difference versus the generic control is positive with the locked
bootstrap interval excluding zero, and provider errors, hard timeouts, or file
corruption do not explain the difference. Activation without outcome
improvement is reported as mechanism activation without observed repair gain.
Regardless of the result, S8-b remains development-only and cannot alter the
S7 conditions or held-out conclusions.
