from numbers import Real


def dedupe_records(records: list[dict]) -> list[dict]:
    by_id = {}
    for record in records:
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier:
            continue

        timestamp = record.get("updated_at")
        if isinstance(timestamp, bool) or not isinstance(timestamp, Real):
            timestamp = None

        if identifier not in by_id:
            by_id[identifier] = (record, timestamp)
            continue

        current_record, current_timestamp = by_id[identifier]
        if timestamp is not None and (current_timestamp is None or timestamp > current_timestamp):
            by_id[identifier] = (record, timestamp)
    return [record for record, _ in by_id.values()]
