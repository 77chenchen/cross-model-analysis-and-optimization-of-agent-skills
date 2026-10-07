# Repair `safe_child`

Fix `safe_child` in `path_safety.py`. Given a base directory and a candidate
relative path, return the resolved candidate `Path` only if it remains inside
the resolved base. Reject absolute paths and traversal outside the base with
`ValueError`. A sibling such as `base-other` is outside the base.
