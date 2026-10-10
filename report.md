# Skill-trajectory benchmark report

Status: pre-S7 analysis skeleton. Every formal test result is marked
`[S7 PENDING]`. This document does not interpret the live S7 batch.

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
The locked plan contains 870 interleaved runs. `[S7 PENDING]`

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

`[S7 PENDING: C0/C1 model-by-split pass tables, task-paired differences,
activation-stratified descriptions, floors/ceilings, and formal figures.]`

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

## 8. Skill modifications

v1 externalizes requirement inventory, rereading, and validation behaviors
identified in dev diagnosis. L3b is a content-independent fixed reminder after
call 32. Both are exploratory; neither changes the S7 core. S8 candidates are
derived only from recurrent dev-diagnose case behaviors and are documented
separately. No v2 skill is introduced here.

## 9. Was the intervention effective?

`[S7 PENDING]` No effectiveness statement is made before the locked benchmark
finishes. Even after completion, exploratory v1/L3b language is restricted to
mechanism activation and descriptive outcomes. “Effective” requires observed
mechanism activation and observable improvement under the preregistered rule.

## 10. Limitations

- Synthetic tasks and self-authored skills limit external validity.
- Calibration contains model/task floors and ceilings; uninformative tasks
  reduce power.
- Task counts are small; repetitions do not create additional task units.
- The LLM judge may be biased. There is one human annotator, the researcher;
  the 24-packet comparison is human-vs-judge, incompletely blinded, and small.
- GPT runs through Codex are a sampling-uncontrolled reference anchor.
- r2 and Codex expose different tool surfaces and cannot be assumed equivalent.
- v1 and L3b lack a length-matched generic-prompt control (C3).
- Post-hoc analyses include qwen-generated process hypotheses, S4 cross-model
  turn/call/blind-write metrics, dev-diagnose case selection, mechanical
  convergent-label checks, and sensitivity exploration.

## 11. Future directions

After S7, apply the locked verifier-pass patch, generate formal tables once,
and create a blinded model/outcome-stratified judge subset. S8 may compare an
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
