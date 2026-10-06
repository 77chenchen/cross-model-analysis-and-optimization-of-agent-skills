# Trajectory annotation protocol

Annotators receive normalized actions and the task identifier, but not model
role, provider, experimental condition, or verifier result. They record the
first event that provides evidence for activation and then score three
observable checkpoints.

- **explicit activation**: the trajectory directly states or enumerates the
  supplied skill's procedure before acting.
- **observable inferred**: the same procedure is evidenced in actions but is
  not directly stated.
- **not observed**: no usable evidence of following the skill procedure.
- **unscorable**: trajectory is absent, corrupt, or ends before a judgement is
  possible. This is not a failure and must be retained in analysis.

Checkpoint definitions are intentionally behavioral: `inspect` means task
materials or target implementation were read; `implement` means an intended
artifact was changed or created; `validate` means a candidate-side validation
command was attempted. Verifier execution by the harness is never counted as
agent validation.

Before formal annotation, two annotators independently label a calibration
set. Resolve discrepancies only after agreement is measured; retain both raw
labels and adjudication notes.
