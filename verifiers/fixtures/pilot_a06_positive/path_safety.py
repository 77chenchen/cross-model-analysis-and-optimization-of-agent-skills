from pathlib import Path
def safe_child(base,candidate):
 b=Path(base).resolve();c=Path(candidate)
 if c.is_absolute():raise ValueError('absolute')
 target=(b/c).resolve()
 try:target.relative_to(b)
 except ValueError:raise ValueError('outside')
 return target
