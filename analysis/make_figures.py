#!/usr/bin/env python3
"""Generate pre-S7 static figures and source CSVs using only local data."""
from __future__ import annotations

import argparse
import csv
import html
import json
import math
import statistics
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from analysis.verifier_pass_v2 import ROOT, enforce_formal_s7_gate, read_records, summarize

FIG = ROOT / "figures"
DATA = FIG / "data"
COLORS = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#000000"]
# Last commit containing every source artifact before this figure-generation
# stage began. It is fixed so the generated README does not point at a
# transient, uncommitted HEAD.
SOURCE_SNAPSHOT = "d5479a28b3a07ecc6f7dc559abc65ebae4536690"


def write_csv(name: str, rows: list[dict]) -> Path:
    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / f"{name}.csv"
    fields = list(rows[0]) if rows else ["status"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(rows or [{"status":"no data"}])
    return path


def wilson(x: int, n: int) -> tuple[float, float]:
    if not n: return (0.0, 0.0)
    z=1.95996398454; p=x/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return max(0,c-h),min(1,c+h)


def svg_bar(name: str, title: str, rows: list[dict], label: str, value: str, low: str | None = None, high: str | None = None, y_label: str = "Value") -> None:
    width,height=1200,700; left,bottom,top,right=110,170,80,40; pw=width-left-right; ph=height-top-bottom
    vals=[float(r[value]) for r in rows]; ymax=max([1.0]+([float(r[high]) for r in rows] if high else vals)); n=max(1,len(rows)); bw=pw/n*.65
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="white"/>',f'<text x="{width/2}" y="40" text-anchor="middle" font-family="Arial" font-size="25">{html.escape(title)}</text>',
           f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+ph}" stroke="#333"/><line x1="{left}" y1="{top+ph}" x2="{left+pw}" y2="{top+ph}" stroke="#333"/>',
           f'<text x="25" y="{top+ph/2}" transform="rotate(-90 25 {top+ph/2})" font-family="Arial" font-size="16">{html.escape(y_label)}</text>']
    for tick in range(6):
        v=ymax*tick/5; y=top+ph-(v/ymax*ph); parts.append(f'<line x1="{left}" y1="{y}" x2="{left+pw}" y2="{y}" stroke="#ddd"/><text x="{left-10}" y="{y+5}" text-anchor="end" font-family="Arial" font-size="13">{v:.2f}</text>')
    for i,row in enumerate(rows):
        x=left+(i+.5)*pw/n-bw/2; v=float(row[value]); y=top+ph-v/ymax*ph
        parts.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{top+ph-y}" fill="{COLORS[i%len(COLORS)]}"/>')
        if low and high:
            lo,hi=float(row[low]),float(row[high]); ylo=top+ph-lo/ymax*ph; yhi=top+ph-hi/ymax*ph; xm=x+bw/2
            parts.append(f'<line x1="{xm}" y1="{ylo}" x2="{xm}" y2="{yhi}" stroke="#111" stroke-width="2"/><line x1="{xm-7}" y1="{ylo}" x2="{xm+7}" y2="{ylo}" stroke="#111"/><line x1="{xm-7}" y1="{yhi}" x2="{xm+7}" y2="{yhi}" stroke="#111"/>')
        text=html.escape(str(row[label])); parts.append(f'<text x="{x+bw/2}" y="{top+ph+18}" transform="rotate(40 {x+bw/2} {top+ph+18})" text-anchor="start" font-family="Arial" font-size="12">{text}</text>')
    parts.append('</svg>')
    FIG.mkdir(parents=True,exist_ok=True); svg=FIG/f"{name}.svg"; svg.write_text("".join(parts),encoding="utf-8")
    png=FIG/f"{name}.png"
    # SVG->PNG through an opaque JPEG intermediate avoids transparent PNGs
    # becoming unreadable in dark-mode viewers while preserving the SVG.
    with tempfile.NamedTemporaryFile(suffix=".jpg") as temporary:
        conversion=subprocess.run(["sips","-s","format","jpeg",str(svg),"--out",temporary.name],capture_output=True,text=True)
        if conversion.returncode:
            raise RuntimeError(f"sips SVG conversion failed: {conversion.stderr}")
        subprocess.run(["sips","-s","format","png",temporary.name,"--out",str(png)],capture_output=True,check=True)
    subprocess.run(["sips","-s","dpiWidth","200","-s","dpiHeight","200",str(png)],capture_output=True,check=True)


