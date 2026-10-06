Implemented `topological_order` to include dependency-only nodes, emit dependencies before dependents, choose the lexical first available node, and raise `ValueError` on cycles without mutating the input.

Verification: `python3 -m unittest -v` passed all 3 tests.