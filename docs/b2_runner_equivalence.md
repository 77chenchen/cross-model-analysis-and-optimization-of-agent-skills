# B2: Gemma runner comparison

Date: 2026-10-08
Status: completed; descriptive only.

## Design

On each of the 12 locked pilot/dev tasks, Gemma4:26b received frozen Skill v0
once in a fresh workspace under each runner. The Codex CLI condition is marked
`runner=codex-cli` and has uncontrolled sampling. The r2 condition is marked
`runner=r2-direct-chat-completions`, transmits temperature `0.5` and seed
`20261008`; every request returned successfully, so the seed was accepted by
the transport, but the provider did not echo it and deterministic application
is not claimed. No test-split task was addressed.

This is one paired observation per task, not a randomized equivalence study:
the two runners have different tool transports, and the CLI sampling setting
is uncontrolled. Results are not pooled with one another or with any previous
CLI cohort.

## Results

| Runner | Passes / 12 | Mean verifier partial score | Empty finals | Verifier failures |
|---|---:|---:|---:|---:|
| `codex-cli` | 8 | 0.785 | 2 | 2 |
| `r2-direct-chat-completions` | 11 | 0.972 | 0 | 1 |

The known-defective A04 task is shown but not interpreted as a clean task
signal. Excluding A04, the descriptive figures are 8/11 passes (0.795 mean
partial) for CLI and 11/11 passes (1.000 mean partial) for r2.

Nine task pairs had the same pass/fail and partial-score pattern. The three
different pairs were:

| Task | Codex CLI | r2 |
|---|---|---|
| A05 version parser | `empty_termination`, partial 0.000 | pass, partial 1.000 |
| B02 JSON normalization | `empty_termination`, partial 0.250 | pass, partial 1.000 |
| B03 duplicate audit | `verifier_fail`, partial 0.500 | pass, partial 1.000 |

The r2 trajectories had a visible `stop` finish reason and 8--14 provider
responses (7--13 tool calls) per task. The CLI normalizer did not expose a
comparable provider finish reason or response count. This measurement gap is
itself part of the runner difference.

## Interpretation and gate decision

The observations do **not** establish equivalence. Rather, they establish
that outcomes materially depend on the runner/tool-loop implementation in this
setting. In particular, B0's hypothesis is consistent with the two CLI empty
terminations: r2 preserved and continued tool-call turns on those tasks. This
is not a causal attribution to the Qwen diagnosis or to Gemma capability,
because the runners differ in transport and sampling control as well.

Consequently, B3 must treat r2 as a new, separately analyzed cohort and redo
both S4 calibration and S5 dev baseline under r2 with nonexclusive outcome
flags. Historical CLI values remain legacy reference evidence only.

The complete run-level table is
`data/b2_runner_equivalence/summary.csv`; raw trajectories and raw provider
responses remain archived locally in their run directories.
