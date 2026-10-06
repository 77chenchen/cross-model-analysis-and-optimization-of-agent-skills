def parse_labels(text: str) -> dict[str, str]:
    labels = {}
    for item in text.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            labels[key.strip()] = value.strip()
    return labels
