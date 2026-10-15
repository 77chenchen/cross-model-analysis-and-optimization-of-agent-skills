# Repair transform

## Event filtering with inclusive date bounds

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a dictionary with events (list), allowed_types (list), start_date, and end_date; malformed top-level input returns [].
- Boundaries must be valid Gregorian dates exactly in YYYY-MM-DD form and start_date must be no later than end_date; otherwise return [].
- Keep dictionary events with an exact allowed type and valid YYYY-MM-DD date inside the inclusive range.
- Ignore malformed events and preserve original order and values.

Do not modify benchmark-owned verifier files.
