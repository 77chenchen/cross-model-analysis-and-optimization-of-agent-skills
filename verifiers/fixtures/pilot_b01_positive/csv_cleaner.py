def clean_rows(rows):
    cleaned = []
    for row in rows:
        name = str(row.get("name", "")).strip()
        email = str(row.get("email", "")).strip().lower()
        try:
            score = int(row.get("score", ""))
        except (TypeError, ValueError):
            continue
        if name and email:
            cleaned.append({"name": name, "email": email, "score": score})
    return cleaned
