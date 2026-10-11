# Skill-trajectory benchmark report

Status: S7 formal analysis complete. All primary pass quantities below read
`verifier.json.passed` through analysis version `s7-formal-v1.0.0`.

## 1. Problem

This project asks whether a written coding skill changes how tool-using models
inspect, edit, validate, and complete small repository-repair tasks, and
whether any behavioral change generalizes across tasks and model capability.
The inferential unit is the task; repetitions estimate within-task sampling
variation.

## 2. Experimental design

The study separates `dev_diagnose`, `dev_validate`, `test_in`, and `test_out`.
Frozen admission checks require positive fixtures to pass and buggy/shortcut
fixtures to fail an external verifier. The formal S7 core compares C0 (no
skill) with C1 (frozen v0 skill) across six models; v1 and L3b are exploratory.
The locked plan contains 870 interleaved runs, all of which have metadata and
a Boolean verifier result. Five qwen retry-exhausted transport failures are
excluded from the primary denominator and treated as failures in sensitivity
analysis.

Primary outcome is the frozen `verifier.json.passed` boolean. Retry-exhausted
transport errors are excluded from the primary numerator and denominator and
included as failures in sensitivity analysis. Hard timeout and max-steps
records remain denominator failures. Repetitions are aggregated within task
before task-paired comparison.

## 3. Selection rationale: skills, tasks, and models

Skills A and B target recurring data-cleaning and transformation behavior;
Skill C provides out-of-domain formal tasks. The synthetic task pool permits
frozen, deterministic verification and exact artifact replay. The model panel
spans a weak target, larger open models, a coding-specialized model, a lower
bound, and GPT-5.6 Sol as a Codex reference anchor. GPT sampling is not aligned
with r2 and is never pooled as a controlled comparison.

S4 verifier-pass calibration placed qwen3.5:9b inside the predeclared 20%--80%
band. Gemma, qwen3.8, and qwen-coder were near the upper end; llama was at the
floor. These calibration observations are descriptive rather than rankings.

## 4. Data collection and analysis

Runner r2 archives raw provider responses, tool events, actions, finish
reasons, usage fields, workspaces, non-exclusive outcome flags, and verifier
results. It requests temperature 0.5, a deterministic seed when supported,
40 tool calls, a conservative 65,536 context budget, 120-second command
timeouts, and a 1,200-second process-group timeout. Actual acceptance is
recorded rather than assumed.

The Codex adaptation revealed that legacy CLI trajectories could hide content
in provider-specific reasoning/tool-call fields. Runner r2 therefore records
raw response fields and parses tool calls explicitly. Codex CLI runs remain a
separate legacy cohort; GPT in S7 remains an uncontrolled reference anchor.

Individual proportions use Wilson or exact intervals. C0/C1 differences use
task-paired bootstrap with fixed seeds. LLM-judge labels come from a blinded
subsample and are bounded by the human-agreement audit. Mechanical process
metrics carry validation and looping conclusions.

## 5. Main results

### Retained dev findings

Verifier-pass correction changed S4 from 102 to 110 passes among 175 usable
runs, original S5 from 8 to 18 among 28, replacement-inclusive S5 from 12 to
24 among 36, and S6 baseline/L3b combined from 25 to 48 among 72. These are
outcome-definition corrections, not performance improvements.

### Formal benchmark

Across all held-out tasks, C0/C1 verifier pass is 43/89 versus 45/89 for
qwen3.5:9b, 33/54 versus 36/54 for gemma4:26b, 45/54 versus 46/54 for
qwen3.8:27b, 33/54 versus 34/54 for qwen3-coder-next, and 0/54 versus 0/54
for llama3.1:8b. Task-paired C1-minus-C0 differences are respectively +1.9,
+5.6, +1.9, +1.9, and 0.0 percentage points. The 10,000-draw paired
bootstrap intervals are [-6.9, 10.6], [0.0, 14.8], [-3.7, 7.4], [-7.4,
13.0], and [0.0, 0.0] points. These patterns do not show a consistent C1
advantage across the controlled model panel.

GPT-5.6 Sol, the sampling-uncontrolled Codex anchor, is 44/54 in both C0 and
C1; it is not pooled with r2 models. The active GPT cohort follows an
owner-authorized post-completion overwrite of 104 usage-limit failures, a
deviation documented separately. One controlled core task,
`test_in_b11_bucket`, is an all-zero floor; there are no all-one ceiling
tasks. Full split and b09 sensitivity views are in
`docs/s7_formal_results_20261011.md` and `results/tables/s7/`.

## 6. Case studies

The fixed-seed, post-hoc case study reads only S4 `dev_diagnose`. Three tasks
were eligible for strong-pass/weak-fail pairing: A03, A05, and B03. A01, B01,
and B05 had no qwen failure candidate. No same-task weak-success/strong-failure
counterexample existed; this absence was retained. Recurrent strong-trajectory
behaviors were reading before editing, validating after editing, avoiding
repeated full rewrites, and rereading after editing. Full step tables are in
`docs/case_studies.md`.

