def normalize_event(event):
    if not event.get("event") or not event.get("user_id"):
        return None
    tags = event.get("tags", [])
    return {"event": event["event"].strip().lower(), "user_id": event["user_id"].strip(), "tags": list(dict.fromkeys(tags))}
