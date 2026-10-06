

All fixed and validated. Here's what was wrong and what I changed in `parse_labels`:

**Bugs fixed in `label_parser.py`:**
1. **`item.split("=")`** → **`item.split("=", 1)`** — the old code crashed on values containing `=` (e.g. `url=https://x.com?a=1`) because unpacking 3+ parts into 2 variables raises `ValueError`. Splitting on the first `=` only preserves extra `=` characters in the value.
2. **Added `.strip()`** on both key and value — trimming wasn't done at all before.
3. **Added empty checks** — entries with an empty key or empty value (after trimming) are now ignored, per the spec.

The public signature `def parse_labels(text: str) -> dict[str, str]` is unchanged.

**Validation** — 15 test cases, all passing:
- Basic pairs: `"a=1; b=2"` → `{"a": "1", "b": "2"}`
- Trimming: `" a = 1 ; b= 2 "` → `{"a": "1", "b": "2"}`
- Values with `=` preserved: `"kv=a=b=c"` → `{"kv": "a=b=c"}`, `"url=https://x.com?a=1&b=2"` intact
- No-`=` entries ignored: `"a=1; garbage; b=2"` → `{"a": "1", "b": "2"}`
- Empty key ignored: `"=value; a=1"` → `{"a": "1"}` (incl. whitespace-only keys)
- Empty value ignored: `"a=; b=2"` → `{"b": "2"}` (incl. whitespace-only values)
- Edge cases: empty/whitespace-only input → `{}`, duplicate keys (last wins), `"k=="` → `{"k": "="}` (the value is literally `=`)

I did not touch any verifier files (none are present in this workspace — only `label_parser.py`, `task.md`, and a stale `__pycache__`).