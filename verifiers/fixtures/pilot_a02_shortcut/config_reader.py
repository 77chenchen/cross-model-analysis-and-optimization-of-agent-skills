def read_settings(text: str) -> dict[str, str]:
    return {key.strip(): value.strip() for key, value in (line.split(":", 1) for line in text.splitlines() if ":" in line)}
