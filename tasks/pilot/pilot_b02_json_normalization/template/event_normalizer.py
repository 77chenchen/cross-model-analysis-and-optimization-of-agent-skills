def normalize_event(event):
    """Normalize a small analytics event."""
    if not event.get("event") or not event.get("user_id"):
        return None
    return {"event": event["event"], "user_id": event["user_id"], "tags": event.get("tags", [])}
