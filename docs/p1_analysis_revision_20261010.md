# P1 analysis revision

Date: 2026-10-10. This is an analysis-only supplement. It changes no frozen
task, verifier, fixture, skill, L3b protocol, S7 condition or schedule, runner,
parser, or prompt. No model or judge request was issued.

## Prior items confirmed

- The call-32 audit found 0/7 cases where replay partial 1.0 later failed the
  frozen verifier (2 baseline and 5 L3b). Formal S7 L3b reporting is limited to
  trigger counts and call-32 state distributions; it will not test
  post-trigger conversion.
- The primary validation definition is a post-final-edit `run_command` whose
  command contains `test`, `pytest`, `unittest`, or `py_compile`; any successful
  post-edit command is the sensitivity definition. The existing qwen C0/C1
  audit reports both definitions, task directions, and quantiles.
- `provider_error_protocol` means retry-exhausted transport failure. S4 has 5
  and original S5 has 8 such records. The older broad provider flag remains
  legacy diagnostics; hard timeouts stay in the pass denominator.
- Frozen `test_in_b09_phone` task text and verifier contain no looping or slow
  operation. Its two 20-minute qwen incidents are retained as failures and all
  applicable summaries will be shown with and without the task. Together with
  A04, it is carried in the known-task-issues table.
- The S4 dev-diagnose cross-model behavior audit is post hoc. The S7 version of
  assistant-turn, calls-per-turn, and blind-write metrics was declared before
  cross-model S7 analysis and remains gated until S7 completion.

## Human--judge agreement supplement

All 24 records now identify the confirmed human annotator as `wangqichen` and
pass the blinded-review validator. `harness/score_b5_r2_human_review.py` now
stores the human-by-judge 2x2 counts for every failure label. Macro kappa uses
only the labels with variance in both raters; macro PABAK covers all eight
labels. Zero-variance labels are retained in the table and PABAK but excluded
from macro kappa because Cohen's kappa is not estimable.

The mechanical audit in `data/b5_r2_human_mechanical_audit_20261010.json`
compares confirmed human labels with four deterministic trajectory signals.
Raw agreement receives an exact Clopper--Pearson interval. This is a post-hoc
convergent audit, not a replacement for human interpretation: the mechanical
rules are deliberately narrower than the semantic labels.

For conclusions, LLM-judge labels may be used as supporting evidence only for
`file_corruption`, `tool_misuse`, and `missed_constraint`. The remaining judge
failure modes are exploratory descriptions. Claims about validation and loops
must use the declared mechanical metrics; `empty_termination` remains wholly
mechanical and outside kappa.
