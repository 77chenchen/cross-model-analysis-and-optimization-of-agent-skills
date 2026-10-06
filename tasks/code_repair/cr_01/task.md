# Task: repair `parse_labels`

The function `parse_labels` in `label_parser.py` parses semicolon-separated `key=value` labels.

Fix its behavior so that it:

1. trims surrounding whitespace from keys and values;
2. preserves additional `=` characters in values;
3. ignores malformed entries with no `=`, an empty key, or an empty value;
4. preserves the existing public function signature.

Do not modify the tests. Run the test suite before finishing.
