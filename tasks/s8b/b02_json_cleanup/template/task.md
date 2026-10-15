# Repair transform

## Recursive JSON-like value cleanup

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input may be a JSON-like null, boolean, number, string, list, or dictionary; preserve non-string scalar values.
- Trim whitespace from every string value and dictionary key.
- Recursively clean lists while preserving order and retaining null list elements.
- Recursively clean dictionaries and remove entries whose original value is null; do not mutate input.

Do not modify benchmark-owned verifier files.
