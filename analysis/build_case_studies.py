#!/usr/bin/env python3
"""Build deterministic dev_diagnose-only paired case-study draft."""
from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "data/b3_s4_r2_runs"
OUTPUT = ROOT / "data/case_study_selection_20261010.json"
DOC = ROOT / "docs/case_studies.md"
SEED = 31010
DEV = [
    "pilot_a01_label_parser", "pilot_a03_record_deduplication", "pilot_a05_version_parser",
    "pilot_b01_csv_cleaning", "pilot_b03_duplicate_audit", "pilot_b05_date_validation",
]
STRONG = {"gemma4:26b", "qwen3.8:27b", "qwen3-coder-next"}
WEAK = "qwen3.5:9b"
VALIDATION = ("test", "pytest", "unittest", "py_compile")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def records() -> list[dict]:
    rows = []
    for path in sorted(RUNS.glob("*/metadata.json")):
        metadata, run_dir = load(path), path.parent
        if metadata.get("task_id") not in DEV:
            continue
        verifier = load(run_dir / "verifier.json")
        events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        tools = [event for event in events if event.get("event") == "tool_result"]
        rows.append({"run_id": metadata["run_id"], "model": metadata.get("requested_model_id"),
                     "task": metadata.get("task_id"), "passed": verifier.get("passed") is True,
                     "run_dir": str(run_dir.relative_to(ROOT)), "tools": tools})
    return rows


def choose(items: list[dict], rng: random.Random) -> dict | None:
    if not items:
        return None
    return sorted(items, key=lambda item: item["run_id"])[rng.randrange(len(items))]


def action(event: dict) -> str:
    name = str(event.get("tool_name"))
    args = str(event.get("arguments") or "").replace("\n", " ")
    result = event.get("result") or {}
    status = "ok" if result.get("ok") is not False and not result.get("timed_out") and result.get("returncode") in (None, 0) else "error"
    return f"{name} ({status}): {args[:100]}"


def quote(event: dict) -> str:
    text = str(event.get("arguments") or "").replace("\n", " ")
    return text[:160].replace("|", "\\|")


def behavior(run: dict) -> dict[str, bool]:
    tools = run["tools"]
    writes = [i for i, event in enumerate(tools) if event.get("tool_name") == "write_file"]
    reads = [i for i, event in enumerate(tools) if event.get("tool_name") == "read_file" and (event.get("result") or {}).get("ok") is True]
    validates = [i for i, event in enumerate(tools) if event.get("tool_name") == "run_command" and any(k in str(event.get("arguments") or "").lower() for k in VALIDATION)]
    return {
        "read_before_edit": bool(writes and any(i < writes[0] for i in reads)),
        "validation_after_edit": bool(writes and any(i > writes[-1] for i in validates)),
        "reread_after_edit": bool(writes and any(i > writes[-1] for i in reads)),
        "avoids_repeated_full_rewrite": len(writes) <= 1,
    }


def compact(run: dict) -> dict:
    return {key: value for key, value in run.items() if key != "tools"} | {"behavior": behavior(run)}


def table(strong: dict, weak: dict) -> list[str]:
    length = max(len(strong["tools"]), len(weak["tools"]))
    first_divergence = next((i for i in range(length)
                             if (strong["tools"][i].get("tool_name") if i < len(strong["tools"]) else None)
                             != (weak["tools"][i].get("tool_name") if i < len(weak["tools"]) else None)), None)
    lines = ["| Step | Strong-model action | Weak-model action | Annotation |", "|---:|---|---|---|"]
    for i in range(length):
        left = action(strong["tools"][i]) if i < len(strong["tools"]) else "—"
        right = action(weak["tools"][i]) if i < len(weak["tools"]) else "—"
        note = "**first mechanical divergence**" if i == first_divergence else ""
        lines.append(f"| {i + 1} | {left.replace('|','/')} | {right.replace('|','/')} | {note} |")
    if first_divergence is not None:
        lines.extend(["", "Two-line-or-shorter trajectory excerpts:", "",
                      f"> Strong: `{quote(strong['tools'][first_divergence])}`",
                      ">",
                      f"> Weak: `{quote(weak['tools'][first_divergence])}`"])
    return lines


