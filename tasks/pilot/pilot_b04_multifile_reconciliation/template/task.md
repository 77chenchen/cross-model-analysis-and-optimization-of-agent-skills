# Repair `reconcile`

Fix `reconcile` in `reconcile.py`. Given `expected` and `actual` dictionaries
of id to integer count, return a dictionary of ids whose counts differ, mapped
to `{"expected": E, "actual": A}`. Missing counts are zero. Sort keys by id
in the returned insertion order and reject non-integer counts with `ValueError`.
