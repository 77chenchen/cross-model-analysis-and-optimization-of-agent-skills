Implemented `topological_order` in [dependencies.py](/Users/wangqichen/Documents/Codex/2026-10-06/zon/work/skill-trajectory-benchmark/data/raw/cr_04__gpt-5.5__rep_05__v0/workspace/dependencies.py:1).

It now:
- returns dependency-first topological order
- includes dependency-only nodes
- uses lexical ordering whenever multiple nodes are available
- raises `ValueError` on cycles
- avoids mutating the input graph

Verification:
- `python3 -m unittest -v` passed: 3 tests OK
- Manual checks passed for dependency-only nodes, input preservation, and self-cycle rejection.