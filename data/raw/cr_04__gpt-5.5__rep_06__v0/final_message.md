Implemented `topological_order` in [dependencies.py](/Users/wangqichen/Documents/Codex/2026-10-06/zon/work/skill-trajectory-benchmark/data/raw/cr_04__gpt-5.5__rep_06__v0/workspace/dependencies.py:1).

It now:
- includes nodes that appear only as dependencies
- returns dependency-first order with lexical tie-breaking
- raises `ValueError` on cycles
- avoids mutating the input graph

Verification:
- `python3 -m unittest -v` passes: 3 tests OK
- Extra manual check confirmed the input graph remains unchanged.