def main() -> None:
    rng, rows = random.Random(SEED), records()
    eligibility, eligible = {}, []
    for task in DEV:
        strong = [row for row in rows if row["task"] == task and row["model"] in STRONG and row["passed"]]
        weak = [row for row in rows if row["task"] == task and row["model"] == WEAK and not row["passed"]]
        eligibility[task] = {"strong_pass_candidates": len(strong), "weak_fail_candidates": len(weak),
                             "eligible": bool(strong and weak), "reason_if_excluded": None if strong and weak else "missing strong pass or weak failure"}
        if strong and weak:
            eligible.append((task, strong, weak))
    # Fixed rule: first two eligible A and first two eligible B after seeded shuffle.
    rng.shuffle(eligible)
    selected = []
    for skill in ("A", "B"):
        pool = [item for item in eligible if item[0].split("_")[1].startswith(skill.lower())]
        for task, strongs, weaks in pool[:2]:
            selected.append({"task": task, "skill": skill, "strong": choose(strongs, rng), "weak": choose(weaks, rng)})
    weak_success = [row for row in rows if row["model"] == WEAK and row["passed"]]
    strong_failure = [row for row in rows if row["model"] in STRONG and not row["passed"]]
    counter = None
    pairs = [(w, s) for w in weak_success for s in strong_failure if w["task"] == s["task"]]
    if pairs:
        w, s = sorted(pairs, key=lambda pair: (pair[0]["task"], pair[0]["run_id"], pair[1]["run_id"]))[rng.randrange(len(pairs))]
        counter = {"task": w["task"], "weak_success": w, "strong_failure": s}
    llama = [row for row in rows if row["model"] == "llama3.1:8b" and len(row["tools"]) >= 2]
    llama_case = choose(llama, rng)

    strong_counts = Counter()
    weak_counts = Counter()
    strong_only_counts = Counter()
    for case in selected:
        sb, wb = behavior(case["strong"]), behavior(case["weak"])
        for key in sb:
            strong_counts[key] += int(sb[key])
            weak_counts[key] += int(wb[key])
            strong_only_counts[key] += int(sb[key] and not wb[key])
    # Eligibility is recurrence in strong successful trajectories, not a
    # post-hoc assertion that the behavior is absent from every weak run.
    candidates = {key: count for key, count in strong_counts.items() if count >= 2}
    payload = {
        "scope": "S4 dev_diagnose only; post hoc case description; no test data",
        "seed": SEED, "selection_rule": "seeded eligible-task shuffle; first two Skill A and first two Skill B; seeded run selection",
        "eligibility": eligibility,
        "selected": [{"task": case["task"], "skill": case["skill"], "strong": compact(case["strong"]), "weak": compact(case["weak"])} for case in selected],
        "counterexample": None if counter is None else {"task": counter["task"], "weak_success": compact(counter["weak_success"]), "strong_failure": compact(counter["strong_failure"])},
        "llama_case": compact(llama_case) if llama_case else None,
        "implicit_behavior_task_counts": {key: {"strong": strong_counts[key], "weak": weak_counts[key], "strong_yes_weak_no": strong_only_counts[key]} for key in behavior(selected[0]["strong"])},
        "s8_candidates_min_two_strong_success_tasks": candidates,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = ["# Dev-diagnose paired case studies", "",
             "> Scope: **post hoc, S4 dev_diagnose only**. No test trajectory was read. These cases describe mechanisms and do not estimate effects.", "",
             "## Selection rule fixed before selection", "",
             f"Seed `{SEED}`. For each of the six dev-diagnose tasks, eligibility requires at least one verifier-passing v0 run from gemma4:26b, qwen3.8:27b, or qwen3-coder-next and one verifier-failing qwen3.5:9b v0 run. Eligible tasks are shuffled once; the first two Skill A and first two Skill B tasks are selected, then one eligible run per side is sampled with the same RNG.", "",
             "| Task | Strong pass candidates | Weak failure candidates | Included | Exclusion reason |", "|---|---:|---:|---|---|"]
    selected_tasks = {case["task"] for case in selected}
    for task in DEV:
        item = eligibility[task]
        reason = item["reason_if_excluded"] or ("eligible but not selected by fixed four-task quota" if task not in selected_tasks else "—")
        lines.append(f"| {task} | {item['strong_pass_candidates']} | {item['weak_fail_candidates']} | {'yes' if task in selected_tasks else 'no'} | {reason} |")
    for index, case in enumerate(selected, 1):
        strong, weak = case["strong"], case["weak"]
        lines.extend(["", f"## Case {index}: {case['task']} (Skill {case['skill']})", "",
                      f"Strong: `{strong['model']}` / `{strong['run_id']}`. Weak: `{weak['model']}` / `{weak['run_id']}`.", ""])
        lines.extend(table(strong, weak))
        sb = behavior(strong)
        lines.extend(["", "Implicit behavior observed in the strong trajectory: " + ", ".join(key for key, value in sb.items() if value) + "."])
    lines.extend(["", "## Counterexample", ""])
    if counter:
        lines.append(f"Weak success `{counter['weak_success']['run_id']}` is paired with strong failure `{counter['strong_failure']['run_id']}` on `{counter['task']}`. This guards against reading model identity as destiny.")
    else:
        lines.append("No same-task weak-success/strong-failure pair exists in the fixed dev-diagnose pool; absence is reported rather than replaced by a hand-picked near-counterexample.")
    lines.extend(["", "## Llama batched-call case", ""])
    if llama_case:
        lines.append(f"`{llama_case['run_id']}` on `{llama_case['task']}` contains {len(llama_case['tools'])} tool results in a short trajectory. It is included as the fixed-seed llama example of batched tool use followed by termination; the cross-model frequency remains the separate post-hoc process statistic.")
    lines.extend(["", "## Candidate implicit behaviors", "", "| Behavior | Strong successful tasks | Weak failed tasks | Strong=yes, weak=no | S8 eligible (strong >=2) |", "|---|---:|---:|---:|---|"])
    for key in sorted(strong_counts):
        lines.append(f"| {key} | {strong_counts[key]} | {weak_counts[key]} | {strong_only_counts[key]} | {'yes' if strong_counts[key] >= 2 else 'no'} |")
    lines.extend(["", "Only behaviors observed in strong successful trajectories on at least two selected tasks enter the S8 candidate pool. Weak-run counts are retained to prevent describing a recurrent strong behavior as uniquely strong when it is not. Counts are descriptive and depend on the fixed case-selection rule."])
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"selected": len(selected), "counterexample": counter is not None, "output": str(DOC)}))


if __name__ == "__main__":
    main()
