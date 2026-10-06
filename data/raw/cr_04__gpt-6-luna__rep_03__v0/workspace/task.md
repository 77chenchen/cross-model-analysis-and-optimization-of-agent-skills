# Task: repair `topological_order`

Fix `topological_order` in `dependencies.py`. It receives a mapping of node names to direct dependency names and must return a deterministic dependency-first ordering. Nodes referenced only as dependencies must be included. At every choice, use lexical ordering. Raise `ValueError` for cycles. Do not mutate the input and keep the public signature unchanged. Run the tests.
