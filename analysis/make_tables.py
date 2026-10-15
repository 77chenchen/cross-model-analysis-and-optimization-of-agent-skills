#!/usr/bin/env python3
"""Reproduce the pre-S7 report tables from local committed artifacts."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path

from analysis.verifier_pass_v2 import ROOT, enforce_formal_s7_gate

OUT = ROOT / "results/tables"


def commit_for(path: str) -> str:
    return subprocess.check_output(["git", "log", "-1", "--format=%H", "--", path], cwd=ROOT, text=True).strip()


def emit(name: str, rows: list[dict], columns: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"{name}.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    (OUT / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formal-s7", action="store_true", help="require the locked 1086/1086 formal-analysis gate")
    args = parser.parse_args()
    if args.formal_s7:
        enforce_formal_s7_gate(ROOT / "STATUS.md", ROOT / "analysis/analysis_patch_manifest.json")
        from analysis.formal_s7_results import main as make_formal_s7_results

        make_formal_s7_results()
        return

    pilot = json.loads((ROOT / "tasks/pilot/admission.json").read_text())
    formal = json.loads((ROOT / "tasks/s3_admission.json").read_text())
    t1 = []
    for item in pilot["tasks"]:
        task = item["id"]; skill = task.split("_")[1][0].upper()
        issue = "task/verifier conflict; report included/excluded" if task == "pilot_a04_dependency_order" else ""
        t1.append({"task": task, "skill": skill, "split": "dev", "admission": "accepted", "known_issue": issue})
    for item in formal["tasks"]:
        task = item["id"]; skill = task.split("_")[2][0].upper()
        issue = "two clustered hard timeouts; sensitivity only, no demonstrated task defect" if task == "test_in_b09_phone" else ""
        t1.append({"task": task, "skill": skill, "split": item["split"], "admission": "accepted", "known_issue": issue})
    emit("T1_tasks", t1, ["task", "skill", "split", "admission", "known_issue"])

    models = [
        ("qwen3.5:9b", "weak target", "r2", "0.5 requested", "sent if supported", "40", "65536", "1200"),
        ("gemma4:26b", "cross-model", "r2", "0.5 requested", "sent if supported", "40", "65536", "1200"),
        ("qwen3.8:27b", "cross-model", "r2", "0.5 requested", "sent if supported", "40", "65536", "1200"),
        ("qwen3-coder-next", "specialized", "r2", "0.5 requested", "sent if supported", "40", "65536", "1200"),
        ("llama3.1:8b", "lower bound", "r2", "0.5 requested", "sent if supported", "40", "65536", "1200"),
        ("ornith1.5:35b", "cross-model", "r2", "0.5 requested", "sent if supported", "40", "65536", "1200"),
        ("glm-5.3-flash", "cross-model", "r2", "0.5 requested", "sent if supported", "40", "65536", "1200"),
        ("gpt-5.6-sol", "reference anchor", "Codex", "uncontrolled", "uncontrolled", "not aligned", "not verified", "1200"),
    ]
    t2 = [dict(zip(["model","role","runner","temperature","seed","max_steps","context_limit","hard_timeout_s"], row)) for row in models]
    emit("T2_models_controls", t2, list(t2[0]))

    audit = json.loads((ROOT / "data/verifier_pass_v2_cohort_audit.json").read_text())["cohorts"]
    t3 = []
    for cohort, views in audit.items():
        for view, item in views.items():
            t3.append({"cohort": cohort, "view": view, "scheduled": item["scheduled"], "provider_error_protocol": item["provider_error_protocol"], "primary_n": item["primary_n"], "legacy_pass": item["legacy_pass"], "verifier_pass": item["verifier_pass"]})
    emit("T3_outcome_reconciliation", t3, list(t3[0]))

    t4 = [
        {"model_group":"qwen3.5:9b","condition":"C0","tasks":18,"repetitions":5,"planned_runs":90,"status":"core"},
        {"model_group":"qwen3.5:9b","condition":"C1","tasks":18,"repetitions":5,"planned_runs":90,"status":"core"},
        {"model_group":"qwen3.5:9b","condition":"v1","tasks":12,"repetitions":5,"planned_runs":60,"status":"exploratory test_in only"},
        {"model_group":"qwen3.5:9b","condition":"L3b","tasks":18,"repetitions":5,"planned_runs":90,"status":"exploratory"},
        {"model_group":"seven other models","condition":"C0","tasks":18,"repetitions":3,"planned_runs":378,"status":"core"},
        {"model_group":"seven other models","condition":"C1","tasks":18,"repetitions":3,"planned_runs":378,"status":"core"},
    ]
    emit("T4_s7_plan", t4, list(t4[0]))

    t5 = [
        {"hypothesis":"C1 validation-after-final-edit < C0","commit":commit_for("docs/s7_process_hypothesis_revision_20261010.md")[:12],"source":"qwen monitoring (generation); other models independent","status":"pending S7 completion"},
        {"hypothesis":"explicit skill reference rises with model capability","commit":commit_for("docs/s7_process_hypothesis_revision_20261010.md")[:12],"source":"pre-cross-model declaration","status":"pending S7 completion"},
        {"hypothesis":"v1 validation rate > C1 on test_in","commit":commit_for("docs/s7_process_hypothesis_revision_20261010.md")[:12],"source":"exploratory","status":"pending S7 completion"},
        {"hypothesis":"L3b call-32 mechanism observation only","commit":commit_for("docs/s7_process_and_l3b_analysis_revision_20261010.md")[:12],"source":"dev replay","status":"descriptive; no conversion test"},
    ]
    emit("T5_hypotheses", t5, list(t5[0]))

    t6 = [
        {"date":"2026-10-10","correction":"primary pass now verifier.json.passed","impact":"legacy empty-final precedence understated pass; old tables retained"},
        {"date":"2026-10-10","correction":"provider_error_protocol separated from broad flag","impact":"hard timeouts remain denominator failures"},
        {"date":"2026-10-10","correction":"A04 recorded as task/verifier conflict","impact":"all applicable dev summaries include/exclude A04"},
        {"date":"2026-10-10","correction":"b09 timeout clustering recorded","impact":"formal summaries include/exclude b09 sensitivity"},
        {"date":"2026-10-10","correction":"validation intent separated from transport success","impact":"9/12 versus 11/12 L3b trigger-validation readings"},
    ]
    emit("T6_errata", t6, list(t6[0]))

    t7 = [
        {"failure_mode":"missed constraints","evidence":"human/judge + verifier checks","change":"v1 explicit requirement inventory","expected_metric":"verifier pass; partial delta"},
        {"failure_mode":"missing post-edit validation","evidence":"mechanical validation-intent metric","change":"v1 validation instruction; L3b fixed reminder","expected_metric":"validation-after-final-edit"},
        {"failure_mode":"repeated whole-file rewrites","evidence":"write_file rewrite metric; post hoc cases","change":"S8 candidate: externalized or imitation process","expected_metric":"rewrite and loop counts"},
        {"failure_mode":"tool misuse","evidence":"human/judge support + mechanical tool errors","change":"no S7 change; S8 candidate only","expected_metric":"tool error rate"},
    ]
    emit("T7_failure_evidence_changes", t7, list(t7[0]))
    print(json.dumps({"tables": 7, "output": str(OUT), "source_commit": subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()}))


if __name__ == "__main__":
    main()
