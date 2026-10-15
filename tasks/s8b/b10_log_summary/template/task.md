# Repair transform

## Log level summary

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a list; other input returns all five recognized levels with zero counts.
- An entry is either a string whose first whitespace-delimited token is its level, or a dictionary with a string level field.
- Recognize DEBUG, INFO, WARNING, ERROR, and CRITICAL case-insensitively after trimming; ignore unknown or malformed entries.
- Return all five keys, including zero counts, in fixed order DEBUG, INFO, WARNING, ERROR, CRITICAL.

Do not modify benchmark-owned verifier files.
