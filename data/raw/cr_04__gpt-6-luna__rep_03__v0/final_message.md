Implemented `topological_order` with dependency-first ordering, lexical tie-breaking via a min-heap, inclusion of dependency-only nodes, and cycle detection. It does not mutate the input.

Verification: `python3 -m unittest -v` passed all 3 tests. `python` was unavailable, so I ran the suite with `python3`.