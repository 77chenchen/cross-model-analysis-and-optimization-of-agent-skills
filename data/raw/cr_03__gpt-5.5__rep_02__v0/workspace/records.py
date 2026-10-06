def dedupe_records(records: list[dict]) -> list[dict]:
    by_id = {}
    timestamps = {}
    for record in records:
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier:
            continue

        updated_at = record.get("updated_at")
        is_numeric_timestamp = isinstance(updated_at, (int, float)) and not isinstance(updated_at, bool)

        if identifier not in by_id:
            by_id[identifier] = record
            timestamps[identifier] = updated_at if is_numeric_timestamp else None
            continue

        current_timestamp = timestamps[identifier]
        if is_numeric_timestamp and (current_timestamp is None or updated_at > current_timestamp):
            by_id[identifier] = record
            timestamps[identifier] = updated_at

    return list(by_id.values())
