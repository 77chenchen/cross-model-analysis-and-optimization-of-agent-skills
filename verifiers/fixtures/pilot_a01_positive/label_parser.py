def parse_labels(text: str) -> dict[str, str]:
    labels = {}
    for item in text.split(";"):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        key, value = key.strip(), value.strip()
        if key and value:
            labels[key] = value
    return labels
