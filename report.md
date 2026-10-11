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
band at 18/32 usable runs (56.2%). On the same calibration batch, gemma4:26b
was 30/36 (83.3%), qwen3.8:27b was 32/35 (91.4%), qwen3-coder-next was 30/36
(83.3%), and llama3.1:8b was 0/36 (0.0%). These ranges come from the 12 pilot
tasks used in S4, not the 18 held-out S7 tasks, so they are descriptive
calibration observations rather than S7 rankings.

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

<!-- S7_CHECK:CORE_BEGIN -->
| Model | C0 verifier pass | C1 verifier pass | C1-C0 pp, task-paired bootstrap 95% interval |
|---|---:|---:|---:|
| qwen3.5:9b | 43/89 (48.3%) | 45/89 (50.6%) | +1.9 [-6.9, 10.6] |
| gemma4:26b | 33/54 (61.1%) | 36/54 (66.7%) | +5.6 [0.0, 14.8] |
| qwen3.8:27b | 45/54 (83.3%) | 46/54 (85.2%) | +1.9 [-3.7, 7.4] |
| qwen3-coder-next | 33/54 (61.1%) | 34/54 (63.0%) | +1.9 [-7.4, 13.0] |
| llama3.1:8b | 0/54 (0.0%) | 0/54 (0.0%) | 0.0 [0.0, 0.0] |
| gpt-5.6-sol (reference anchor) | 44/54 (81.5%) | 44/54 (81.5%) | 0.0 [-5.6, 5.6] |
<!-- S7_CHECK:CORE_END -->

The controlled rows do not show a consistent C1 advantage. GPT-5.6 Sol is a
sampling-uncontrolled Codex reference anchor and is not pooled with r2 models.

![Formal S7 benchmark overview](figures/s7/S7_F1_main_results.png)

Figure 1 uses the completed S7 formal data, not an interim monitoring export.
Its pass intervals are single-proportion Wilson intervals; condition
comparisons use the task-paired bootstrap reported in the tables.

The split-specific paired estimates show that neither split supplies a common
direction across models:

<!-- S7_CHECK:SPLIT_BEGIN -->
| Model | test_in C1-C0 pp (95% bootstrap interval; 12 tasks) | test_out C1-C0 pp (95% bootstrap interval; 6 tasks) |
|---|---:|---:|
| qwen3.5:9b | +5.0 [-5.0, 13.3] | -4.2 [-23.3, 14.2] |
| gemma4:26b | +8.3 [0.0, 22.2] | 0.0 [0.0, 0.0] |
| qwen3.8:27b | -2.8 [-8.3, 0.0] | +11.1 [0.0, 22.2] |
| qwen3-coder-next | -2.8 [-11.1, 5.6] | +11.1 [0.0, 33.3] |
| llama3.1:8b | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| gpt-5.6-sol (reference anchor) | 0.0 [-8.3, 8.3] | 0.0 [0.0, 0.0] |
<!-- S7_CHECK:SPLIT_END -->

### Strong-versus-weak process summary

Here, *strong* is the fixed case-study panel (gemma4:26b, qwen3.8:27b, and
qwen3-coder-next), and *weak* is qwen3.5:9b. Values are run-level median
[IQR]. Binary metrics also show the raw occurrence rate in parentheses. Under
r2, a step is one parsed tool result, so `steps` and `tool calls` are
identical by construction.

| Cohort / condition | n (tasks x repetitions x models) | Steps | Tool calls | Assistant turns | Validate-intent after last edit | Successful command after last edit | Any same-path `write_file` rewrite | Timeout |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Strong / C0 | 162 (18 x 3 x 3) | 8.0 [7.0, 11.0] | 8.0 [7.0, 11.0] | 9.0 [7.2, 12.0] | 100 [0, 100]% (68.5%) | 100 [100, 100]% (93.8%) | 0 [0, 75]% (25.3%) | 0 [0, 0]% (0.0%) |
| Strong / C1 | 162 (18 x 3 x 3) | 9.0 [7.0, 12.0] | 9.0 [7.0, 12.0] | 9.0 [7.0, 12.0] | 100 [0, 100]% (71.6%) | 100 [100, 100]% (97.5%) | 0 [0, 0]% (17.9%) | 0 [0, 0]% (0.0%) |
| Weak / C0 | 89 usable of 90 (18 x 5) | 8.0 [6.0, 14.0] | 8.0 [6.0, 14.0] | 9.0 [7.0, 15.0] | 100 [0, 100]% (64.0%) | 100 [100, 100]% (86.5%) | 0 [0, 100]% (40.4%) | 0 [0, 0]% (1.1%) |
| Weak / C1 | 89 usable of 90 (18 x 5) | 7.0 [5.0, 19.0] | 7.0 [5.0, 19.0] | 8.0 [6.0, 20.0] | 0 [0, 100]% (38.2%) | 100 [0, 100]% (65.2%) | 0 [0, 100]% (31.5%) | 0 [0, 0]% (1.1%) |

