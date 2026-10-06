def parse_labels(text: str) -> dict[str, str]:
    """Parse semicolon-separated key=value labels into a dictionary."""
    labels = {}
    for item in text.split(";"):
        if "=" not in item:
            continue
        parts = item.split("=", 1)
        key = parts[0].strip()
        value = parts[1].strip()
        if key and value:
            labels[key] = value
    return labels
