def clean_rows(rows):
    """Normalize selected CSV-style records."""
    cleaned = []
    for row in rows:
        if row.get("name") and row.get("email") and row.get("score"):
            cleaned.append({"name": row["name"], "email": row["email"], "score": row["score"]})
    return cleaned
