# Ornith task-hash audit

Date: 2026-10-15

During the completed Ornith schedule audit, three of the six records for
`test_out_c02_sessions` were found to carry task-tree hash
`68e6e33bd25e6d44eac0bff6fc1aaa5c7878f7e0e56700128acacecf9a0c7321`
instead of the frozen seed hash
`c608400df969983520dabc58f80bab1e8f275d56f8dad0b334e24ffb5cbbedc8`.

Affected records:

- `s7-ornith1-5-35b-test_out_c02_sessions-C0-r1`
- `s7-ornith1-5-35b-test_out_c02_sessions-C1-r2`
- `s7-ornith1-5-35b-test_out_c02_sessions-C1-r3`

The other three records for the task used the frozen hash. No completed record
was deleted, overwritten, or rerun. The repository task template was restored
to the frozen hash before GLM reached this task. Ornith results are reported
both as recorded and with all six `test_out_c02_sessions` records excluded.
The task-paired estimate changes from -1.9 pp (95% paired-bootstrap interval
[-16.7, 9.3]) to -2.0 pp ([-17.6, 9.8]); the interpretation is unchanged.
