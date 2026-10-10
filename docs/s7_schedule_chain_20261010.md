# S7 schedule-chain operational note

Date: 2026-10-10.

The locked per-model S7 schedule runners intentionally exit after one model.
`harness/chain_s7_schedules.py` is an outer operational supervisor that connects
those existing runners. It does not edit or replace runner r2, task assets,
skills, prompts, parser definitions, schedule TSVs, seeds, conditions, retries,
or analysis definitions.

For a schedule that was already active when the supervisor started, the
supervisor waits for its PID and treats that schedule as a completion barrier.
It does not resume that schedule: if the process exits before every row has the
required artifacts, the chain stops. Later schedules are invoked serially in
the supplied order through the already locked direct-provider or Codex schedule
runner. A nonzero exit or incomplete row stops the chain rather than skipping
to another model.

The live PID, state, and log are stored below the ignored S7 output root at
`data/s7_runs/_schedule_chain/`. The advisory file lock prevents two chain
supervisors from running concurrently.
