def parse_version(value):
    """Parse a version string into (major, minor, patch, suffix_or_none)."""
    import re
    
    stripped = value.strip()
    
    if not stripped:  # reject empty or whitespace-only strings
        raise ValueError(f"Invalid version {value!r}")

