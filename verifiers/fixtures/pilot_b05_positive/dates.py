from datetime import date
import re
def valid_dates(values):
 out=[]
 for x in values:
  if isinstance(x,str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}',x):
   try:date.fromisoformat(x);out.append(x)
   except ValueError:pass
 return out
