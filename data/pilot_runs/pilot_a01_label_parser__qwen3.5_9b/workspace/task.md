# Repair `parse_labels`

Fix `parse_labels` in `label_parser.py`.

The input contains semicolon-separated `key=value` entries. Trim keys and values, preserve additional `=` characters in a value, and ignore entries with no `=`, an empty key, or an empty value. Preserve the public function signature.
