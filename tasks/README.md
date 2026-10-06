# Formal task protocol

`pilot/` contains 10--15 calibration tasks and is permanently excluded from formal analysis.

`dev/` contains 5 tasks for Skill A and 5 for Skill B. It is the only split visible while diagnosing trajectories and designing transformation rules.

`test_in/` contains 7 held-out tasks for A and 7 for B. `test_out/` contains 12 Skill C tasks. These directories remain unopened until the transformation operator is frozen.

Each task has an immutable template, visible task description, declared split, and a verifier-owned evaluation package. A task enters any split only after its verifier passes positive, negative, and shortcut/gaming checks.
