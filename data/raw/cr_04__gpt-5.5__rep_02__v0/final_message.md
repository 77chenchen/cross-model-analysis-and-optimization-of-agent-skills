Implemented the fix in [dependencies.py](/Users/wangqichen/Documents/Codex/2026-10-06/zon/work/skill-trajectory-benchmark/data/raw/cr_04__gpt-5.5__rep_02__v0/workspace/dependencies.py:1).

`topological_order` now:
- returns dependency-first order
- includes dependency-only nodes
- uses lexical ordering for ready nodes
- detects cycles with `ValueError`
- avoids mutating the input

Verification passed:

```text
python3 -m unittest -v
Ran 3 tests in 0.000s
OK
```