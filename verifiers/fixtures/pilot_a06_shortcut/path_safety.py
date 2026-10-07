from pathlib import Path
def safe_child(base,candidate):
 target=(Path(base)/candidate).resolve()
 if str(target).startswith(str(Path(base).resolve())):return target
 raise ValueError('outside')
