Fixed `parse_config` while preserving its public signature. It now trims keys and values, removes whitespace-prefixed inline comments, preserves embedded `#`, and skips empty or malformed entries.

Added regression coverage. Verification: `python3 -m unittest -v` — all 5 tests passed.