The strict validation-intent metric is the preregistered primary process
definition; any successful post-edit command is the sensitivity definition.
The original qwen-generated directional hypothesis was specifically that C1
would *decrease* validation after the last edit relative to C0. The table is a
process description, not a mediation analysis.

### Detectability and post-hoc informative-task sensitivity

For the controlled three-repeat models, an approximate two-sided 5%, 80%-power
minimum detectable difference was computed from the observed within-task
Bernoulli variance: each condition's unbiased repeat variance is divided by
three, the two condition variances are added, and the mean across 18 tasks is
divided by 18 before multiplying the standard error by 1.96 + 0.842. This
within-task-only planning calculation gives 11.6 points for gemma4:26b, 10.4
for qwen3-coder-next, and 9.0 for qwen3.8:27b. Llama has zero observed variance
at its floor, making the formula degenerate rather than demonstrating high
power. The formal bootstrap remains the inferential analysis because it also
respects task-level heterogeneity.

The following sensitivity analysis is explicitly **post hoc**. For each
model, it removes task pairs where both C0 and C1 are all failures or both are
all passes, then repeats the task bootstrap. It is selection on observed
outcomes and is not a replacement for the full 18-task result.

| Model | Retained tasks | Removed all-0 | Removed all-1 | C1-C0 pp [95% bootstrap interval] |
|---|---:|---:|---:|---:|
| qwen3.5:9b | 11 | 3 | 4 | +3.2 [-11.8, 16.8] |
| gemma4:26b | 3 | 5 | 10 | +33.3 [0.0, 66.7] |
| qwen3.8:27b | 3 | 1 | 14 | +11.1 [-33.3, 33.3] |
| qwen3-coder-next | 4 | 5 | 9 | +8.3 [-33.3, 50.0] |
| llama3.1:8b | 0 | 18 | 0 | not estimable |
| gpt-5.6-sol (reference anchor) | 2 | 2 | 14 | 0.0 [-33.3, 33.3] |

### Denominator and overwrite reconciliation

Qwen's core denominator is 89 rather than 54 because it was scheduled for
five repeats per task (18 x 5 = 90) and one retry-exhausted transport failure
was excluded in each of C0 and C1. Each other core condition used three
repeats (18 x 3 = 54); the strong-model core had no protocol provider errors.
Across all qwen S7 conditions, the five retry-exhausted records are distributed
as follows: one C0 `test_out_c02_sessions`, one C1
`test_in_a09_header`, two L3b `test_out_c02_sessions`, and one L3b
`test_out_c03_consolidate`. Thus two affect the core denominators and three
affect only the exploratory L3b denominator.

The active GPT cohort has 108 records and 108 unique run ids: 54 C0 and 54 C1,
with no exact run-id overlap. After parsing the `-rN` suffix, both conditions
contain the same 54 task-repetition keys and neither contains duplicates. At
the owner's direction, the two temporary pre-overwrite copies were removed
from `/tmp`; they are not part of the active analysis or retained repository
data.

One controlled core task, `test_in_b11_bucket`, is an all-zero floor; there
are no all-one ceiling tasks. Full split and b09 sensitivity views are in
`docs/s7_formal_results_20261011.md` and `results/tables/s7/`.

## 6. Case studies

