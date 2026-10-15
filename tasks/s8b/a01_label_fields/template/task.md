# Repair transform

## Delimited key/value parsing

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a string; otherwise return {}.
- Split on semicolons, then split each entry only at its first equals sign.
- Trim key and value; skip malformed entries and entries with empty trimmed key or value.
- For duplicate keys, the last valid value wins.

Do not modify benchmark-owned verifier files.
