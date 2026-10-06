def read_settings(text: str) -> dict[str, str]:
    settings = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        if key and value:
            settings[key] = value
    return settings
