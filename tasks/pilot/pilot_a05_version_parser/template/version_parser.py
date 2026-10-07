def parse_version(value):
    parts = value.split('.')
    return tuple(int(part) for part in parts)
