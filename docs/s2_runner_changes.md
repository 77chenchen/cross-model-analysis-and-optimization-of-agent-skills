# S2 runner instrumentation

## Added controls

- `run_with_timeout.py` launches each model command in a new process group and
  terminates the entire group after 1,200 seconds. It writes `process.json`.
- `outcomes.py` classifies `pass`, `verifier_fail`, `compile_error`,
  `empty_termination`, `timeout`, `context_overflow`, and `provider_error`.
- `record_run.py` adds `runtime.json`, post-processes verifier check counts,
  and writes a partial score without modifying verifier decision logic.

## Missing historical fields

Old raw JSONL does not expose finish reasons, context-overflow state, or
per-step token/reasoning values. Replays preserve these as null/unknown;
historical metadata is not overwritten. New normalized events carry nullable
fields for these observations when a provider supplies them.

## Validation

Unit tests cover classification precedence and partial-score aggregation. A
one-second process-group timeout smoke test returned exit code 124. Three
historical trajectories were replayed into temporary directories only, yielding
expected classifications without mutating original artifacts.
