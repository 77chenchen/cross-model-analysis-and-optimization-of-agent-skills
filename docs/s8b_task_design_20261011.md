# S8-b task-design record

Status: task construction and admission complete; ready for protocol locking. This is a new dev-only study,
not a revision of S7 or of the abandoned S8-a pilot.

## Fixed matrix target

The intended matrix is 24 newly authored development tasks × four prompt arms
(fresh C1/v0, externalized process, abstract trajectory imitation, and a
length-matched generic control) × two repetitions = 192 runs. The task is the
inferential unit. Two repetitions estimate gross within-task instability only;
they are not treated as two independent tasks.

## Separation from prior evidence

None of the 24 task identifiers below may be a prior `dev_diagnose`,
`dev_validate`, or S7 test task. Candidate process behaviors remain derived
from the earlier strong/weak paired diagnostic; these tasks are a fresh
development evaluation set. The abandoned S8-a artifacts were discarded before
this design record was created and will not be combined with S8-b.

## Candidate task pool

| Group | ID | Task family | Primary hidden-risk category |
|---|---|---|---|
| A | a01_label_fields | delimited key/value parsing | separator preservation and empty fields |
| A | a02_config_lines | line-oriented configuration parsing | comments, whitespace, repeated keys |
| A | a03_version_parts | version parsing | optional prefix and numeric ordering |
| A | a04_duration_units | duration conversion | mixed units and invalid tokens |
| A | a05_safe_extension | filename extension extraction | dotfiles and case normalization |
| A | a06_date_format | date normalization | calendar validity and alternate separator |
| A | a07_path_segments | relative-path normalization | traversal and empty segments |
| A | a08_header_names | header canonicalization | punctuation and duplicate separators |
| A | a09_phone_digits | phone normalization | country prefix and invalid length |
| A | a10_query_pairs | query-string parsing | repeated keys and encoded separators |
| A | a11_slug_text | slug construction | Unicode/punctuation collapse |
| A | a12_range_clamp | bounded integer conversion | coercion and bounds |
| B | b01_record_dedup | record de-duplication | non-mutation and first/last policy |
| B | b02_json_cleanup | JSON-like value cleanup | recursive normalization |
| B | b03_csv_totals | tabular aggregation | malformed cells and numeric coercion |
| B | b04_tag_merge | tag-list consolidation | order-preserving uniqueness |
| B | b05_schema_rename | record schema conversion | missing keys and defaults |
| B | b06_event_filter | event filtering | type and timestamp boundaries |
| B | b07_inventory_delta | inventory reconciliation | absent keys and negative values |
| B | b08_contact_group | contact grouping | normalized grouping keys |
| B | b09_invoice_cents | monetary total conversion | rounding and invalid amounts |
| B | b10_log_summary | log-level summary | unknown levels and stable order |
| B | b11_manifest_diff | file-manifest comparison | ordering and missing fields |
| B | b12_bucket_assign | categorical bucketing | inclusive boundaries and invalid input |

Each task will receive: a self-contained `task.md`, a deliberately defective
starter implementation, fixed fixtures, an external verifier with multiple
named checks, and positive/negative/shortcut admission checks. Any task that
fails admission will be replaced before the S8-b lock; it will not be repaired
after trajectories are seen.

## Admission and lock gates

Before a provider request, all 24 tasks must pass: (1) reference/positive
implementation passes every named verifier check; (2) the frozen starter
fails; (3) a simple shortcut fails; (4) verifier termination is within the
locked timeout; and (5) task text specifies every verifier-observed
requirement. The final prompt manifest, task/verifier tree hash, schedule hash,
runner hash, and analysis script hash will then be committed in an S8-b lock.
