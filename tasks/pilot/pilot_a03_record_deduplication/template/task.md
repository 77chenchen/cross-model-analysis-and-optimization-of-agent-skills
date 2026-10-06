# Repair `deduplicate_records`

Fix `deduplicate_records` in `deduplicate.py`. It receives a list of mapping
records with an `id` field. Return new dictionaries containing the first
record for each non-empty, trimmed string id; IDs are compared
case-insensitively. Ignore non-mapping records and missing/blank IDs. Preserve
the order of retained records and never mutate the caller's input.
