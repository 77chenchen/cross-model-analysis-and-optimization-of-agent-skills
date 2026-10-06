Fixed `dedupe_records` to ignore invalid IDs, retain the greatest timestamp, and keep the earlier record on ties. The public signature is unchanged, and inputs are not mutated.

Added regression coverage for older timestamps and unhashable IDs.

Verification: `python3 -m unittest -v` — all 4 tests pass.