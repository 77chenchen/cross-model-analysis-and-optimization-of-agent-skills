# S3 split lock

Locked 2026-10-07.  The complete membership is machine-readable in
`config/splits.yaml` and the formal task inventory is in
`tasks/formal_manifest.json`.

| split | membership | purpose |
|---|---:|---|
| dev_diagnose | 6 viewed pilot tasks, balanced A/B | diagnosis and skill design |
| dev_validate | 6 viewed pilot tasks, balanced A/B | version selection only |
| test_in | 12 newly authored tasks, 6 A + 6 B | held-out in-skill evaluation |
| test_out | 6 newly authored Skill-C tasks | held-out transfer evaluation |

Formal tasks are admitted only if the external contract verifier accepts the
positive fixture and rejects both the buggy template and shortcut fixture.
`python3 harness/check_s3_admission.py` produces `tasks/s3_admission.json`;
the S3 lock report records all 18 tasks as accepted.

No model execution occurred during S3.  Before S7, formal split contents may
be accessed only for immutable admission or infrastructure work, never to
choose or revise a skill.
