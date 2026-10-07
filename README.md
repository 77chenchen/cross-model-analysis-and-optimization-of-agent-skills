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

Formal `dev`, `test_in`, and `test_out` tasks will be added only after the
pilot pool establishes stable task difficulty and a valid model capability
gradient.

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
