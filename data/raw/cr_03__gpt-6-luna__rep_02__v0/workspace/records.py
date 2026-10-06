from numbers import Real


def dedupe_records(records: list[dict]) -> list[dict]:
    by_id = {}
    for record in records:
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier:
            continue

        timestamp = record.get("updated_at")
        numeric_timestamp = isinstance(timestamp, Real) and not isinstance(timestamp, bool)
        current = by_id.get(identifier)
        if current is None:
            by_id[identifier] = record
            continue

        current_timestamp = current.get("updated_at")
        current_numeric = isinstance(current_timestamp, Real) and not isinstance(current_timestamp, bool)
        if numeric_timestamp and (
            not current_numeric or timestamp > current_timestamp
        ):
            by_id[identifier] = record
    return list(by_id.values())
