# Repair transform

## Record de-duplication

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a dictionary containing records (a list) and key (a non-empty string); invalid input returns [].
- Ignore non-dictionary records, records missing the key field, and records whose key value is None or unhashable.
- Keep the first occurrence position for each identifier but use a shallow copy of its last valid record.
- Return a new list and do not modify the input list or its records.

Do not modify benchmark-owned verifier files.
