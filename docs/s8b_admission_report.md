# S8-b task construction and admission report

Date: 2026-10-15 (Asia/Singapore)

State: task construction and admission complete; ready for protocol locking. No S8-b experiment has run.

## Admission result

The final local command `python3 harness/admit_s8b_tasks.py` reported `task_count = 24`, `accepted_count = 24`, and `all_accepted = true`. Every task has five unique named cases. The verifier executes each case's expected-output check and input-nonmutation check; ordered mappings receive an additional order check. Thus tasks have 10 named checks, or 13/15 where mapping order is part of the contract. Reference runs pass all checks; frozen starters and the `return None` shortcut each fail the task suite. All verifier stdout parsed as JSON, and process status agreed with its `passed` field.

Admission runs the reference, starter, and shortcut in separate temporary workspaces with a five-second timeout per run. The final combined time for those three verifier runs was 77.5–94.1 ms per task; all were far below timeout. `tasks/s8b_admission.json` contains per-run timing, return code, parsed checks, timeout state, alignment status, and an input fingerprint so stale results are invalidated when relevant files change.

## Task families and results

| Task | Task family / target risk | Cases | Named checks | Ref | Starter rejected | Shortcut rejected | Alignment | Admission |
|---|---|---:|---:|---|---|---|---|---|
| a01_label_fields | Delimited key/value parsing; first separator, empty fields, duplicate overwrite | 5 | 10 | pass | yes | yes | pass | accepted |
| a02_config_lines | Line configuration parsing; comments, whitespace, repeated keys | 5 | 10 | pass | yes | yes | pass | accepted |
| a03_version_parts | Version parsing; prefix and numeric components | 5 | 10 | pass | yes | yes | pass | accepted |
| a04_duration_units | Duration conversion; mixed and repeated units, malformed token rejection | 5 | 10 | pass | yes | yes | pass | accepted |
| a05_safe_extension | Filename extension extraction; dotfiles and final suffix | 5 | 10 | pass | yes | yes | pass | accepted |
| a06_date_format | Date normalization; calendar validity and separator rules | 5 | 10 | pass | yes | yes | pass | accepted |
| a07_path_segments | Relative path normalization; traversal and empty segments | 5 | 10 | pass | yes | yes | pass | accepted |
| a08_header_names | Header canonicalization; punctuation runs and ASCII policy | 5 | 10 | pass | yes | yes | pass | accepted |
| a09_phone_digits | Phone normalization; country prefix, formatting and invalid characters | 5 | 10 | pass | yes | yes | pass | accepted |
| a10_query_pairs | Query parsing; repeats, encoded separators and malformed escapes | 5 | 10 | pass | yes | yes | pass | accepted |
| a11_slug_text | Unicode slug construction; punctuation collapse | 5 | 10 | pass | yes | yes | pass | accepted |
| a12_range_clamp | Integer coercion and inclusive bounds; boolean rejection | 5 | 10 | pass | yes | yes | pass | accepted |
| b01_record_dedup | Record de-duplication; first position, last value, non-mutation | 5 | 10 | pass | yes | yes | pass | accepted |
| b02_json_cleanup | Recursive JSON cleanup; nested strings, nulls and list order | 5 | 10 | pass | yes | yes | pass | accepted |
| b03_csv_totals | Tabular aggregation; malformed cells, decimal coercion and key order | 5 | 15 | pass | yes | yes | pass | accepted |
| b04_tag_merge | Ordered tag consolidation; normalization and stable uniqueness | 5 | 10 | pass | yes | yes | pass | accepted |
| b05_schema_rename | Schema conversion; legacy mapping, precedence and defaults | 5 | 10 | pass | yes | yes | pass | accepted |
| b06_event_filter | Event filtering; exact types and inclusive valid-date range | 5 | 10 | pass | yes | yes | pass | accepted |
| b07_inventory_delta | Inventory reconciliation; sequential updates, underflow and key order | 5 | 13 | pass | yes | yes | pass | accepted |
| b08_contact_group | Contact grouping; email-domain normalization and stable group order | 5 | 15 | pass | yes | yes | pass | accepted |
| b09_invoice_cents | Monetary conversion; exact decimal half-up rounding and invalid values | 5 | 10 | pass | yes | yes | pass | accepted |
| b10_log_summary | Log-level counts; unknown levels and fixed output order | 5 | 15 | pass | yes | yes | pass | accepted |
| b11_manifest_diff | Manifest comparison; missing fields, duplicates and sorted results | 5 | 10 | pass | yes | yes | pass | accepted |
| b12_bucket_assign | Categorical bucketing; inclusive and overlapping boundaries | 5 | 10 | pass | yes | yes | pass | accepted |

## Task/verifier contract

Each task statement now records the exact accepted input shape, output shape,
edge and malformed-input behavior, ordering/overwrite policy, and public
`transform(value)` signature. The admission harness verifies that each
contract's requirement sentences appear in that task's `task.md`. Multi-input
tasks pass one dictionary or list through `value`; the signature is unchanged.
The verifier checks a deep-copied input after every run to ensure the function
did not mutate it. The few tasks whose contract observes mapping iteration
order also receive explicit mapping-order checks.

## Repairs made

- Fixed a02's original fixtures: the JSON strings contained literal backslash+n
  characters rather than line breaks. Runtime inspection showed that
  `splitlines()` therefore received a single line and every expected parse
  failed. The new contract uses actual newline characters and passes all five
  cases.
- Expanded all task statements from brief summaries into complete input and
  behavior contracts aligned with their reference functions and fixtures.
- Added a deterministic authoring utility for producing the 24 contracts and
  corresponding task statements from the same requirement definitions.
- Strengthened the verifier with JSON-compatible tuple comparison, input
  non-mutation checks, and explicit mapping-order checks where required.
- Strengthened admission with required-file/schema checks, at least four cases,
  unique case names, requirement-to-task-text checks, per-process timeout,
  JSON/exit consistency checks, named-check completeness, and content
  fingerprints that invalidate stale acceptance records.

## Commands and guardrails

Construction and incremental admission:

```text
python3 harness/build_s8b_contracts.py
python3 harness/admit_s8b_tasks.py --task <task_id>
```

Final admission:

```text
python3 harness/admit_s8b_tasks.py
```

Syntax validation:

```text
python3 -m py_compile harness/admit_s8b_tasks.py harness/materialize_s8b_tasks.py verifiers/s8b_contract_verifier.py
```

No model or external LLM endpoint was called. No existing trajectory or test
trajectory was used to choose task rules, cases, or reference answers. No S7
task, verifier, schedule, prompt, runner, result, or analysis asset was edited.
No provider request was made, no execution schedule was created or run, and
none of the 192 planned runs was started.
