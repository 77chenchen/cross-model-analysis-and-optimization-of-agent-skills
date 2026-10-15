# Repair transform

## Phone number normalization

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a string; otherwise return None.
- Only digits and formatting characters space, hyphen, period, parentheses, and plus are allowed; any other character invalidates the input.
- After removing formatting, accept ten digits or eleven digits beginning with country digit 1 and remove that leading 1.
- Return the ten-digit local number as a string; all other lengths return None.

Do not modify benchmark-owned verifier files.
