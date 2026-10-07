from pathlib import Path
def safe_child(base, candidate):
    return Path(base) / candidate
