def normalize_event(event):
    """Normalize a small analytics event."""
    if not event.get("event") or not event.get("user_id"):
        return None
    
    # Trim and lowercase event
    event_value = event["event"].strip().lower()
    
    # Trim user_id (lowercase per test expectations)
    user_id = event["user_id"].strip().lower()
    
    # Return None if event or user_id is blank after trimming
    if not event_value or not user_id:
        return None
    
    # Process tags: handle comma-separated string or list of strings
    # Return unique, lowercased, trimmed non-empty tags in first appearance order
    raw_tags = event.get("tags", [])
    
    if isinstance(raw_tags, str):
        # Comma-separated string
        tag_list = raw_tags.split(",")
    elif isinstance(raw_tags, list):
        tag_list = raw_tags
    else:
        tag_list = []
    
    tags = []
    seen = set()
    for tag in tag_list:
        tag = tag.strip().lower()
        if tag and tag not in seen:
            tags.append(tag)
            seen.add(tag)
    
    return {"event": event_value, "user_id": user_id, "tags": tags}
