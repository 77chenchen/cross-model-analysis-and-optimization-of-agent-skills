# Repair transform

## Header name canonicalization

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a string; other inputs return the empty string.
- Lowercase the text and treat only ASCII letters and digits as word characters.
- Replace each maximal run of punctuation, whitespace, or non-ASCII characters with one underscore.
- Remove leading and trailing underscores; punctuation-only input becomes the empty string.

Do not modify benchmark-owned verifier files.
