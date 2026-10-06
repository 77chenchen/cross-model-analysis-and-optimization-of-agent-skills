def normalize_event(event):
    if not isinstance(event, dict):
        return None
    name, user = event.get("event"), event.get("user_id")
    if not isinstance(name, str) or not isinstance(user, str):
        return None
    name, user = name.strip().lower(), user.strip()
    if not name or not user:
        return None
    raw = event.get("tags", [])
    raw = raw.split(",") if isinstance(raw, str) else raw
    if not isinstance(raw, list):
        raw = []
    tags = []
    for tag in raw:
        if isinstance(tag, str) and (clean := tag.strip().lower()) and clean not in tags:
            tags.append(clean)
    return {"event": name, "user_id": user, "tags": tags}
