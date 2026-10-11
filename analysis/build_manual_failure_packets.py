#!/usr/bin/env python3
"""Make a fixed-seed, local-only manual-reading sample of weak-model failures."""
from __future__ import annotations

import json
import random
import shutil
from pathlib import Path

from analysis.build_report_supplements import ROOT, mechanical_failure_records, read_csv, safe_events

SEED = 20261011
COUNT = 15
OUT = ROOT / "docs" / "manual_failure_review_packets"


def compact(value: object, limit: int = 900) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return text if len(text) <= limit else text[:limit] + " …[truncated]"


def tool_steps(run_dir: Path) -> list[dict]:
    return [event for event in safe_events(run_dir / "events.jsonl") if event.get("event") == "tool_result"][-10:]


def main() -> None:
    rows = read_csv(ROOT / "results" / "s7" / "run_metrics.csv")
    pool = [record for record in mechanical_failure_records(rows) if "qwen3.5:9b" in record["cohort"]]
    assert len(pool) == 98, f"expected 98 weak failures, got {len(pool)}"
    selected = random.Random(SEED).sample(sorted(pool, key=lambda record: record["run_id"]), COUNT)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    manifest = {"seed": SEED, "population_n": len(pool), "sample_n": COUNT, "packets": []}
    for index, record in enumerate(selected, 1):
        run_dir = Path(record["run_dir"])
        task = (run_dir / "workspace" / "task.md")
        if not task.exists():
            task = run_dir / "task.md"
        packet_id = f"packet_{index:03d}"
        lines = [
            f"# Manual failure review {packet_id}", "",
            "This packet contains no pre-filled conclusion. Read the task, then the last ten recorded tool results and verifier reason. Fill only the researcher fields at the end.",
            "", "## Task", "", "```text", task.read_text(encoding="utf-8", errors="replace").rstrip(), "```",
            "", "## Last 10 recorded tool results", "",
        ]
        for step_no, event in enumerate(tool_steps(run_dir), 1):
            result = event.get("result") or {}
            lines += [f"### {step_no}. `{event.get('tool_name', 'unknown')}`", "", f"Arguments: `{event.get('arguments', '')}`", "", "```json", compact(result), "```", ""]
        reasons = record["failed_checks"] or ([f"verifier error: {record['verifier_error']}"] if record["verifier_error"] else ["No named verifier check was recorded."])
        lines += ["## Verifier failure reason", "", *[f"- `{reason}`" for reason in reasons], "", "## Researcher review (leave blank until manual review)", "", "- Observed failure pattern:", "- Evidence (step numbers):", "- Notes:", ""]
        (OUT / f"{packet_id}.md").write_text("\n".join(lines), encoding="utf-8")
        manifest["packets"].append({"packet_id": packet_id, "source_run_id": record["run_id"], "cohort": record["cohort"], "task_path": str(task.relative_to(ROOT))})
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Manual failure-review packets\n\nFixed-seed (`20261011`) sample of 15 from 98 qwen3.5:9b verifier-failing runs. Packets deliberately leave the review fields blank; `manifest.json` retains source mapping for audit. This is local reading only and does not invoke a model or judge.\n",
        encoding="utf-8")
    print(json.dumps({"population": len(pool), "packets": len(selected), "seed": SEED}))


if __name__ == "__main__":
    main()
