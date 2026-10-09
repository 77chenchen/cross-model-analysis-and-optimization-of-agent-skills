#!/usr/bin/env python3
"""Post-hoc reconstruction/replay summary for the completed L3b batch."""
from __future__ import annotations
import csv, json, random, statistics
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
replay={r["run_id"]:r for r in csv.DictReader((ROOT/"data/l3b_replay_at32.csv").open())}
def b(x): return x=="True"
def avg(xs): return statistics.mean(xs) if xs else None
def bootstrap(ds):
    if not ds: return None
    rng=random.Random(20261009); samples=sorted(avg([rng.choice(ds) for _ in ds]) for _ in range(10000))
    return {"task_pairs":len(ds),"mean_difference_l3b_minus_baseline":avg(ds),"paired_bootstrap_95":[samples[249],samples[9749]]}
rows=[]
for path in sorted((ROOT/"data/l3b_runs").glob("pilot_*/metadata.json")):
    m=json.loads(path.read_text()); flags=m["outcome_flags"]; r=replay[m["run_id"]]; verifier=json.loads((path.parent/"verifier.json").read_text())
    if flags.get("provider_error"): outcome="provider_error"
    elif flags.get("timeout"): outcome="timeout"
    elif flags.get("context_overflow"): outcome="context_overflow"
    elif flags.get("max_steps_reached"): outcome="max_steps_reached"
    elif flags.get("compile_error"): outcome="compile_error"
    elif verifier.get("passed") is True: outcome="pass"
    else: outcome="verifier_fail"
    at32=None if r["partial_at_32"] in ("",None) else float(r["partial_at_32"]); final=m.get("partial_score")
    rows.append({"run_id":m["run_id"],"task":m["task_id"],"condition":"l3b" if m.get("l3b_trigger_at") else "baseline","legacy":m.get("legacy_outcome_category"),"outcome":outcome,"final_empty":not (path.parent/"final.md").read_text().strip(),"pass":outcome=="pass","a_layer":b(r["a_layer_eligible"]),"at32":at32,"increment":None if at32 is None or final is None else final-at32,"replay_match":r["pre32_replay_matches_final_workspace"]})
groups={c:[x for x in rows if x["condition"]==c] for c in ("baseline","l3b")}
out={}
for c,g in groups.items():
    out[c]={"runs":len(g),"reconstructed_outcomes":dict(Counter(x["outcome"] for x in g)),"legacy_outcomes":dict(Counter(x["legacy"] for x in g)),"final_empty_rate_all_runs":sum(x["final_empty"] for x in g)/len(g),"final_empty_x_pass":{"empty_pass":sum(x["final_empty"] and x["pass"] for x in g),"empty_nonpass":sum(x["final_empty"] and not x["pass"] for x in g),"nonempty_pass":sum(not x["final_empty"] and x["pass"] for x in g),"nonempty_nonpass":sum(not x["final_empty"] and not x["pass"] for x in g)}}
a={c:[x for x in groups[c] if x["a_layer"] and x["increment"] is not None] for c in groups}
means={c:{t:avg([x["increment"] for x in a[c] if x["task"]==t]) for t in {x["task"] for x in a[c]}} for c in a}
common=sorted(set(means["baseline"])&set(means["l3b"])); diffs=[means["l3b"][t]-means["baseline"][t] for t in common]
summary={"status":"post_hoc_exploratory; no efficacy claim","outcome_reconstruction":out,"final_empty_is_behavioral_not_outcome":True,"replay":{"limit_tool_call":32,"a_layer_definition":">=32 completed tool calls","pre32_workspace_validation":{"checked":sum(x["replay_match"]!="" for x in rows),"exact_matches":sum(x["replay_match"]=="True" for x in rows),"mismatches":sum(x["replay_match"]=="False" for x in rows),"limitation":"run_command side effects are not replayed"},"baseline_negative_control":{"n":len(a["baseline"]),"mean_final_minus_at32":avg([x["increment"] for x in a["baseline"]]),"distribution":[x["increment"] for x in a["baseline"]]},"l3b_a_layer":{"n":len(a["l3b"]),"mean_final_minus_at32":avg([x["increment"] for x in a["l3b"]]),"distribution":[x["increment"] for x in a["l3b"]]},"task_paired":{"per_task_means":means,"comparison":bootstrap(diffs)}}}
(ROOT/"data/l3b_revised_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
lines=["# L3b revised descriptive analysis","","Pre-registered metrics are retained separately. Everything below is post-hoc exploratory; Wilson intervals in the original report quantify single proportions only and are not condition-difference tests.","","## Reconstructed outcomes and final-empty behavior",""]
for c,v in out.items(): lines.append(f"- {c}: reconstructed {v['reconstructed_outcomes']}; legacy {v['legacy_outcomes']}; final-empty rate {v['final_empty_rate_all_runs']:.3f}; final-empty × pass {v['final_empty_x_pass']}.")
lines += ["","Final-empty is now an independent behavioral indicator: abnormal termination is classified first, then compile/verifier outcome; legacy `empty_termination` remains for audit only.","","## Post-call-32 write-only replay","",f"Pre-32 terminal replay exactly matched final workspace in {summary['replay']['pre32_workspace_validation']['exact_matches']}/{summary['replay']['pre32_workspace_validation']['checked']} checked runs; {summary['replay']['pre32_workspace_validation']['mismatches']} mismatched. There were 9 baseline and 12 L3b A-layer candidates; 10 L3b increments were scoreable because one user-authorized verifier timeout had no final partial and one verifier result was unavailable. A-layer (>=32 calls) final_partial − partial_at_32: baseline negative control mean {summary['replay']['baseline_negative_control']['mean_final_minus_at32']} (n={summary['replay']['baseline_negative_control']['n']}), L3b mean {summary['replay']['l3b_a_layer']['mean_final_minus_at32']} (n={summary['replay']['l3b_a_layer']['n']}). Task-paired bootstrap: {summary['replay']['task_paired']['comparison']}. `run_command` side effects are not replayed, so these increments are exploratory.",""]
(ROOT/"docs/l3b_results.md").write_text("\n".join(lines))
print(json.dumps(summary,indent=2))
