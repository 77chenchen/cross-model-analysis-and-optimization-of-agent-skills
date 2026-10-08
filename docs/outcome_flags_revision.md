# Outcome representation revision (2026-10-08)

`outcome_category` is retained as the **legacy exclusive label** for
compatibility. It is a precedence-based summary and must not be treated as a
complete description of a run.

Newly recorded runs also contain `legacy_outcome_category` and independent
boolean `outcome_flags`:

- `final_empty`
- `no_edit`
- `compile_error`
- `verifier_fail`
- `timeout`
- `context_overflow`
- `provider_error`

The flags may co-occur. For example, a run can have an empty final response,
no source edit, a failed verifier, and a nonzero partial score. Existing run
directories and metadata are not rewritten; their missing flags remain
unknown rather than being retroactively asserted.
