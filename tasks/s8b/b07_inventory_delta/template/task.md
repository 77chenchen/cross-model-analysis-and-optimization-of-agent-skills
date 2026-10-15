# Repair transform

## Inventory delta reconciliation

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a dictionary with stock (mapping non-empty string item names to non-negative integers) and deltas (list); invalid top-level input or stock returns None.
- Booleans are not integers.
- Apply valid two-item list or tuple pairs [item, integer_delta] sequentially; ignore malformed pairs, invalid names, and non-integer deltas.
- New items start at zero. If any applied delta makes stock negative, return None for the whole operation; else return a new mapping preserving initial order and appending new items in first-use order.

Do not modify benchmark-owned verifier files.
