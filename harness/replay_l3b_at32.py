#!/usr/bin/env python3
"""Replay write-only r2 traces to the post-tool-call-32 workspace snapshot.

This is post-hoc analysis. `run_command` side effects are deliberately not
replayed and every row records whether a pre-32 terminal run matched its final
workspace exactly.
"""
from __future__ import annotations

import csv, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMIT = 32

def files(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc")}

def apply(workspace: Path, event: dict) -> bool:
    if event.get("event") != "tool_result" or not event.get("result", {}).get("ok"):
        return False
    name = event.get("tool_name")
    try: args = json.loads(event.get("arguments", "{}"))
    except (TypeError, json.JSONDecodeError): return False
    if name == "write_file":
        path = (workspace / args["path"]).resolve()
        if workspace.resolve() not in path.parents: return False
        path.parent.mkdir(parents=True, exist_ok=True); path.write_text(args["content"], encoding="utf-8"); return True
    if name == "str_replace":
        path = (workspace / args["path"]).resolve()
        if workspace.resolve() not in path.parents: return False
        old, new = args.get("old_str", args.get("old_text")), args.get("new_str", args.get("new_text"))
        if not isinstance(old, str) or not isinstance(new, str) or not path.is_file(): return False
        text = path.read_text(encoding="utf-8")
        if text.count(old) != 1: return False
        path.write_text(text.replace(old, new), encoding="utf-8"); return True
    return False

def verify(task: str, workspace: Path) -> tuple[float | None, str | None]:
    try:
        run = subprocess.run([sys.executable, str(ROOT / "verifiers" / f"{task}.py"), str(workspace)], capture_output=True, text=True, timeout=5)
        data = json.loads(run.stdout); checks = data.get("checks") or {}; values = [v for v in checks.values() if isinstance(v, bool)]
        return (sum(values) / len(values) if values else None), None
    except subprocess.TimeoutExpired: return None, "verifier_timeout_5s"
    except Exception as error: return None, f"{type(error).__name__}: {error}"

rows = []
for meta_path in sorted((ROOT / "data/l3b_runs").glob("pilot_*/metadata.json")):
    run = meta_path.parent; meta = json.loads(meta_path.read_text()); events = [json.loads(x) for x in (run / "events.jsonl").read_text().splitlines()]
    calls = [event for event in events if event.get("event") == "tool_result"]
    tool_calls = len(calls); task = meta["task_id"]; final = meta.get("partial_score")
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp) / "workspace"; shutil.copytree(ROOT / "tasks/pilot" / task / "template", ws)
        for event in calls[:min(LIMIT, tool_calls)]: apply(ws, event)
        if tool_calls < LIMIT:
            match = files(ws) == files(run / "workspace")
            partial, error = final, None if match else "pre32_workspace_mismatch"
        else:
            match, partial, error = None, *verify(task, ws)
    rows.append({"run_id": meta["run_id"], "task_id": task, "condition": "l3b" if meta.get("l3b_trigger_at") else "baseline", "tool_calls": tool_calls, "a_layer_eligible": tool_calls >= LIMIT, "partial_at_32": partial, "final_partial": final, "final_minus_at32": None if partial is None or final is None else final-partial, "pre32_replay_matches_final_workspace": match, "replay_error": error})
out = ROOT / "data/l3b_replay_at32.csv"
with out.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
print(json.dumps({"runs": len(rows), "pre32_validation": sum(r["pre32_replay_matches_final_workspace"] is not None for r in rows), "a_layer": sum(r["a_layer_eligible"] for r in rows)}))
