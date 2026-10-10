# S8 candidate-mechanism study plan (documentation only)

Date: 2026-10-10. Status: draft; **do not execute before S7 is complete and
formally analyzed**. This plan changes no S7 asset and authorizes no request.

## Motivation and evidence boundary

The pre-S7 interventions were not derived from a fixed strong-success versus
weak-failure paired diagnosis. P3 therefore applied a seeded selection rule to
S4 `dev_diagnose` only. Across the three eligible paired tasks, strong
successful trajectories recurrently read before editing (3/3), validated
after editing (3/3), avoided repeated full-file rewrites (3/3), and reread
after editing (2/3). These are post-hoc candidate behaviors, not established
causes. No `dev_validate` or test trajectory is used to design the conditions.

## Conditions

All conditions retain the same task text, tools, sampling request, max steps,
timeouts, and runner. A fresh, same-batch frozen-v0 C1 reference is required;
historical baselines are not substituted. The three candidate conditions are:

1. **Externalized process:** concise explicit requirements to read the target
   before editing, avoid unnecessary whole-file rewrites, validate after the
   final edit, and reread the final file.
2. **Trajectory imitation:** a content-free abstract demonstration of the
   sequence `read → targeted edit → test → reread → finish`, without task
   answers or verifier details.
3. **Length-matched generic control:** the same token budget and formatting,
   but generic planning/completion prose with no candidate behavior.

The resulting design has four arms: C1 plus these three. Prompt text, token
counts, serialization, hashes, and a new S8 activation parser must be frozen
before the first run. No condition may be revised after seeing outcomes.

## Task and model scope

Use only the six locked `dev_validate` tasks. qwen3.5:9b is the target model.
Gemma4:26b is eligible only on tasks whose frozen v0 calibration verifier-pass
rate lies in 20%--80%. Current S4 rates are 100% on five dev-validate tasks and
0% on A04, so **no Gemma task currently qualifies and no Gemma run is planned**.
This prevents adding ceiling/floor observations merely to enlarge n.

A04 remains frozen and is reported both included and excluded because its task
text and verifier conflict. `test_in_b09_phone` is not a dev-validate task and
therefore cannot enter S8; the “exclude b09” view is identical to the all-task
S8 view. It remains a required reporting column only for any later formal or
new-holdout analysis where that task is actually present.

## Repetitions, schedule, and run count

Use eight repetitions per task-condition, with temperature requested at 0.5
and deterministic request seeds when accepted. Generate one fixed, interleaved
schedule across task, arm, and repetition; concurrency one; request-level
transport retry policy unchanged. Core qwen count is:

`6 tasks × 4 arms × 8 repetitions = 192 runs`.

At roughly 5--20 minutes per serial run, the operational envelope is about
16--64 hours. This is an estimate for scheduling, not a promised duration.
Provider-error replacements, if any, use fresh IDs and the predeclared policy;
original failures remain immutable.

## Approximate power perspective

The table gives a normal-approximation minimum detectable absolute difference
for two independent proportions around 0.5, two-sided alpha 0.05 and 80% power:
`(1.96 + 0.84) × sqrt(2 × 0.25 / n)`. It is a conservative orientation, not
the paired-task analysis itself. Repetitions do not increase the task-level n.

| Tasks per arm (n) | Approximate detectable absolute difference |
|---:|---:|
| 6 | 0.81 |
| 12 | 0.57 |
| 18 | 0.47 |
| 24 | 0.40 |
| 36 | 0.33 |

With only six dev-validate tasks, S8 is a mechanism/selection study with weak
power for an efficacy claim. Eight repetitions improve task-rate estimation,
not the number of independent task units.

## Activation measurement

The primary mechanism measure is explicit-reference activation: a run must
explicitly mention at least one frozen candidate action (read-before-edit,
targeted/no-full-rewrite edit, validate-after-edit, or reread-after-edit) in a
stored assistant response before executing the corresponding action. The S8
parser and exact phrase families are frozen and unit-tested before execution.
Behavior-only inference is reported separately and never counted as explicit
activation.

## Outcomes and analysis

Primary outcome: task-level verifier-pass difference between each behavioral
condition and the length-matched generic control, using
`verifier.json.passed`, repetitions aggregated within task, and paired
10,000-draw bootstrap with a frozen seed. Provider-error protocol exclusions
and provider-as-failure sensitivity follow verifier-pass v2.

Secondary outcomes are explicit activation rate, validation after final edit
(primary intent rule and transport-success sensitivity), partial-score delta
from no-op seed, reread-after-edit, whole-file rewrite count, repeated-action
loop count, first edit position, steps, final-empty, timeout, max-steps, and
tool-error rate. C1 comparisons are descriptive context; multiplicity is
shown rather than hidden.

All results are shown with and without A04. A b09-excluded column is retained
and marked “not applicable; task absent.” Individual proportions receive
Wilson intervals; condition differences use task pairing. Means are accompanied
by medians, quartiles, and per-task directions.

## Decision rule

No condition is described as effective unless all of the following hold:

1. explicit mechanism activation is observed in at least 50% of runs and in
   at least four of six tasks;
2. the task-paired mean verifier-pass difference versus the length-matched
   control is positive and its predeclared bootstrap interval excludes zero;
3. the direction remains positive without A04; and
4. provider errors, hard timeouts, or file corruption do not account for the
   apparent difference.

If mechanism activation is absent, the result is “mechanism not activated,”
not “skill ineffective.” If activation occurs without outcome improvement,
report an activated mechanism with no observed improvement. Given n=6, any
positive finding remains dev-only and requires a new holdout before a transfer
claim.

## Optional new holdout

A stronger follow-up would author 6--8 entirely new tasks after freezing the
S8 conditions, then run admission without using trajectories to revise the
prompts. Estimated work is 1--2 hours per task plus 4--8 hours for protocol,
fixture, verifier, shortcut, and review integration: roughly 10--24 hours.
At eight repetitions and four arms, six tasks require 192 qwen runs and eight
tasks require 256. Serial runtime is roughly 16--85 hours at the same broad
5--20-minute envelope.

## Relationship to S7 and deferred work

S8 starts only after S7 reaches 870/870, verifier-pass v2 passes its hash gate,
formal S7 results are committed once, and the owner explicitly approves S8.
S8 cannot change, rerun, filter, or reinterpret S7 conditions. Any LLM-judge
case labeling needed for S8 is deferred until S7 finishes so it cannot alter
provider load during the formal batch.
