# Repair transform

## Unicode text slug construction

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a string; other inputs return the empty string.
- Lowercase the text and retain Unicode alphanumeric characters.
- Replace each maximal run of non-alphanumeric characters with one hyphen and remove boundary hyphens.
- If no alphanumeric characters remain, return the empty string.

Do not modify benchmark-owned verifier files.
