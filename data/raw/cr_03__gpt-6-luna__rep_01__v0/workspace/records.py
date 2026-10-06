from numbers import Real


def dedupe_records(records: list[dict]) -> list[dict]:
    by_id = {}
    for record in records:
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier:
            continue

        current = by_id.get(identifier)
        updated_at = record.get("updated_at")
        current_updated_at = current.get("updated_at") if current is not None else None
        timestamp_is_numeric = isinstance(updated_at, Real) and not isinstance(updated_at, bool)
        current_timestamp_is_numeric = (
            isinstance(current_updated_at, Real) and not isinstance(current_updated_at, bool)
        )

        # Replace only when this record has a strictly newer numeric timestamp.
        # Dict insertion order then continues to reflect each ID's first appearance.
        if current is None or (
            timestamp_is_numeric
            and (not current_timestamp_is_numeric or updated_at > current_updated_at)
        ):
            by_id[identifier] = record
    return list(by_id.values())
