def parse_config(text: str) -> dict[str, str]:
    result = {}
    for line in text.splitlines():
        line = line.strip()
        for index, char in enumerate(line):
            if char == "#" and index > 0 and line[index - 1].isspace():
                line = line[:index]
                break
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key and value:
            result[key] = value
    return result
