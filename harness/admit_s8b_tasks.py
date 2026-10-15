#!/usr/bin/env python3
"""Strict local admission gate for S8-b task contracts; never calls a model."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASK_ROOT = ROOT / "tasks" / "s8b"
CONTRACT_ROOT = ROOT / "verifiers" / "s8b_contracts"
VERIFIER = ROOT / "verifiers" / "s8b_contract_verifier.py"
ADMISSION_FILE = ROOT / "tasks" / "s8b_admission.json"
STATUS_FILE = ROOT / "S8B_STATUS.md"
TIMEOUT_SECONDS = 5


def task_ids() -> list[str]:
    return sorted(p.name for p in TASK_ROOT.iterdir() if p.is_dir())


def input_fingerprint(task: str) -> str:
    paths = [
        CONTRACT_ROOT / f"{task}.json",
        TASK_ROOT / task / "template" / "task.md",
        TASK_ROOT / task / "template" / "solution.py",
        VERIFIER,
    ]
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def check_contract_shape(task: str, contract: dict, task_text: str) -> tuple[bool, list[str], str | None]:
    errors: list[str] = []
    if contract.get("task_id") != task:
        errors.append("task_id_mismatch")
    if not isinstance(contract.get("reference_solution"), str) or "def transform(value):" not in contract.get("reference_solution", ""):
        errors.append("missing_executable_reference_signature")
    cases = contract.get("cases")
    if not isinstance(cases, list) or len(cases) < 4:
        errors.append("fewer_than_four_cases")
        cases = cases if isinstance(cases, list) else []
    names = [c.get("name") for c in cases if isinstance(c, dict)]
    if len(names) != len(cases) or any(not isinstance(n, str) or not n.strip() for n in names):
        errors.append("invalid_case_name")
    if len(set(names)) != len(names):
        errors.append("duplicate_case_name")
    for case in cases:
        if not isinstance(case, dict) or not {"name", "input", "expected"} <= set(case):
            errors.append("case_fields_incomplete")
            break
    requirements = contract.get("task_requirements")
    if not isinstance(requirements, list) or not requirements or any(not isinstance(x, str) or not x.strip() for x in requirements):
        errors.append("missing_task_requirements")
        requirements = []
    missing = [rule for rule in requirements if rule not in task_text]
    if missing:
        errors.append("task_text_omits_requirements")
    if "def transform(value)" not in task_text:
        errors.append("task_text_signature_missing")
    return not errors, errors, "; ".join(missing) if missing else None


def verify(task: str, source: str) -> dict:
    """Run one candidate in a temporary task workspace under a fixed timeout."""
    with tempfile.TemporaryDirectory(prefix="s8b_admit_") as scratch:
        workspace = Path(scratch).resolve()
        (workspace / "solution.py").write_text(source, encoding="utf-8")
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONIOENCODING": "utf-8",
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        started = time.perf_counter()
        try:
            done = subprocess.run(
                [sys.executable, str(VERIFIER), task, str(workspace)],
                cwd=workspace,
                env=env,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                check=False,
            )
            elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        except subprocess.TimeoutExpired:
            return {"timed_out": True, "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
                    "returncode": None, "json_valid": False, "passed": None, "checks": {}}
        try:
            parsed = json.loads(done.stdout)
            valid = isinstance(parsed, dict) and isinstance(parsed.get("checks"), dict) and isinstance(parsed.get("passed"), bool)
        except (json.JSONDecodeError, TypeError):
            parsed, valid = {}, False
        return {
            "timed_out": False,
            "elapsed_ms": elapsed_ms,
            "returncode": done.returncode,
            "json_valid": valid,
            "passed": parsed.get("passed") if valid else None,
            "checks": parsed.get("checks", {}) if valid else {},
            "exit_consistent": bool(valid and ((done.returncode == 0 and parsed["passed"]) or (done.returncode != 0 and not parsed["passed"]))),
        }


def evaluate(task: str) -> dict:
    base = TASK_ROOT / task / "template"
    contract_path = CONTRACT_ROOT / f"{task}.json"
    task_path = base / "task.md"
    starter_path = base / "solution.py"
    result = {"task_id": task, "accepted": False}
    if not all(p.is_file() for p in (contract_path, task_path, starter_path, VERIFIER)):
        result["reason"] = "missing_required_file"
        return result
    result["input_fingerprint"] = input_fingerprint(task)
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        task_text = task_path.read_text(encoding="utf-8")
        starter = starter_path.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        result["reason"] = "invalid_or_unreadable_input"
        return result
    shape_ok, shape_errors, _ = check_contract_shape(task, contract, task_text)
    cases = contract.get("cases", [])
    names = [case["name"] for case in cases if isinstance(case, dict) and isinstance(case.get("name"), str)]
    required_checks = set(names) | {f"{name}__input_unchanged" for name in names}
    if contract.get("ordered_mapping_output"):
        required_checks |= {f"{name}__mapping_order" for name, case in zip(names, cases) if isinstance(case.get("expected"), dict)}
    result.update({"case_count": len(cases), "named_check_count": len(required_checks),
                   "case_names_unique": len(names) == len(set(names)),
                   "task_verifier_aligned": shape_ok, "alignment_errors": shape_errors})
    if not shape_ok:
        result["reason"] = "contract_or_task_alignment"
        return result

    reference = verify(task, contract["reference_solution"])
    starter_result = verify(task, starter)
    shortcut_result = verify(task, "def transform(value):\n    return None\n")
    result.update({
        "reference_passes": reference["passed"] is True and reference["returncode"] == 0 and reference["exit_consistent"] and not reference["timed_out"],
        "starter_passes": starter_result["passed"] is True and starter_result["returncode"] == 0,
        "shortcut_passes": shortcut_result["passed"] is True and shortcut_result["returncode"] == 0,
        "reference": reference,
        "starter": starter_result,
        "shortcut": shortcut_result,
    })
    ref_checks = reference.get("checks", {})
    result["named_checks_complete"] = len(ref_checks) >= 3 and required_checks <= set(ref_checks) and all(ref_checks.get(name) is True for name in required_checks)
    negative_runs_valid = all(
        run["json_valid"] and run["exit_consistent"] and not run["timed_out"]
        for run in (starter_result, shortcut_result)
    )
    result["negative_runs_valid"] = negative_runs_valid
    result["accepted"] = bool(
        result["reference_passes"]
        and not result["starter_passes"]
        and not result["shortcut_passes"]
        and result["named_checks_complete"]
        and negative_runs_valid
        and reference["json_valid"]
        and len(ref_checks) >= 3
    )
    if not result["accepted"]:
        result["reason"] = "admission_checks_failed"
    return result


def update_status(rows: list[dict], accepted: bool) -> None:
    total_accepted = sum(row.get("accepted") is True for row in rows)
    completed = sum("case_count" in row for row in rows)
    summary = [
        "<!-- S8B_ADMISSION_PROGRESS_BEGIN -->",
        "## Task construction and admission progress",
        "",
        f"State: **{'task construction and admission complete; ready for protocol locking' if accepted else 'task construction and admission in progress'}**",
        "",
        f"Completed task admissions: {completed}/24. Currently accepted: {total_accepted}/24. No S8 experimental run has been started.",
        "",
        "| Task | Cases | Reference | Starter rejected | Shortcut rejected | Task/verifier alignment | Verifier ms | Admission |",
        "|---|---:|---|---|---|---|---:|---|",
    ]
    for row in rows:
        if "case_count" not in row:
            summary.append(f"| {row['task_id']} | — | pending | pending | pending | pending | — | pending |")
            continue
        ref = row.get("reference", {})
        starter = row.get("starter", {})
        shortcut = row.get("shortcut", {})
        total_ms = sum(x.get("elapsed_ms", 0) for x in (ref, starter, shortcut))
        summary.append(
            f"| {row['task_id']} | {row.get('case_count', 0)} | "
            f"{'pass' if row.get('reference_passes') else 'FAIL'} | "
            f"{'yes' if not row.get('starter_passes') and starter.get('json_valid') else 'no'} | "
            f"{'yes' if not row.get('shortcut_passes') and shortcut.get('json_valid') else 'no'} | "
            f"{'pass' if row.get('task_verifier_aligned') else 'FAIL'} | {total_ms:.3f} | "
            f"{'accepted' if row.get('accepted') else 'rejected'} |"
        )
    summary.append("<!-- S8B_ADMISSION_PROGRESS_END -->")
    existing = STATUS_FILE.read_text(encoding="utf-8") if STATUS_FILE.exists() else "# S8-b status monitor\n"
    block = "\n".join(summary)
    pattern = re.compile(r"<!-- S8B_ADMISSION_PROGRESS_BEGIN -->.*?<!-- S8B_ADMISSION_PROGRESS_END -->", re.S)
    if pattern.search(existing):
        updated = pattern.sub(block, existing)
    else:
        updated = existing.rstrip() + "\n\n" + block + "\n"
    updated = re.sub(r"Last updated: .*", f"Last updated: {date.today().isoformat()} (Asia/Singapore)", updated, count=1)
    STATUS_FILE.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=task_ids(), help="admit one task and preserve prior task results")
    args = parser.parse_args()
    ids = task_ids()
    previous = {}
    if ADMISSION_FILE.exists():
        try:
            previous = {row["task_id"]: row for row in json.loads(ADMISSION_FILE.read_text(encoding="utf-8")).get("tasks", [])}
        except (json.JSONDecodeError, KeyError, TypeError):
            previous = {}
    selected = [args.task] if args.task else ids
    rows_by_id = {}
    for task in ids:
        prior = previous.get(task, {})
        current_fingerprint = input_fingerprint(task) if (CONTRACT_ROOT / f"{task}.json").is_file() else None
        if prior.get("input_fingerprint") == current_fingerprint and current_fingerprint:
            rows_by_id[task] = prior
        else:
            rows_by_id[task] = {"task_id": task, "accepted": False, "reason": "not_yet_checked"}
    for task in selected:
        rows_by_id[task] = evaluate(task)
        rows = [rows_by_id[t] for t in ids]
        count = sum(row.get("accepted") is True for row in rows)
        print(json.dumps({"task_id": task, "accepted_count": count, "task_count": len(ids), "result": rows_by_id[task]}, ensure_ascii=False))
        update_status(rows, count == len(ids))
    rows = [rows_by_id[task] for task in ids]
    report = {
        "stage": "s8b_admission",
        "task_count": len(ids),
        "accepted_count": sum(row.get("accepted") is True for row in rows),
        "all_accepted": len(ids) == 24 and all(row.get("accepted") is True for row in rows),
        "tasks": rows,
    }
    update_status(rows, report["all_accepted"])
    ADMISSION_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if (args.task and rows_by_id[args.task].get("accepted")) or report["all_accepted"] else 1)


if __name__ == "__main__":
    main()
