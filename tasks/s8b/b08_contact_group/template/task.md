# Repair transform

## Contact grouping by normalized email domain

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a list of contact dictionaries; other input returns {}.
- A usable contact has a non-empty string name and an email with exactly one @, a non-empty local part, and a dotted domain of non-empty ASCII alphanumeric/hyphen labels that do not start or end with a hyphen.
- Trim name and email, lowercase the domain for the output key, and preserve contact order within each domain.
- Skip invalid contacts and return domain keys mapped to lists of trimmed names; groups retain first-seen order.

Do not modify benchmark-owned verifier files.
