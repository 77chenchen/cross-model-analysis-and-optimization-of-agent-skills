# Repair `dependency_order`

Fix `dependency_order` in `dependency_order.py`. Given a mapping from node to
an iterable of prerequisite nodes, return a deterministic topological order:
prerequisites precede dependents and tied ready nodes are alphabetical. Include
prerequisites that appear only as values. Raise `ValueError` for a cycle.
