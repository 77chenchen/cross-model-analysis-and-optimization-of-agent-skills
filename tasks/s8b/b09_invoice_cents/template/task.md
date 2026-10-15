# Repair transform

## Invoice amount conversion to cents

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a list of amounts; other input returns 0.
- Accept strings or integers that represent non-negative decimal amounts; skip booleans, floats, invalid strings, and negative values.
- Parse exactly and round each accepted amount half-up to the nearest cent before summing; return integer cents.
- Allow leading plus and surrounding whitespace; reject currency symbols and exponent notation.

Do not modify benchmark-owned verifier files.