## 7. Patterns and anomalies

The llama S4 pattern was usually one batched tool-call response followed by a
stop; 16/40 `run_command` calls requested an invalid 300-second timeout. This
is a mixed tool-argument and capability-floor observation, not an interface
serialization failure.

L3b has several legitimate readings. Legacy single-label outcomes suggested a
smaller number of passes; verifier-pass reconstruction gives baseline 22/36
and L3b 26/36. In the call-32-selected A layer it is 2/9 versus 6/12, while the
B layer is 20/27 versus 20/24. Among runs not passing at call 32, final pass is
0/7 versus 1/6. These small post-randomization strata differ in composition;
no effect claim follows. Validation is 11/12 under any successful command and
9/12 under the stricter test-intent definition.

The call-32 partial=1 proxy agreed with final verifier pass in all seven
available dev cases (0/7 proxy-positive final failures), but write-only replay
cannot reproduce command side effects.

In S7, the qwen-generated validation hypothesis replicates for qwen (task-level
C1-minus-C0 validation after final edit: -25.0 points) but not across the
independent r2 models: gemma is +11.1, qwen3.8 is 0.0, qwen-coder is -1.9,
and llama is +38.9 points. Explicit C1 skill-reference rates also do not rise
monotonically with model capability under the locked parser.

## 8. Skill modifications

v1 externalizes requirement inventory, rereading, and validation behaviors
identified in dev diagnosis. L3b is a content-independent fixed reminder after
call 32. Both are exploratory; neither changes the S7 core. S8 candidates are
derived only from recurrent dev-diagnose case behaviors and are documented
separately. No v2 skill is introduced here.

## 9. Was the intervention effective?

The controlled S7 core does not show a consistent verifier-pass improvement
from C1 across models or splits. v1 produces observable mechanism changes:
explicit reference occurs in 48/60 runs and task-level validation rises by
45.0 points relative to C1. Its paired verifier-pass difference is 0.0 points
with a [-11.7, 13.3] bootstrap interval, so it does not meet the preregistered
threshold requiring mechanism activation plus observable outcome improvement.
L3b triggers in only 11/87 usable runs; its call-32 strata are post-assignment
and remain descriptive. These findings do not establish that written skills
cannot help outside this task pool.

## 10. Limitations

- Synthetic tasks and self-authored skills limit external validity.
- Calibration contains model/task floors and ceilings; uninformative tasks
  reduce power.
- Task counts are small; repetitions do not create additional task units.
- The LLM judge may be biased. There is one human annotator, the researcher;
  the 24-packet comparison is human-vs-judge, incompletely blinded, and small.
- GPT runs through Codex are a sampling-uncontrolled reference anchor.
- The active GPT cohort overwrote 104 initial usage-limit failures after S7
  completion at the owner's direction, violating the original run-once rule;
  it is descriptive only.
- r2 and Codex expose different tool surfaces and cannot be assumed equivalent.
- v1 and L3b lack a length-matched generic-prompt control (C3).
- Post-hoc analyses include qwen-generated process hypotheses, S4 cross-model
  turn/call/blind-write metrics, dev-diagnose case selection, mechanical
  convergent-label checks, and sensitivity exploration.

## 11. Future directions

S8 may compare an
externalized process, a trajectory-imitation prompt, and a length-matched
generic prompt on `dev_validate`; it must not retroactively modify S7. A new
6--8-task untouched holdout would improve separation between diagnosis and
evaluation.

## Errata and methodological lessons

The legacy mutually exclusive label classified verifier-passing runs with
empty final messages as `empty_termination`, understating pass rates. The
broad provider-error flag also captured process kills; only retry-exhausted
transport errors belong to `provider_error_protocol`. Old tables are retained
as legacy audit artifacts and replaced, not overwritten.

Several earlier mean-only process summaries were pulled upward by extreme
long trajectories; medians, quartiles, and task-paired directions are now
required. Finally, stratifying on reaching call 32 is conditioning on a
post-treatment variable. A-layer differences may reflect trajectory
composition rather than the reminder.

Known task issues are reported rather than repaired: A04 contains a frozen
task/verifier conflict and receives included/excluded dev views. b09_phone has
two clustered hard timeouts but no demonstrated slow task/verifier behavior;
formal analyses will show included/excluded sensitivity views.

## Human--judge agreement and permitted use

Across 24 confirmed human annotations, macro kappa over five estimable labels
is 0.588 (bootstrap 95% 0.434--0.771), while macro PABAK over all eight labels
is 0.677 (0.552--0.781). Exact eight-label-set agreement is 25.0%. Judge labels
support conclusions only for file corruption, tool misuse, and missed
constraint. Other judge modes remain exploratory; validation and loop claims
use mechanical definitions.