The fixed-seed, post-hoc case study reads only S4 `dev_diagnose`. Three tasks
were eligible for strong-pass/weak-fail pairing: A03, A05, and B03. A01, B01,
and B05 had no qwen failure candidate. No same-task weak-success/strong-failure
counterexample existed; this absence was retained. Recurrent strong-trajectory
behaviors were reading before editing, validating after editing, avoiding
repeated full rewrites, and rereading after editing. Full step tables are in
`docs/case_studies.md`. Their mechanically defined strong-pass, strong-fail,
weak-pass, and weak-fail occurrence rates are reported in
`docs/behavior_outcome_crosstab.md`. The cross-tab uses only S4
`dev_diagnose`; it is observational and does not imply that a behavior causes
verifier success.

More importantly, the four behaviors do not separate success from failure in
this sample. Reading before editing is 100% in all four cells. Post-edit
validation and rereading are not lower in the failure cells: validation is
70.2% versus 100.0% for strong pass/fail and 30.0% versus 62.5% for weak
pass/fail; rereading is 25.5% versus 50.0% and 20.0% versus 50.0%,
respectively. Avoiding a repeated full-file write is also similar across the
four cells (76.6%, 83.3%, 80.0%, and 75.0%). The weak-pass and weak-fail cells
contain only n=10 and n=8 runs, so these are descriptive rates, not stable
failure predictors.

This connects directly to Section 9: v1 externalizes these same behaviors.
Its +45.0-point change in strict post-edit validation with no verifier-pass
change is consistent with the cross-tab's observation that performing the
behavior does not by itself explain success. The mechanical failure
classification is in `docs/weak_failure_taxonomy.md`. Across the 98
weak-target failures, terminal flags are non-exclusive: 57 have an empty final
message, 13 reach the step limit, and 2 time out. The same document tabulates
failed verifier checks and comparable strong-model S7 failure rows; these
descriptive counts do not attribute a cause.

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

In S7, the preregistered directional prediction was that C1 would reduce
post-edit validation relative to C0. That direction is observed for qwen
(task-level C1-minus-C0 validation after final edit: -25.0 points) but not
across the independent r2 models: gemma is +11.1, qwen3.8 is 0.0, qwen-coder
is -1.9, and llama is +38.9 points. Explicit C1 skill-reference rates also do
not rise monotonically with model capability under the locked parser. For
qwen3.8, qwen-coder-next, and llama, C1 was supplied inline in each serialized
request rather than as a workspace skill file. A local re-scan of stored
content and reasoning fields found literal skill markers in 0/54, 0/54, and
1/54 usable C1 runs, respectively, matching the locked mention-based parser;
see `docs/s7_c1_reference_diagnostic.md`. Thus the near-zero citation rate is
a delivery-and-measurement limitation, not evidence that those models were not
shown the protocol.

## 8. Skill modifications

v1 externalizes requirement inventory, rereading, and validation behaviors
identified in dev diagnosis. L3b is a content-independent fixed reminder after
call 32. Both are exploratory; neither changes the S7 core. S8 candidates are
derived only from recurrent dev-diagnose case behaviors and are documented
separately. No v2 skill is introduced here.

## 9. Was the intervention effective?

The main finding is that the v1 mechanism was activated, but verifier pass
rate did not change. The controlled S7 core likewise does not show a
consistent verifier-pass improvement from C1 across models or splits. v1
produces observable mechanism changes:
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
  it is descriptive only. The temporary archives have been deleted; only the
  retained manifest, `data/s7_gpt_overwrite_audit_20261011.json`, remains.
- r2 and Codex expose different tool surfaces and cannot be assumed equivalent.
- v1 and L3b lack a length-matched generic-prompt control (C3).
- Post-hoc analyses include qwen-generated process hypotheses, S4 cross-model
  turn/call/blind-write metrics, dev-diagnose case selection, mechanical
  convergent-label checks, and sensitivity exploration.

## 11. Future directions

S8 was not executed because it is a post-S7, separately preregistered
follow-up and this report-freeze task explicitly forbids new experiments.
Running it now would also turn a dev-diagnose-derived proposal into an
unregistered extension of the completed benchmark. If separately approved,
S8 may compare an externalized process, a trajectory-imitation prompt, and a
length-matched generic prompt on `dev_validate`; it must not retroactively
modify S7. A new 6--8-task untouched holdout would improve separation between
diagnosis and evaluation.

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
