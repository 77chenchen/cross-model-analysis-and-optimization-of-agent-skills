import re
def transform(r):
 o=r.get("op")
 if o=="slug": return re.sub(r"[^a-z0-9]+","-",r["text"].lower()).strip("-")
 if o=="clamp": return max(r["low"],min(r["high"],r["value"]))
 if o=="header":
  if ":" not in r["text"]: return None
  a,b=(x.strip() for x in r["text"].split(":",1)); return [a,b] if a and b else None
 if o=="extension":
  x=r["text"].rsplit(".",1); return x[1].lower() if len(x)==2 and x[0] and x[1] else ""
 if o=="duration":
  m=re.fullmatch(r"(\d+)([smh])",r["text"]); return int(m[1])*{"s":1,"m":60,"h":3600}[m[2]] if m else None
 if o=="enum": return r["mapping"].get(r["value"].strip().lower())
 if o=="tags":
  out=[]
  for x in r["text"].split(","):
   x=x.strip().lower()
   if x and x not in out: out.append(x)
  return out
 if o=="total": return sum(x.get("amount",0) for x in r["rows"] if type(x.get("amount")) is int)
 if o=="phone":
  x="".join(c for c in r["text"] if c.isdigit()); x=x if len(x)==10 else x[1:] if len(x)==11 and x[0]=="1" else ""; return "+1"+x if len(x)==10 else None
 if o=="cents":
  m=re.fullmatch(r"(\d+)(?:\.(\d{1,2}))?",r["text"]); return int(m[1])*100+int((m[2] if m[2] else "").ljust(2,"0")) if m else None
 if o=="bucket": return None if r["value"]<0 else "low" if r["value"]<10 else "medium" if r["value"]<100 else "high"
 if o=="difference": return sorted(set(x.strip().lower() for x in r["left"] if x.strip())-set(x.strip().lower() for x in r["right"] if x.strip()))
 if o=="inventory":
  d={}
  for x in r["rows"]: d[x["id"]]=d.get(x["id"],0)+x["count"]
  return sorted(k for k,v in d.items() if v<r["reorder"])
 if o=="sessions":
  d={}
  for x in r["events"]: d.setdefault(x["user"],set()).add(x["action"])
  return sorted(k for k,v in d.items() if {"login","purchase"}<=v)
 if o=="consolidate":
  d={}
  for x in r["rows"]:
   y=d.setdefault(x["id"],{"id":x["id"],"n":0,"label":""});y["n"]+=x["n"];y["label"]=y["label"] or x["label"]
  return [d[k] for k in sorted(d)]
 if o=="policy": return sorted(x["user"] for x in r["rows"] if x["active"] and x["role"] in r["allowed"])
 if o=="metrics":
  x=r["values"]; return {"count":len(x),"total":sum(x),"average":round(sum(x)/len(x),2) if x else None}
 if o=="migrate": return [{"id":transform({"op":"slug","text":x["name"]}),"name":x["name"],"enabled":x["status"]=="active"} for x in r["rows"] if x["name"].strip()]
 raise ValueError("unknown operation")
