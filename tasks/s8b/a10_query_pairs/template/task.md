# Repair transform

## URL query pair parsing

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a string; other input returns {}.
- Ignore one optional leading question mark, split pairs on ampersand, and split each pair at its first equals sign.
- Decode percent escapes as UTF-8 and plus as space; ignore pairs with no equals sign, empty decoded keys, malformed percent escapes, or invalid UTF-8.
- Keep empty values and store values in encounter order as lists, including a one-item list for a single occurrence.

Do not modify benchmark-owned verifier files.
