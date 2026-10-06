def parse_config(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        for index, char in enumerate(line):
            if char == "#" and index > 0 and line[index - 1].isspace():
                line = line[:index]
                break

        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            continue
        result[key] = value
    return result
