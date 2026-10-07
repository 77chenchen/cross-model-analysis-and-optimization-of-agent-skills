#!/usr/bin/env python3
"""Materialize frozen S3 formal tasks from the reviewable definitions below."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = [
 ("test_in","A","a07_slug","slug text: lowercase, replace runs of non-alphanumerics with one hyphen, trim hyphens", {"op":"slug","text":"Hello, World!"},"hello-world", {"op":"slug","text":"  A__B   C  "},"a-b-c"),
 ("test_in","A","a08_clamp","clamp integer value inclusively between low and high", {"op":"clamp","value":7,"low":0,"high":5},5,{"op":"clamp","value":-1,"low":0,"high":5},0),
 ("test_in","A","a09_header","parse Header: value; trim both sides; reject missing colon or blank sides with null", {"op":"header","text":" X-Id : abc "},["X-Id","abc"],{"op":"header","text":"bad"},None),
 ("test_in","A","a10_extension","return lowercase extension without dot; hidden files and trailing dots yield empty string", {"op":"extension","text":"A.TXT"},"txt",{"op":"extension","text":".env"},""),
 ("test_in","A","a11_duration","parse integer duration with suffix s/m/h into seconds; invalid suffix yields null", {"op":"duration","text":"2h"},7200,{"op":"duration","text":"10x"},None),
 ("test_in","A","a12_enum","map a trimmed lowercase value through supplied mapping; unknown yields null", {"op":"enum","value":" Open ","mapping":{"open":1,"closed":2}},1,{"op":"enum","value":"other","mapping":{"open":1}},None),
 ("test_in","B","b07_tags","split comma tags; trim/lowercase, deduplicate preserving first order", {"op":"tags","text":" A, b, a "},["a","b"],{"op":"tags","text":" ,X,,x "},["x"]),
 ("test_in","B","b08_total","sum integer amounts in record list; ignore non-integers and bool", {"op":"total","rows":[{"amount":2},{"amount":3}]},5,{"op":"total","rows":[{"amount":True},{"amount":"4"}]},0),
 ("test_in","B","b09_phone","normalize digits to +1XXXXXXXXXX; accept 10 digits or leading 1; invalid null", {"op":"phone","text":"(415) 555-0100"},"+14155550100",{"op":"phone","text":"123"},None),
 ("test_in","B","b10_cents","parse nonnegative decimal currency into integer cents; reject >2 decimals", {"op":"cents","text":"12.3"},1230,{"op":"cents","text":"1.234"},None),
 ("test_in","B","b11_bucket","bucket nonnegative integer as low <10, medium <100, high otherwise; negative null", {"op":"bucket","value":10},"medium",{"op":"bucket","value":-1},None),
 ("test_in","B","b12_difference","return sorted normalized strings in left but not right", {"op":"difference","left":[" A","b"],"right":["a"]},["b"],{"op":"difference","left":["x","x"],"right":[]},["x"]),
 ("test_out","C","c01_inventory","from rows id/count, return sorted ids whose total count is below reorder point", {"op":"inventory","rows":[{"id":"b","count":1},{"id":"a","count":4}],"reorder":3},["b"],{"op":"inventory","rows":[{"id":"a","count":1},{"id":"a","count":3}],"reorder":3},[]),
 ("test_out","C","c02_sessions","from events user/action, return sorted users with both login and purchase", {"op":"sessions","events":[{"user":"u","action":"login"},{"user":"u","action":"purchase"}]},["u"],{"op":"sessions","events":[{"user":"u","action":"login"}]},[]),
 ("test_out","C","c03_consolidate","merge records by id summing n and retaining first nonempty label", {"op":"consolidate","rows":[{"id":"a","n":1,"label":""},{"id":"a","n":2,"label":"A"}]},[{"id":"a","n":3,"label":"A"}],{"op":"consolidate","rows":[]},[]),
 ("test_out","C","c04_policy","return sorted users allowed when active true and role in allowed list", {"op":"policy","rows":[{"user":"a","active":True,"role":"admin"},{"user":"b","active":False,"role":"admin"}],"allowed":["admin"]},["a"],{"op":"policy","rows":[{"user":"x","active":True,"role":"user"}],"allowed":["admin"]},[]),
 ("test_out","C","c05_metrics","return count, total and rounded average for numeric values; empty average null", {"op":"metrics","values":[1,2,3]}, {"count":3,"total":6,"average":2.0},{"op":"metrics","values":[]},{"count":0,"total":0,"average":None}),
 ("test_out","C","c06_migrate","convert old records name/status to new id/name/enabled; id is lowercase slug, enabled when status active", {"op":"migrate","rows":[{"name":"Ada Lovelace","status":"active"}]},[{"id":"ada-lovelace","name":"Ada Lovelace","enabled":True}],{"op":"migrate","rows":[{"name":" ","status":"active"}]},[]),
]

REFERENCE = '''import re
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
  m=re.fullmatch(r"(\\d+)([smh])",r["text"]); return int(m[1])*{"s":1,"m":60,"h":3600}[m[2]] if m else None
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
  m=re.fullmatch(r"(\\d+)(?:\\.(\\d{1,2}))?",r["text"]); return int(m[1])*100+int((m[2] if m[2] else "").ljust(2,"0")) if m else None
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
'''

# These deliberately imperfect seeds are task-specific.  They model distinct
# plausible implementation shortcuts rather than reusing a single `return
# None` defect throughout the evaluation pool.
SEEDS = {
 "slug": '    return request.get("text", "").lower()\n',
 "clamp": '    return request["value"]\n',
 "header": '    return request["text"].split(":")\n',
 "extension": '    return request["text"].split(".")[-1]\n',
 "duration": '    return int(request["text"][:-1])\n',
 "enum": '    return request["mapping"].get(request["value"])\n',
 "tags": '    return request["text"].split(",")\n',
 "total": '    return sum(row.get("amount", 0) for row in request["rows"])\n',
 "phone": '    return request["text"]\n',
 "cents": '    return int(float(request["text"]) * 100)\n',
 "bucket": '    return "low"\n',
 "difference": '    return request["left"]\n',
 "inventory": '    return []\n',
 "sessions": '    return []\n',
 "consolidate": '    return request["rows"]\n',
 "policy": '    return [row["user"] for row in request["rows"]]\n',
 "metrics": '    return {"count": len(request["values"])}\n',
 "migrate": '    return request["rows"]\n',
}

def main():
 manifest=[]
 for split,skill,short,description,normal,normal_out,hidden,hidden_out in TASKS:
  task=f"{split}_{short}"; d=ROOT/"tasks"/split/task; (d/"template").mkdir(parents=True,exist_ok=True)
  (d/"template"/"task.md").write_text(f"# {task}\n\nImplement `transform(request)` in `solution.py`. {description}. Preserve the function signature.\n")
  op = normal["op"]
  (d/"template"/"solution.py").write_text("def transform(request):\n" + SEEDS[op])
  c=ROOT/"verifiers"/"formal_contracts";c.mkdir(exist_ok=True);(c/f"{task}.json").write_text(json.dumps({"cases":[{"name":"normal","input":normal,"expected":normal_out},{"name":"hidden_boundary", "input":hidden,"expected":hidden_out}]}))
  for label,code in (("positive",REFERENCE),("shortcut","def transform(request):\n    return None\n")):
   f=ROOT/"verifiers"/"fixtures"/f"{task}_{label}";f.mkdir(parents=True,exist_ok=True);(f/"solution.py").write_text(code)
  manifest.append({"id":task,"split":split,"skill":skill,"verifier":"verifiers/contract_verifier.py"})
 (ROOT/"tasks"/"formal_manifest.json").write_text(json.dumps({"tasks":manifest},indent=2)+"\n")
if __name__=="__main__": main()
