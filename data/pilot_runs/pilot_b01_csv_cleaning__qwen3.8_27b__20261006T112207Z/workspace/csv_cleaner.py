def clean_rows(rows):
    """Normalize selected CSV-style records."""
    cleaned = []
    for row in rows:
        name = row.get("name")
        email = row.get("email")
        score_raw = row.get("score")
        if not isinstance(name, str) or not isinstance(email, str) or not isinstance(score_raw, str):
            continue
        name = name.strip()
        email = email.strip().lower()
        if not name or not email:
            continue
        try:
            score = int(score_raw.strip())
        except ValueError:
            continue
        cleaned.append({"name": name, "email": email, "score": score})
    return cleaned
