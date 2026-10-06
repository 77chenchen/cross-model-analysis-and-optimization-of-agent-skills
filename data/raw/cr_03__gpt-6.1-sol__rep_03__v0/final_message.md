Fixed `dedupe_records` to validate IDs, keep the greatest timestamp, and retain the earlier record on ties. The public signature, input records, and output ordering are preserved.

Added regression coverage for older timestamps and unhashable IDs. All 4 tests pass with `python3 -m unittest discover -v`.