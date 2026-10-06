# Repair `read_settings`

Fix `read_settings` in `config_reader.py`.

Each non-empty, non-comment line has the form `key: value`. Ignore malformed
lines and lines whose key or value is empty after trimming. Strip whitespace
from keys and values, retain colons that occur inside a value, and let the
last occurrence of a key win. Keep the public function signature unchanged.
