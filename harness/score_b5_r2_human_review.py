#!/usr/bin/env python3
"""Score pre-registered B5-r2 human-vs-judge agreement after validation."""
from __future__ import annotations
import json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "data" / "b5_r2_human_review"
HUMAN, JUDGE = REVIEW / "human_annotations.jsonl", ROOT / "data" / "b5_r2_blinded_annotations"
LABELS = ["premature_implementation", "repeated_exploration", "ineffective_debugging_loop", "insufficient_validation", "missed_constraint", "premature_completion", "tool_misuse", "file_corruption"]
DRAW, SEED = 10_000, 20261010

def interval(values):
    if not values: return None
    values = sorted(values); return [values[int(.025*(len(values)-1))], values[int(.975*(len(values)-1))]]
def binary(judge, human):
    n = len(judge); agreement = sum(a == b for a, b in zip(judge, human))/n; pabak = 2*agreement-1
    if sum(judge) in {0,n} or sum(human) in {0,n}: return {"n":n,"kappa":None,"kappa_estimable":False,"pabak":pabak,"observed_agreement":agreement}
    pj, ph = sum(judge)/n, sum(human)/n; expected = pj*ph+(1-pj)*(1-ph)
    return {"n":n,"kappa":(agreement-expected)/(1-expected),"kappa_estimable":True,"pabak":pabak,"observed_agreement":agreement}
def score(rows):
    per = {label:binary([label in j["failure_modes"] for j,_ in rows],[label in h["failure_modes"] for _,h in rows]) for label in LABELS}
    kappas=[x["kappa"] for x in per.values() if x["kappa"] is not None]
    exact=sum({x for x in LABELS if x in j["failure_modes"]}=={x for x in LABELS if x in h["failure_modes"]} for j,h in rows)/len(rows)
    return {"per_label":per,"macro_kappa":sum(kappas)/len(kappas) if kappas else None,"macro_kappa_estimable_labels":len(kappas),"macro_pabak":sum(x["pabak"] for x in per.values())/len(per),"exact_set_match_rate":exact}
def main():
    packets=sorted(p.stem for p in REVIEW.glob("packet_*.json"))
    if len(packets)!=24 or not HUMAN.exists(): raise SystemExit("need 24 public packets and complete human_annotations.jsonl")
    raw=[json.loads(x) for x in HUMAN.read_text(encoding="utf-8").splitlines() if x.strip()]; human={x.get("run_id"):x for x in raw}
    if len(raw)!=24 or set(human)!=set(packets): raise SystemExit("human labels must first pass harness/check_b5_r2_human_review.py")
    rows=[]; excluded=[]
    for packet in packets:
        judge=json.loads((JUDGE/f"{packet}.json").read_text()); h=human[packet]
        if "unscorable" in judge.get("failure_modes",[]) or "unscorable" in h.get("failure_modes",[]): excluded.append(packet)
        else: rows.append((judge,h))
    if not rows: raise SystemExit("no scorable paired packets")
    observed=score(rows); rng=random.Random(SEED)
    boot={"macro_kappa":[],"macro_pabak":[],"exact_set_match_rate":[],**{f"{x}:kappa":[] for x in LABELS},**{f"{x}:pabak":[] for x in LABELS}}
    for _ in range(DRAW):
        item=score([rng.choice(rows) for _ in rows])
        for key in ("macro_kappa","macro_pabak","exact_set_match_rate"):
            if item[key] is not None: boot[key].append(item[key])
        for label,value in item["per_label"].items():
            if value["kappa"] is not None: boot[f"{label}:kappa"].append(value["kappa"])
            boot[f"{label}:pabak"].append(value["pabak"])
    print(json.dumps({"protocol":"b5-r2-human-kappa-20261010","scorable_packets":len(rows),"unscorable_packet_ids":excluded,"bootstrap":{"draws":DRAW,"seed":SEED},"observed":observed,"bootstrap_95":{k:{"interval":interval(v),"estimable_replicates":len(v)} for k,v in boot.items()}},indent=2))
if __name__ == "__main__": main()
