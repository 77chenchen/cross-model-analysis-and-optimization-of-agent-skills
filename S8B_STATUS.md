# S8-b status monitor

Last updated: 2026-10-15 (Asia/Singapore)

## Current state

**Task construction and admission complete; ready for protocol locking. No model run is active.**

S8-a was stopped before redesign. Its local, uncommitted run directory was
moved to Trash at the owner's request; no S8-a run is part of S8-b or any
planned analysis.

## Locked target after admission

| Item | Target | Completed | Remaining | State |
|---|---:|---:|---:|---|
| Fresh dev-only task specifications | 24 | 24 | 0 | complete |
| Task templates | 24 | 24 | 0 | complete |
| Fixtures and verifier contracts | 24 | 24 | 0 | complete |
| Independent verifier framework | 1 | 1 | 0 | complete; named output and non-mutation checks |
| Positive / negative / shortcut admission | 24 | 24 | 0 | 24/24 accepted |
| Prompt, schedule, and execution lock | 1 | 0 | 1 | ready to begin; not part of this task |
| qwen3.5:9b S8-b runs | 192 | 0 | 192 | not started |
| Predeclared S8-b analysis | 1 | 0 | 1 | not started; no experiment has run |

## Matrix

`24 fresh tasks × 4 conditions × 2 repetitions = 192 runs`

Conditions: fresh C1/v0 reference, externalized candidate behaviors, abstract
trajectory imitation, and length-matched generic control. The task is the
inferential unit; repetitions measure only gross within-task instability.

## Guardrails

- Only new development tasks may enter S8-b: no prior dev or S7 test task is
  eligible.
- No provider request may occur until all 24 tasks pass admission and the
  S8-b execution lock is committed.
- S7 tasks, verifiers, skills, runner, schedules, data, and results remain
  immutable.
- Once S8-b starts, this file will record completed runs, the active schedule
  row, provider/timeout incidents, and remaining work after each completed
  run.

## References

- [Task design](docs/s8b_task_design_20261011.md)
- [Protocol draft](config/s8b_protocol_draft.yaml)

<!-- S8B_ADMISSION_PROGRESS_BEGIN -->
## Task construction and admission progress

State: **task construction and admission complete; ready for protocol locking**

Completed task admissions: 24/24. Currently accepted: 24/24. No S8 experimental run has been started.

| Task | Cases | Reference | Starter rejected | Shortcut rejected | Task/verifier alignment | Verifier ms | Admission |
|---|---:|---|---|---|---|---:|---|
| a01_label_fields | 5 | pass | yes | yes | pass | 90.512 | accepted |
| a02_config_lines | 5 | pass | yes | yes | pass | 83.470 | accepted |
| a03_version_parts | 5 | pass | yes | yes | pass | 83.774 | accepted |
| a04_duration_units | 5 | pass | yes | yes | pass | 94.078 | accepted |
| a05_safe_extension | 5 | pass | yes | yes | pass | 81.527 | accepted |
| a06_date_format | 5 | pass | yes | yes | pass | 80.583 | accepted |
| a07_path_segments | 5 | pass | yes | yes | pass | 81.134 | accepted |
| a08_header_names | 5 | pass | yes | yes | pass | 82.567 | accepted |
| a09_phone_digits | 5 | pass | yes | yes | pass | 80.390 | accepted |
| a10_query_pairs | 5 | pass | yes | yes | pass | 80.851 | accepted |
| a11_slug_text | 5 | pass | yes | yes | pass | 78.301 | accepted |
| a12_range_clamp | 5 | pass | yes | yes | pass | 77.525 | accepted |
| b01_record_dedup | 5 | pass | yes | yes | pass | 78.448 | accepted |
| b02_json_cleanup | 5 | pass | yes | yes | pass | 77.866 | accepted |
| b03_csv_totals | 5 | pass | yes | yes | pass | 80.593 | accepted |
| b04_tag_merge | 5 | pass | yes | yes | pass | 79.263 | accepted |
| b05_schema_rename | 5 | pass | yes | yes | pass | 78.112 | accepted |
| b06_event_filter | 5 | pass | yes | yes | pass | 79.839 | accepted |
| b07_inventory_delta | 5 | pass | yes | yes | pass | 77.769 | accepted |
| b08_contact_group | 5 | pass | yes | yes | pass | 78.968 | accepted |
| b09_invoice_cents | 5 | pass | yes | yes | pass | 80.704 | accepted |
| b10_log_summary | 5 | pass | yes | yes | pass | 78.425 | accepted |
| b11_manifest_diff | 5 | pass | yes | yes | pass | 77.645 | accepted |
| b12_bucket_assign | 5 | pass | yes | yes | pass | 78.348 | accepted |
<!-- S8B_ADMISSION_PROGRESS_END -->
