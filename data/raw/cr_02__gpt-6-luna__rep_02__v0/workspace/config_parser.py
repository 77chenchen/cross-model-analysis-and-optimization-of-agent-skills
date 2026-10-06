def parse_config(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        for index, char in enumerate(value):
            if char == "#" and index > 0 and value[index - 1].isspace():
                value = value[:index]
                break
        value = value.strip()
        if not key or not value:
            continue
        result[key] = value
    return result
