Fixed `topological_order` to choose the lexically first available node, include dependency-only nodes, and raise `ValueError` for cycles. The public signature and input remain unchanged.

Added regression coverage. Verification: `python3 -m unittest -v` — all 7 tests passed.