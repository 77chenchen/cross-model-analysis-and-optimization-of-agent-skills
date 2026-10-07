def deduplicate_records(records):
    """Keep one record for each identifier (case-insensitive, trimmed)."""

    seen_ids_lower = set()
    result = []

    for r in records:
        if "id" not in r or isinstance(r["id"], type(None)):
            continue
        
        trimmed_id = r["id"].strip()
        if len(trimmed_id) == 0:
            continue
        lower_trimmed = trimmed_id.lower()

        if lower_trimmed not in seen_ids_lower:
            seen_ids_lower.add(lower_trimmed)
            result.append(r)
    
    return result
