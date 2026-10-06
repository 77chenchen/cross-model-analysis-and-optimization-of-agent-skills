Fixed `dedupe_records` to ignore invalid IDs, retain the greatest timestamp, and keep the earlier record on ties without mutating inputs. The public signature is unchanged.

Added regression coverage for older records arriving later and non-string list IDs.

Verification: `python3 -m unittest discover -v` — all 4 tests passed.