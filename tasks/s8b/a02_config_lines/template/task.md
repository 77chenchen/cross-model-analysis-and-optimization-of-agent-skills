# Repair transform

## Line-oriented configuration parsing

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a string; otherwise return {}.
- Split on actual line breaks, trim each line, and ignore blank lines and lines beginning with # after trimming.
- Split remaining lines at the first colon, trim both fields, and skip malformed lines and empty keys or values.
- The last valid value wins for repeated keys; a blank later value does not erase an earlier valid value.

Do not modify benchmark-owned verifier files.
