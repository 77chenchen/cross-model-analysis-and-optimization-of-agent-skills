Fixed `dedupe_records` to ignore missing, empty, and non-string IDs; retain the record with the greatest numeric `updated_at`; and keep the earlier record on ties. The function preserves first-seen ID order and does not mutate input records.

Verification: `python3 -m unittest -v` passed all 3 tests.