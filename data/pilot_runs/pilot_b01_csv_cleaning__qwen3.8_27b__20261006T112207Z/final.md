

Done. `clean_rows` in `csv_cleaner.py` now implements everything `task.md` requires:

**Fixes applied:**
- **`name`**: trimmed, and rows with an empty/whitespace-only (or missing/non-string) name are discarded
- **`email`**: trimmed and lowercased; empty after trim is discarded
- **`score`**: parsed with `int(score.strip())`; rows where it isn't a valid integer (`"abc"`, `"3.5"`, missing) are discarded
- **Output**: each accepted row is a **new** dict containing exactly `name`, `email`, `score` (extra input keys dropped) — caller dicts are never mutated
- **Order**: accepted rows keep their input order
- Accepts any iterable (lists, generators, etc.)

**Validation** (via a throwaway script in `/tmp`, no benchmark files touched) — all checks passed:
- normalization + trimming/lowercasing (e.g. `"  ADA@example.COM "` → `"ada@example.com"`, `" 42 "` → `42`)
- discard rules: empty name, empty email, non-integer score
- integer edge cases: `-5`, `0`, `+9` accepted; `3.5` rejected
- no mutation of caller's dicts (deep-equal snapshot check)
- exact key set and `int` score type on every output dict
- order preservation and generator input

No benchmark-owned verifier files were created or modified.