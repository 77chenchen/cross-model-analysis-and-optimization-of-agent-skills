# Task: repair `parse_config`

Fix `parse_config` in `config_parser.py`.

The function reads `key=value` lines. It must trim keys and values, ignore blank lines and full-line comments, remove inline comments beginning with `#` only when the `#` is preceded by whitespace, and preserve `#` that is part of a value. Ignore lines without a non-empty key and value. Keep the public signature unchanged and run the tests.
