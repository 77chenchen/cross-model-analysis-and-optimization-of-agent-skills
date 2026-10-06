Fixed `parse_labels` to trim keys and values, preserve additional `=` characters in values, and ignore malformed or empty entries. The public signature and tests are unchanged.

Verification: `python3 -m unittest discover -v` — all 4 tests passed.