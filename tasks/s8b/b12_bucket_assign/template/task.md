# Repair transform

## Inclusive numeric bucketing

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a dictionary with values and buckets lists; invalid top-level input returns [].
- A bucket must have a non-empty string name and finite numeric min/max bounds that are not booleans, with min <= max; ignore invalid buckets.
- For each finite numeric value other than a boolean, choose the first bucket whose inclusive interval contains it; return None for invalid or unmatched values.
- Preserve input order and output length; overlapping intervals use the first supplied valid bucket.

Do not modify benchmark-owned verifier files.
