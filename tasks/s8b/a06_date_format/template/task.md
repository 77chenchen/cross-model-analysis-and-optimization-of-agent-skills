# Repair transform

## Calendar date normalization

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is exactly a string in YYYY-MM-DD or YYYY/MM/DD form using ASCII digits; otherwise return None.
- The two separators must match.
- Validate the Gregorian calendar date, including leap years.
- Return a valid date in YYYY-MM-DD form with zero-padded fields.

Do not modify benchmark-owned verifier files.
