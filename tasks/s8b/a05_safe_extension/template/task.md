# Repair transform

## Safe filename extension extraction

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a string; otherwise return None.
- Use the last slash-separated path component as the filename.
- Return the lowercase suffix after the final dot, without the dot.
- No dot, a trailing dot, or a single-leading-dot file such as .env has no extension; .config.json has extension json.

Do not modify benchmark-owned verifier files.
