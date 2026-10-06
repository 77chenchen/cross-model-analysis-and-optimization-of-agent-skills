def parse_labels(text: str) -> dict[str, str]:
    """Parse semicolon-separated key=value labels into a dictionary."""
    labels = {}
    for item in text.split(";"):
        if "=" not in item:
            continue
        key, value = item.split("=")
        labels[key] = value
    return labels
