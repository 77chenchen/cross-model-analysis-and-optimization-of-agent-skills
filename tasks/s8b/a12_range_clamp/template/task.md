# Repair transform

## Bounded integer coercion

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a dictionary with value, min, and max; malformed input returns None.
- value is an integer or a base-10 integer string with optional whitespace and sign; booleans, floats, and other values are invalid.
- min and max are integers but not booleans, and min must not exceed max.
- Return the parsed value clamped to the inclusive bounds.

Do not modify benchmark-owned verifier files.
