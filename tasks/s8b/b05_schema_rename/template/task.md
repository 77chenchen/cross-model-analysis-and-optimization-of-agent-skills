# Repair transform

## Legacy contact schema conversion

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a dictionary; otherwise return defaults with name, email, and phone set to empty strings.
- Output always has exactly the keys name, email, and phone.
- Prefer each new key over its legacy alias: full_name, email_address, and phone_number.
- Trim selected string values; use the empty-string default for missing or non-string selected values; ignore unknown keys and do not mutate input.

Do not modify benchmark-owned verifier files.
