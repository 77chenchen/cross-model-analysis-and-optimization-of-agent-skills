# Repair `normalize_event`

Fix `normalize_event` in `event_normalizer.py`. Given one event mapping,
return a new mapping with exactly `event`, `user_id`, and `tags`: trim and
lowercase `event`; trim `user_id`; turn a comma-separated string or list of
strings into a list of unique, lowercased, trimmed non-empty tags in first
appearance order. Return `None` if `event` or `user_id` is missing or blank.
Do not mutate input values.
