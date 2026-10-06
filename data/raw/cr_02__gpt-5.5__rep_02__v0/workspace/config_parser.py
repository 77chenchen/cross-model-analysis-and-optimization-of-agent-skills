def parse_config(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        comment_start = None
        for index, char in enumerate(value):
            if char == "#" and index > 0 and value[index - 1].isspace():
                comment_start = index
                break
        if comment_start is not None:
            value = value[:comment_start]
        key = key.strip()
        value = value.strip()
        if not key or not value:
            continue
        result[key] = value
    return result
