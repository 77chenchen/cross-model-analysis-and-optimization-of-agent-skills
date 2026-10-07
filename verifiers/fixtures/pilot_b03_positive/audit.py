def duplicate_ids(records):
 counts={}
 for r in records:
  x=r.get('id') if isinstance(r,dict) else None
  if isinstance(x,str) and (x:=x.strip().lower()):counts[x]=counts.get(x,0)+1
 return sorted(x for x,n in counts.items() if n>1)
