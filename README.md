# Trajectory-Driven Transferable Skill Optimization

This repository implements a controlled benchmark for studying cross-model agent trajectories and turning observable failure patterns into transferable skill transformations.

The project is currently at D1/D2: formal controls, model-provider preflight, and an isolated pilot task are in place. Historical exploratory benchmark assets have been removed from the current tree and are not part of the formal study.

## Current layout

- `config/`: locked model panel and shared controls.
- `skills/`: v0 skill definitions for A, B, and C.
- `tasks/pilot/`: calibration-task protocol and candidate pool.
- `verifiers/`: external verifier implementations and sanity fixtures.
- `harness/`: clean-workspace execution contracts.
- `metadata/`: reproducibility schema.
- `data/pilot_connectivity/`: provider/function-calling preflight.
- `data/pilot_runs/`: non-formal pilot trajectories.

Formal `dev`, `test_in`, and `test_out` tasks will be added only after the pilot pool establishes stable task difficulty and a valid model capability gradient.
