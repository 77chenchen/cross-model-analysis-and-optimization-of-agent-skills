def dedupe_records(records: list[dict]) -> list[dict]:
    by_id = {}
    for record in records:
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier:
            continue
        if identifier not in by_id or record["updated_at"] > by_id[identifier]["updated_at"]:
            by_id[identifier] = record
    return list(by_id.values())