def tool_rows() -> list[dict]:
    rows=[]
    for path in sorted((ROOT/"data/b3_s4_r2_runs").glob("*/metadata.json")):
        meta=json.loads(path.read_text()); events=[json.loads(x) for x in (path.parent/"events.jsonl").read_text().splitlines()]
        tools=[e for e in events if e.get("event")=="tool_result"]
        for i,e in enumerate(tools):
            decile=min(10,int(i/max(1,len(tools))*10)+1); name=e.get("tool_name"); kind="read" if name in {"read_file","list_directory"} else "write" if name in {"write_file","str_replace"} else "command" if name=="run_command" else "other"
            rows.append({"model":meta.get("requested_model_id"),"decile":decile,"action_type":kind})
    counts=Counter((r["model"],r["decile"],r["action_type"]) for r in rows); totals=Counter((r["model"],r["decile"]) for r in rows)
    return [{"model":m,"decile":d,"action_type":a,"count":c,"proportion":c/totals[(m,d)]} for (m,d,a),c in sorted(counts.items())]


def run_metrics() -> list[dict]:
    rows=[]
    for path in sorted((ROOT/"data/b3_s4_r2_runs").glob("*/metadata.json")):
        meta=json.loads(path.read_text()); events=[json.loads(x) for x in (path.parent/"events.jsonl").read_text().splitlines()]; tools=[e for e in events if e.get("event")=="tool_result"]
        writes=[i for i,e in enumerate(tools,1) if e.get("tool_name")=="write_file"]; paths=[]
        for e in tools:
            if e.get("tool_name")=="write_file":
                try: paths.append(json.loads(e.get("arguments") or "{}").get("path"))
                except json.JSONDecodeError: paths.append(None)
        commands=[(i,e) for i,e in enumerate(tools,1) if e.get("tool_name")=="run_command"]
        primary=[i for i,e in commands if any(k in str(e.get("arguments") or "").lower() for k in ("test","pytest","unittest","py_compile"))]
        sensitivity=[i for i,e in commands if (e.get("result") or {}).get("ok") is True]
        repeated=Counter((e.get("tool_name"),str(e.get("arguments"))) for e in tools)
        runtime=json.loads((path.parent/"runtime_r2.json").read_text()) if (path.parent/"runtime_r2.json").exists() else {}; usage=runtime.get("usage") or {}
        rows.append({"model":meta.get("requested_model_id"),"steps":len(tools),"first_edit":writes[0] if writes else 0,"validation_primary":int(bool(writes and any(i>writes[-1] for i in primary))),"validation_sensitivity":int(bool(writes and any(i>writes[-1] for i in sensitivity))),"write_rewrites":max(0,len(writes)-len(set(paths))),"loops":sum(c-1 for c in repeated.values() if c>=3),"input_tokens":usage.get("prompt_tokens",usage.get("input_tokens",0)) or 0,"cached_tokens":usage.get("cached_input_tokens",0) or 0,"output_tokens":usage.get("completion_tokens",usage.get("output_tokens",0)) or 0,"reasoning_tokens":usage.get("reasoning_tokens",usage.get("reasoning_output_tokens",0)) or 0})
    return rows


