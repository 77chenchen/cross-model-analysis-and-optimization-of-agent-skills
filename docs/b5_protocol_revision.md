# B5 protocol revision and pre-registration

Date: 2026-10-08. This document is committed before the replacement and blind
judge batches and before any L3b run. Frozen tasks, fixtures, verifiers, and
v0/v1 skills are out of scope.

## Transport failures

A retry is permitted only when the API request received no response and failed
as HTTP 5xx, a connection failure, or a connection timeout. There are at most
three total attempts, with 1- and 2-second backoff. Retry events store attempt
number, UTC timestamp, error type/text, and backoff in `metadata.json` and
`events.jsonl`. Tool calls, content replies, verifier failures, and a 20-minute
hard timeout are terminal and are never retried. Exhaustion is a
`provider_error`, excluded from the pass denominator and still reported by
task. The eight historical 502s are retained; eight fresh replacement IDs are
scheduled at worker concurrency 1 after the observed two time clusters.

## Outcome compatibility

`final_empty`, `no_edit`, `compile_error`, `verifier_fail`, `timeout`,
`context_overflow`, `provider_error`, and `max_steps_reached` are independent
flags. The new primary category may be `max_steps_reached`; legacy labels keep
the prior `empty_termination` value for these records. No historical record is
backfilled or overwritten.

## L3b

The complete immutable schedule is `config/l3b_protocol.yaml` plus
`config/l3b_dev_validate_matrix.tsv`. At call 32 only, append this exact fixed
message: “You have 8 tool calls remaining. Prioritize validating the current
implementation, then provide a final summary when done.” There is no automatic
retry/continuation, no tool change, and no max-step change. The randomized,
interleaved order covers six dev-validate tasks × two conditions × six repeats.
The runner records activation and post-trigger actions. Seed partial scores are
in `data/pilot_seed_partial_baselines.csv`; all partial reports use their delta
as well as their absolute score.

This is the final intervention round. S7's core remains C0/C1 cross-model
baselines; v1 and L3b are exploratory and cannot support an efficacy claim
without both mechanism activation and observable improvement.

## Blind review

`harness/make_b5_r2_blinded_packets.py` creates 24 newly randomized anonymous
packets from the r2 36-run baseline and stores the mapping outside the public
packet directory. The old packets remain method validation only and are
excluded from any reported Cohen's kappa. The 24 new packets are the sole
human-annotation set for a future kappa calculation.
