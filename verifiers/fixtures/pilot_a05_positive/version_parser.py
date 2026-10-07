import re
def parse_version(value):
 m=re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([A-Za-z0-9]+))?',value)
 if not m: raise ValueError('invalid version')
 return int(m[1]),int(m[2]),int(m[3]),m[4]
