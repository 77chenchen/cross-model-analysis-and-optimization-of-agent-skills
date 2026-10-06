# Repair `clean_rows`

Fix `clean_rows` in `csv_cleaner.py`. The function receives an iterable of
row dictionaries. Return new dictionaries containing exactly `name`, `email`,
and `score`: trim `name` and lowercase/trim `email`; parse `score` as an
integer; discard rows with an empty name/email or a non-integer score. Do not
mutate the caller's dictionaries, and preserve the order of accepted rows.
