# Repair transform

## Duration text to seconds

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a string; otherwise return None.
- Empty or whitespace-only input means zero seconds.
- Each whitespace-separated token must contain ASCII digits followed by exactly one lowercase unit s, m, h, or d.
- Use factors 1, 60, 3600, and 86400 and sum repeated units.
- If any token is malformed, signed, negative, or uses another unit, return None for the whole input.

Do not modify benchmark-owned verifier files.
