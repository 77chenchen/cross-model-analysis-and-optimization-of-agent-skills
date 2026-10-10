# S7 `test_in_b09_phone` known-issue record

Date: 2026-10-10. This is a read-only assessment of a frozen, admitted task.
It changes neither the task, verifier, fixture, runner, schedule, nor any
completed record.

## Observed clustering

The two completed qwen3.5:9b 20-minute hard timeouts are
`s7-qwen3-5-9b-test_in_b09_phone-C0-r3` and
`s7-qwen3-5-9b-test_in_b09_phone-C1-r4`. Both have zero completed tool calls.
The former retains two failed request attempts before process termination; the
latter has no completed runtime log. They are hard `timeout` outcomes, not
retry-exhausted `provider_error_protocol` records, and therefore remain
non-passes in the protocol denominator.

## Frozen task and verifier review

The task asks only for normalizing a phone string to `+1XXXXXXXXXX`, accepting
ten digits or a leading `1`, otherwise returning null. The frozen formal
contract has two direct cases: a formatted normal number and a short invalid
string. The verifier imports the submitted solution and evaluates these finite
cases; neither `task.md` nor the contract contains a loop, input generator,
subprocess, network access, or slow-operation requirement.

This review finds no evidence that the frozen task or verifier itself induced a
long execution. The clustering identifies a qwen runner/provider/trajectory
incident on this task, not a demonstrated task-verifier defect. Other observed
qwen phone trajectories include ordinary terminal outcomes, and the ongoing
gemma schedule has already produced ordinary completed phone runs, which is
inconsistent with an intrinsically non-terminating verifier.

## Reporting treatment

The task remains frozen and included. Every formal S7 pass comparison that
includes `test_in_b09_phone` will additionally report the same task-level
summary with it omitted. This leave-one-task-out view is a sensitivity analysis
for the clustered hard timeouts; it cannot turn an admitted task into a
post-hoc exclusion or authorize a rerun.
