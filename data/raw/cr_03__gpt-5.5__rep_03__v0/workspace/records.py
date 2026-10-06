def dedupe_records(records: list[dict]) -> list[dict]:
    by_id = {}
    timestamps = {}
    for record in records:
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier:
            continue

        updated_at = record.get("updated_at")
        if not isinstance(updated_at, (int, float)):
            updated_at = float("-inf")

        if identifier not in by_id or updated_at > timestamps[identifier]:
            by_id[identifier] = record
            timestamps[identifier] = updated_at
    return list(by_id.values())
