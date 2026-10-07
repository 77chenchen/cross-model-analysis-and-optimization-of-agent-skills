# Formal task protocol

`pilot/` contains 12 viewed calibration tasks. They are permanently excluded from
the formal holdout analysis and are split by `config/splits.yaml` into six
`dev_diagnose` tasks and six `dev_validate` tasks.

The development split is represented by the locked pilot membership above.
Only `dev_diagnose` may be used to diagnose trajectories and design
transformation rules; `dev_validate` is used only to select versions.

`test_in/` contains 6 held-out tasks for A and 6 for B. `test_out/` contains 6
Skill C tasks. The S3 construction/admission check is the only allowed
pre-S7 access to these splits; their agent-run results must remain unseen until
the transformation operator is frozen.

Each task has an immutable template, visible task description, declared split, and a verifier-owned evaluation package. A task enters any split only after its verifier passes positive, negative, and shortcut/gaming checks.
