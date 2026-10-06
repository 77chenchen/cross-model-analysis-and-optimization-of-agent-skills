The `parse_labels` function in `label_parser.py` was updated to correctly handle semicolon-separated `key=value` entries by:
1.  Trimming whitespace from both keys and values using `.strip()`.
2.  Using `.split("=", 1)` to ensure that any additional `=` characters within the value are preserved.
3.  Ignoring entries where the key or the value is empty after trimming.

I have also verified the fix with a test suite covering various scenarios, including extra whitespace, multiple equals signs, and invalid/empty entries.

```python
def parse_labels(text: str) -> dict[str, str]:
    """Parse semicolon-separated key=value labels into a dictionary."""
    labels = {}
    for item in text.split(";"):
        if "=" not in item:
            continue
        parts = item.split("=", 1)
        key = parts[0].strip()
        value = parts[1].strip()
        if key and value:
            labels[key] = value
    return labels
```