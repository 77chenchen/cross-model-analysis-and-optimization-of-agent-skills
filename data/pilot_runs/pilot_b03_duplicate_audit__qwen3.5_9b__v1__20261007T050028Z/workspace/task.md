# Repair `duplicate_ids`

Fix `duplicate_ids` in `audit.py`. From iterable records, return a sorted list
of normalized string IDs that occur more than once. Normalize by trimming and
lowercasing; ignore missing, blank, and non-string IDs.
