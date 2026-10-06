def parse_labels(text: str) -> dict[str, str]:
    """Parse semicolon-separated key=value labels into a dictionary."""
    labels = {}
    for item in text.split(";"):
        if "=" not in item:
            continue
        key, value = (part.strip() for part in item.split("=", 1))
        if not key or not value:
            continue
        labels[key] = value
    return labels
