# Repair transform

## CSV-style category amount aggregation

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a list; each accepted row is a list or tuple of at least two cells: category and amount.
- Category must be a non-empty trimmed string; amount may be finite int, float, or decimal string, but not boolean.
- Ignore malformed rows, invalid categories, and invalid or non-finite amounts.
- Sum by trimmed category and return float totals; dictionary keys retain first-seen category order.

Do not modify benchmark-owned verifier files.
