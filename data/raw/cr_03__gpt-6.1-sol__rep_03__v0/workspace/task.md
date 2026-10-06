# Task: repair `dedupe_records`

Fix `dedupe_records` in `records.py`. Given a list of dictionaries, return one record per non-empty string `id`, retaining the record with the greatest numeric `updated_at`. If timestamps are tied, retain the earlier input record. Ignore records with a missing, empty, or non-string `id`, and do not mutate input records. Keep the public signature unchanged and run the tests.
