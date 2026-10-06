def clean_rows(rows):
    return [{"name": row["name"].strip(), "email": row["email"].strip().lower(), "score": int(row["score"])} for row in rows]
