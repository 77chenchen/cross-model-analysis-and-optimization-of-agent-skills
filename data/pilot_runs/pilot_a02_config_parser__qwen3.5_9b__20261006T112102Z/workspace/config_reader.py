def read_settings(text: str) -> dict[str, str]:
    """Read a small colon-delimited settings file."""
    settings = {}
    for line in text.splitlines():
        if line.startswith("#") or not line:
            continue
        if ":" in line:
            key, value = line.split(":")
            settings[key] = value
    return settings
