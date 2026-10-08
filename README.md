# Trajectory-Driven Transferable Skill Optimization

This repository implements a controlled benchmark for studying cross-model agent trajectories and turning observable failure patterns into transferable skill transformations.

The project has completed D1--D5 pilot infrastructure, weak-model diagnosis,
and a recorded v0/v1 pilot comparison. Historical exploratory benchmark assets
have been removed from the current tree and are not part of the formal study.

## Current layout

- `config/`: locked model panel and shared controls.
- `skills/`: v0 skill definitions for A, B, and C.
- `tasks/pilot/`: calibration-task protocol and candidate pool.
- `verifiers/`: external verifier implementations and sanity fixtures.
- `harness/`: clean-workspace execution contracts.
- `metadata/`: reproducibility schema.
- `data/pilot_connectivity/`: provider/function-calling preflight.
- `data/pilot_runs/`: non-formal pilot trajectories.

## Split lock (S3, 2026-10-07)

All 12 viewed pilot tasks are now designated development-only: six balanced
A/B tasks in `dev_diagnose` and six in `dev_validate` (the exact membership is
locked in `config/splits.yaml`).  The formal pool contains 6 new Skill-A and 6
new Skill-B `test_in` tasks plus 6 new Skill-C `test_out` tasks.  Every formal
task has a task description, a distinct deliberately faulty seed, an external
contract verifier, and positive/template/shortcut admission fixtures; the
admission report records 18/18 accepted.

After this lock, only `dev_diagnose` trajectories may inform skill changes;
`dev_validate` selects among pre-specified versions.  `test_in` and `test_out`
are evaluation-only and will not be run or inspected beyond this construction
and admission step until the S7 analysis lock.

## Sampling policy lock (S0, 2026-10-07)

For future calibration, dev, and Part 1 baselines, the requested policy is
temperature **0.5** and **three** fresh repetitions per task-condition. Tasks,
not repetitions, are the statistical sampling unit; repetitions estimate
within-task variation only. The weak-target repetition count for the eventual
S7 final benchmark will be selected after inspecting dev variation, before S7
runs begin.

The current Codex CLI rejects both `temperature` and `seed` as unsupported
configuration fields before dispatching a request. Therefore the present runner
cannot guarantee a requested temperature or seed for any configured provider.
New runs record `temperature_requested: 0.5`, a null effective temperature,
and `sampling_control: unsupported_by_cli`; any analysis must state this
uncontrolled sampling setting as a limitation. Existing temperature-0 pilot
metadata is retained unchanged, marked as legacy temp0 pilot evidence, and is
never pooled with the future sampling-policy cohort.

## Recorded D5 negative result

Tag `d5-v0v1-pilot` identifies the D5 qwen3.5:9b pilot comparison. On A03,
A05, B03, and B05, Skill v0 passed 0/4 and Skill v1 passed 0/4. This negative
result is immutable historical evidence: v1 will not be overwritten or
reinterpreted as a formal efficacy result.

## S4 calibration result

S4 completed the locked 216-run descriptive calibration matrix (six models,
12 pilot tasks, three fresh repetitions, frozen v0 skills). `gemma4:26b` is
the selected primary weak target for dev-only work because 5 of its 12 task
conditions had observed pass rates in the 20%--80% calibration interval.
`qwen3.5:9b` is a documented floor condition (0/36 passes; 35
`empty_termination` outcomes), retained as evidence rather than optimized
against. See `docs/s4_calibration_results.md` and the run/task tables in
`data/calibration_runs/` for descriptive results and limitations.

## S5 dev-only baseline

S5 collected 72 new v0 observations on the locked dev pool: GPT-5.6 and the
selected gemma4:26b target, each on 12 tasks with three repetitions. The
blind judge packet boundary was validated for all 72 trajectories. Summary
tables, a static trajectory-pattern figure, and four descriptive cases are in
`data/s5_results/`, `docs/s5_baseline_results.md`, and `docs/s5_cases.md`.
Twenty-four blinded packets await independent human labels before Cohen's
kappa can be calculated; no agreement figure is reported before that review.

## Control-variable reality (revised 2026-10-08)

| variable | requested protocol | current Codex CLI path | status in recorded runs |
|---|---|---|---|
| temperature | 0.5 | `--strict-config` rejects `temperature` before dispatch | requested; not controlled |
| seed | fixed when supported | `--strict-config` rejects `seed` before dispatch | not controlled |
| max steps | 40 | no native `codex exec` option; supplied only in the agent prompt | requested; not enforced by runner |
| context limit | 65,536 | no verified CLI override or returned effective value | requested; not controlled |
| timeout | 20 minutes | `run_with_timeout.py` creates a process group and terminates it at 1,200 seconds | controlled and recorded |

The first four rows are limitations of the current CLI execution path, not
claims about raw provider APIs. New metadata distinguishes requested from
effective settings; analysis treats task as the statistical unit and does not
pool the legacy temperature-0 pilot with the newer cohort.

## Runner r2 lock (B1, 2026-10-08)

`harness/r2_agent.py` is the separate, direct SoC LaaS Chat Completions runner
for open-weight models. It transmits temperature `0.5`, accepts an optional
seed, enforces a local 40-tool-call cap and a 65,536-token conservative
context estimate, bounds each shell command to 120 seconds, and is itself
wrapped in the existing 20-minute process-group timeout. Every response is
archived before interpretation, including full reasoning payloads where the
provider supplies them, finish reason, usage fields, and tool-call parsing
status. It never retries a provider call and sends no extra user continuation;
the only follow-up turn is the required tool-result message.

The r2 pilot entry point can address only `tasks/pilot`, so it cannot run a
test split. Temperature is considered transport-accepted only after the
endpoint returns a response. A requested seed is likewise recorded as
transport-accepted when the request succeeds; it is not claimed to be an
effective deterministic control unless the provider explicitly echoes it.
The direct provider currently supplies no such temperature/seed echo, which
remains a reported limitation. Configuration is frozen in
`config/r2_runner_lock.yaml` before any r2 test run.

All historical CLI artifacts remain `runner=codex-cli` legacy evidence and
are never pooled with r2 observations. GPT-5.6 remains a Codex-only reference
anchor with uncontrolled sampling unless direct API credentials become
available.

## B2 runner comparison (2026-10-08)

One fresh Gemma4:26b v0 observation was collected per runner on each locked
pilot/dev task. The direct r2 runner passed 11/12 while the uncontrolled
Codex CLI runner passed 8/12; the runners diverged on A05, B02, and B03. This
is descriptive evidence that the runner implementations are not exchangeable,
not an efficacy result or a model ranking. Details and the A04-excluded view
are in `docs/b2_runner_equivalence.md`. B3 therefore starts a distinct r2
cohort and does not pool any r2 result with legacy CLI results.

## Protocol revision (2026-10-08; before any test run)

S7, if it is ever authorized after an effective dev-validate result, has a
core purpose of collecting C0 (no skill) and C1 (original skill) cross-model
baselines. Skill v1, L3, and any future mechanism-specific condition are
exploratory: report their activation rate and descriptive outcomes separately.
An “intervention effective” claim requires both observed mechanism activation
and an observable dev-validate improvement; a pass-rate difference alone is
insufficient. No test split has been run under this revision.
