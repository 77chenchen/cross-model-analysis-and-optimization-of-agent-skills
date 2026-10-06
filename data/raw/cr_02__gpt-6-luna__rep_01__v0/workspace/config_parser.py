def parse_config(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        # An inline comment starts at a hash preceded by whitespace.
        for index, char in enumerate(value):
            if char == "#" and index > 0 and value[index - 1].isspace():
                value = value[:index].rstrip()
                break
        if key and value:
            result[key] = value
    return result
