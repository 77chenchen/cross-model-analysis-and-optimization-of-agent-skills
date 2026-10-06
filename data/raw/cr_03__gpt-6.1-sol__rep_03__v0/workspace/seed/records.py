def dedupe_records(records: list[dict]) -> list[dict]:
    by_id = {}
    for record in records:
        identifier = record.get("id")
        if identifier:
            by_id[identifier] = record
    return list(by_id.values())
