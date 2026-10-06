Implemented `topological_order` in [dependencies.py](/Users/wangqichen/Documents/Codex/2026-10-06/zon/work/skill-trajectory-benchmark/data/raw/cr_04__gpt-5.5__rep_04__v0/workspace/dependencies.py:1).

It now:
- includes dependency-only nodes
- returns dependency-first order
- chooses lexically whenever multiple nodes are available
- detects cycles with `ValueError`
- leaves the input graph untouched

Verification: `python3 -m unittest -v` passed all 3 tests. I also ran small spot checks for non-mutation, dependency-only ordering, self-cycles, and longer cycles.