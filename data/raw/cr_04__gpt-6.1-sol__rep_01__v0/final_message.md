Fixed `topological_order` to return dependency-first order, choose lexically at every step, include dependency-only nodes, and raise `ValueError` for cycles. The public signature and input remain unchanged.

Added regression coverage. All 7 tests pass with `python3 -m unittest -v`; `git diff --check` also passes.