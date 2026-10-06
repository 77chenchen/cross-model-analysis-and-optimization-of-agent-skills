def deduplicate_records(records):
    seen, result = set(), []
    for record in records:
        if not isinstance(record, dict):
            continue
        raw_id = record.get("id")
        if not isinstance(raw_id, str) or not raw_id.strip():
            continue
        key = raw_id.strip().lower()
        if key not in seen:
            seen.add(key)
            result.append(dict(record))
    return result
