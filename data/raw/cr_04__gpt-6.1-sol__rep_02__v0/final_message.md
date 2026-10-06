Fixed `topological_order` to include dependency-only nodes, choose lexically among eligible nodes, and raise `ValueError` for cycles. The public signature is unchanged, and the input is preserved.

Added regression coverage. Verification: `python3 -m unittest -v` — all 7 tests passed.