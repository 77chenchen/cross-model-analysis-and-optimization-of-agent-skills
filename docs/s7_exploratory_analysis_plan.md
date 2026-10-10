# S7 exploratory-condition analysis plan

Date: 2026-10-10. This plan is committed before any new v1 or L3b S7 result
calculation. It does not alter the running matrix, prompts, models, seeds,
schedule, or core C0/C1 analysis plan.

## Status and scope

v1 and L3b are exploratory conditions for `qwen3.5:9b` only. They are not
the S7 confirmatory comparison and are never described as effective. All
reports label their estimates as descriptive and report `test_in` and
`test_out` separately.

## v1 versus C1

The v1 comparison uses only the 12 `test_in` Skill-A/Skill-B tasks, because
there is no frozen v1 Skill-C protocol. For each task, aggregate its five
fresh repetitions within condition and calculate the task-level v1-minus-C1
difference. A paired bootstrap resamples the 12 matched tasks. Provider-error
exclusion from the primary denominator and the all-scheduled sensitivity view
are both reported. `test_out` is explicitly absent, not a zero-valued v1
result.

## L3b versus C1

L3b uses the frozen v0 skill and covers all 18 tasks. It is interpreted by
fixed call-depth strata, not as a single unconditional intervention estimate:

- **A layer:** trajectories reaching call 32. For L3b, the reminder is
  injected at that fixed point. Report trigger count and, conditional on a
  trigger, subsequent validation, post-call-32 partial change where replay is
  valid, and final outcome. The C1 A layer is a descriptive negative control.
- **B layer:** trajectories ending before call 32. No L3b reminder is ever
  inserted. Any L3b-minus-C1 difference here is treated only as a noise and
  imbalance estimate, not as a mechanism effect.

The condition-specific call-32 stratum is descriptive because reaching 32 is
post-assignment behavior. No result is conditioned or reweighted to make an
efficacy claim.

## Shared limitations and reporting limits

There is no length-matched C3 control. Therefore differences involving the
reminder cannot distinguish reminder content from trajectory-length or
budget-related selection. This limitation appears alongside every L3b table.
Wilson intervals, when shown, describe individual proportions only; they are
not between-condition tests. The final report does not make a skill-effect
claim from v1 or L3b, regardless of intermediate numbers.
