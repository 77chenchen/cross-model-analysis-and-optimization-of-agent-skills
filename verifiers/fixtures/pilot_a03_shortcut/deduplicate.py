def deduplicate_records(records):
    seen, result = set(), []
    for record in records:
        if isinstance(record, dict) and record.get("id") not in seen:
            seen.add(record.get("id"))
            result.append(dict(record))
    return result
