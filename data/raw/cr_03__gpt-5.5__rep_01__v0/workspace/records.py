from numbers import Real


def _numeric_updated_at(record: dict):
    value = record.get("updated_at")
    if isinstance(value, bool) or not isinstance(value, Real):
        return None
    return value


def dedupe_records(records: list[dict]) -> list[dict]:
    by_id = {}
    for record in records:
        identifier = record.get("id")
        if not isinstance(identifier, str) or identifier == "":
            continue

        current = by_id.get(identifier)
        if current is None:
            by_id[identifier] = record
            continue

        updated_at = _numeric_updated_at(record)
        current_updated_at = _numeric_updated_at(current)
        if updated_at is not None and (
            current_updated_at is None or updated_at > current_updated_at
        ):
            by_id[identifier] = record
    return list(by_id.values())
