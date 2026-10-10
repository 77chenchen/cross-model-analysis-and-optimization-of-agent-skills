# S7 process-hypothesis revision: verifier-pass erratum

Date: 2026-10-10. This revision is committed before generating any monitoring
snapshot or analysis for a model other than qwen3.5:9b. It changes no locked
S7 condition, parser, prompt, schedule, seed, tool, concurrency setting, or
formal-analysis procedure.

## Revised hypotheses

The sole primary process hypothesis is: **relative to C0, C1 has a lower
rate of validation after the final edit.**

Two secondary, descriptive hypotheses are that C1 has more `write_file`
rewrites and more repeated-action loops. They are explicitly secondary because
the qwen generating snapshot has zero medians for both measures in several
cells and non-uniform task-level directions. A new descriptive prediction is
that the rate of an explicit skill reference increases with model capability.
For v1 relative to C1, the directional prediction retained for test-in only is
higher validation after the final edit.

The completed qwen3.5:9b snapshot generated these hypotheses and is not an
independent test. The other five models (`gemma4:26b`, `qwen3.8:27b`,
`qwen3-coder-next`, `llama3.1:8b`, and the uncontrolled GPT-5.6 Sol reference
anchor) are independent checks only after their respective locked schedules
complete.

## Outcome and comparison rules

All pass-rate quantities use the frozen verifier's `passed` field, never the
legacy `outcome_category`. Provider-error records are excluded from the primary
pass-rate denominator and reported separately; the sensitivity denominator
includes them as non-passes. The legacy category remains retained as historical
metadata only.

The v1-versus-C1 comparison is limited to the 12 `test_in` tasks and uses
task-level pairing. It is exploratory and must not be used as a formal S7
effect claim. Formal S7 analysis still starts only after all 870 scheduled runs
are complete.
