# Repair `parse_version`

Fix `parse_version` in `version_parser.py`. Accept only versions shaped
`MAJOR.MINOR.PATCH` with non-negative decimal integers and optional `-suffix`.
Return `(major, minor, patch, suffix_or_none)`. Reject leading `v`, missing
parts, extra dots, empty suffixes, and leading zeroes except the literal `0`
by raising `ValueError`.