def medians(rows: list[dict], fields: list[str]) -> list[dict]:
    groups=defaultdict(list)
    for r in rows: groups[r["model"]].append(r)
    return [{"model":m,**{f:statistics.median(float(x[f]) for x in xs) for f in fields},"n":len(xs)} for m,xs in sorted(groups.items())]


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--formal-s7",action="store_true"); args=parser.parse_args()
    if args.formal_s7:
        enforce_formal_s7_gate(ROOT/"STATUS.md",ROOT/"analysis/analysis_patch_manifest.json")
        raise SystemExit("S7 gate passed; formal figures require the post-completion analysis commit")
    s4=read_records(ROOT/"data/b3_s4_r2_runs"); by=defaultdict(list)
    for r in s4: by[r["model"]].append(r)
    f1=[]
    for model,rs in sorted(by.items()):
        x=summarize(rs); lo,hi=wilson(x["verifier_pass"],x["primary_n"]); f1.append({"model":model,"n":x["primary_n"],"passes":x["verifier_pass"],"rate":x["verifier_pass_rate"],"wilson_low":lo,"wilson_high":hi,"calibration_band":"20%-80%"})
    write_csv("F1_dev_pass_rates",f1); svg_bar("F1_dev_pass_rates","F1. Dev verifier-pass rates",f1,"model","rate","wilson_low","wilson_high","Verifier pass rate")
    audit=json.loads((ROOT/"data/verifier_pass_v2_cohort_audit.json").read_text())["cohorts"]; f2=[]
    for cohort in ("S4","S5_original","S5_replacement_inclusive","S6_L3b"):
        x=audit[cohort]["all"]
        for metric in ("legacy_pass","verifier_pass"):
            f2.append({"cohort_metric":f"{cohort} {metric}","cohort":cohort,"metric":metric,"numerator":x[metric],"denominator":x["primary_n"],"rate":x[metric]/x["primary_n"]})
    write_csv("F2_legacy_vs_verifier",f2); svg_bar("F2_legacy_vs_verifier","F2. Legacy vs verifier pass",f2,"cohort_metric","rate",y_label="Pass rate")
    f3=[]
    for model,rs in sorted(by.items()):
        for flag in ("verifier_pass","final_empty","timeout","max_steps_reached","provider_error_protocol"):
            f3.append({"model_flag":f"{model} {flag}","model":model,"flag":flag,"count":sum(bool(r[flag]) for r in rs),"n":len(rs),"rate":sum(bool(r[flag]) for r in rs)/len(rs)})
    write_csv("F3_outcome_flags",f3); svg_bar("F3_outcome_flags","F3. Non-exclusive outcome flags",f3,"model_flag","rate",y_label="Run fraction")
    f4=tool_rows()
    for row in f4: row["model_decile"] = f"{row['model']} d{row['decile']}"
    write_csv("F4_actions_by_decile",f4); f4_plot=[r for r in f4 if r["action_type"]=="write"]; svg_bar("F4_actions_by_decile","F4. Write-action share by trajectory decile",f4_plot,"model_decile","proportion",y_label="Write share")
    raw=run_metrics(); write_csv("F5_process_metrics_raw",raw); f5=medians(raw,["validation_primary","validation_sensitivity","write_rewrites","loops","first_edit","steps"]); write_csv("F5_process_metrics_summary",f5); svg_bar("F5_process_metrics","F5. Median trajectory steps",f5,"model","steps",y_label="Median tool calls")
    process=json.loads((ROOT/"data/s4_dev_diagnose_process_audit_20261010.json").read_text())["by_model"]; f6=[]
    for model,x in process.items(): f6.append({"model":model,"n":x["runs"],"assistant_turns_median":x["assistant_turns"]["median"],"calls_per_turn_median":x["tool_calls_per_assistant_turn"]["median"],"blind_write_rate":x["write_before_first_successful_read"]["numerator"]/x["write_before_first_successful_read"]["denominator"]})
    write_csv("F6_turns_calls_blindwrite",f6); svg_bar("F6_turns_calls_blindwrite","F6. Dev-diagnose assistant turns (post hoc)",f6,"model","assistant_turns_median",y_label="Median assistant turns")
    f7=medians(raw,["input_tokens","cached_tokens","output_tokens","reasoning_tokens"]); write_csv("F7_token_composition",f7); svg_bar("F7_token_composition","F7. Median input-token count",f7,"model","input_tokens",y_label="Median tokens")
    l3=json.loads((ROOT/"data/verifier_pass_erratum_20261010.json").read_text())["S6_L3b_transition_audit"]; f8=[]
    for condition in ("baseline","l3b"):
        x=l3["at32_status"][condition]
        transition=next(item[condition] for item in l3["comparisons"] if item["label"].startswith("At-call-32"))
        values={"A_layer_runs":x["A_layer_runs"],"already_pass_at_32":x["already_verifier_pass_at32"],"not_pass_at_32":x["not_verifier_pass_at32"],"final_pass_among_not_pass_at_32":transition["successes"]}
        for state,value in values.items():
            f8.append({"condition_state":f"{condition} {state}","condition":condition,"state":state,"count":value})
    write_csv("F8_l3b_transitions",f8); svg_bar("F8_l3b_transitions","F8. L3b call-32 transition counts",f8,"condition_state","count",y_label="Runs")
    k=json.loads((ROOT/"data/b5_r2_human_review_results.json").read_text()); f9=[]
    for label,x in k["observed"]["per_label"].items():
        interval=k["bootstrap_95"].get(label+":kappa",{}).get("interval")
        f9.append({"label":label,"kappa":x["kappa"] if x["kappa"] is not None else 0,"kappa_estimable":x["kappa_estimable"],"kappa_low":interval[0] if interval else 0,"kappa_high":interval[1] if interval else 0,"pabak":x["pabak"],**x["contingency_2x2"]})
    write_csv("F9_kappa_pabak",f9); svg_bar("F9_kappa_pabak","F9. Human–judge PABAK by failure label",f9,"label","pabak",y_label="PABAK")
    source_commit=SOURCE_SNAPSHOT
    readme=["# Figures", "", f"Generated by `python3 -m analysis.make_figures` from commit-local, pre-S7 data at source commit `{source_commit}`. Each figure has PNG (200 dpi), SVG, and CSV source in `figures/data/`.", ""]
    sources={"F1":"S4 verifier.json; Wilson 95%","F2":"verifier-pass v2 cohort audit","F3":"S4 non-exclusive flags","F4":"S4 tool calls mechanically binned into deciles","F5":"S4 mechanical process metrics; medians","F6":"S4 dev_diagnose only; post hoc medians","F7":"S4 recorded usage fields; medians","F8":"S6 L3b replay transition audit","F9":"24-packet human–judge agreement; bootstrap intervals in CSV/JSON"}
    for key,source in sources.items(): readme.extend([f"## {key}","",f"Source/definition: {source}. Source commit: `{source_commit}`. Script: `analysis/make_figures.py`. Colorblind-safe Okabe–Ito palette. No formal S7 result is included.",""])
    (FIG/"README.md").write_text("\n".join(readme),encoding="utf-8")
    print(json.dumps({"figures":9,"output":str(FIG)}))


if __name__=="__main__": main()
