# Repair transform

## Safe relative path normalization

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a string; otherwise return None.
- Reject paths beginning with slash and any path containing a segment exactly equal to two dots.
- Split on slash, remove empty and single-dot segments, and preserve remaining segment text and order.
- Join remaining segments with slash; empty and dot-only relative paths become the empty string.

Do not modify benchmark-owned verifier files.
