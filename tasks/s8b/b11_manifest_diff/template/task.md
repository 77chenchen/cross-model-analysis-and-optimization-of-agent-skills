# Repair transform

## File manifest comparison

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a dictionary with before and after lists; invalid top-level input returns empty added, removed, and changed lists.
- A valid entry has a non-empty string path, non-negative integer size that is not boolean, and non-empty string sha256; ignore invalid entries.
- For duplicate paths, the last valid entry wins.
- Added means only after, removed means only before, and changed means present in both with size or sha256 different; return lexicographically sorted lists.

Do not modify benchmark-owned verifier files.
