Fixed `topological_order` to return dependency-first ordering, choose lexically among ready nodes, include dependency-only nodes, and raise `ValueError` for cycles. The public signature is unchanged, and input is not mutated.

Added regression coverage. Verification: `python3 -m unittest -v` — all 7 tests passed.