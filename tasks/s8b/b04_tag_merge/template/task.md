# Repair transform

## Ordered tag-list consolidation

Implement def transform(value) in solution.py. Its public signature must remain unchanged.

Requirements:
- Input is a list of tag-list values; ignore non-list groups and non-string tags.
- Visit groups and tags in input order, trim each tag, and lowercase it.
- Drop blank normalized tags and preserve the first occurrence of each normalized tag.
- Return a new flat list without modifying the input lists.

Do not modify benchmark-owned verifier files.
