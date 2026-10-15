# Repair transform

## Version component normalization

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a string containing one to three dot-separated ASCII non-negative integers; otherwise return None.
- Trim surrounding whitespace and accept one optional lowercase v prefix.
- Reject empty components, signs, suffixes, non-ASCII digits, and more than three components.
- Return a three-integer tuple and pad missing components with zero; leading zeroes are allowed.

Do not modify benchmark-owned verifier files.
