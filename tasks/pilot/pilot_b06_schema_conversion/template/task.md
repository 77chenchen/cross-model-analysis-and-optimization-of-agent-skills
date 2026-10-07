# Repair `to_rows`

Fix `to_rows` in `schema_conversion.py`. Convert a mapping of column name to
equal-length value lists into a list of row dictionaries. Preserve the input
mapping's key order. Return `[]` for an empty mapping; raise `ValueError` when
any value is not a list or column lengths differ.
