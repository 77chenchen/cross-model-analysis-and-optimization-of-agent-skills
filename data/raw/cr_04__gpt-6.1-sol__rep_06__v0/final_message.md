Fixed `topological_order` to return dependency-first ordering with lexical tie-breaking, include dependency-only nodes, and raise `ValueError` for cycles. The public signature and input remain unchanged.

Added regression coverage. Verification: `python3 -m unittest -v` — all 7 tests passed.