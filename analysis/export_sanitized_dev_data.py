#!/usr/bin/env python3
"""Export sanitized, combined pre-S7 artifacts without raw model responses."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from analysis.verifier_pass_v2 import ROOT

OUT = ROOT / "data/release"
COHORTS = {
    "S4": ROOT / "data/b3_s4_r2_runs",
    "S5": ROOT / "data/b3_s5_r2_runs",
    "S5_replacements": ROOT / "data/b5_provider_replacements",
    "S6_L3b": ROOT / "data/l3b_runs",
}
META_FIELDS = (
    "run_id", "task_id", "split", "condition", "skill_version", "requested_model_id",
    "repetition", "runner", "runner_version", "temperature_requested", "seed_requested",
    "max_steps", "context_limit", "worker_concurrency", "outcome_category",
    "legacy_outcome_category", "outcome_flags", "partial_score", "verifier_timeout",
    "request_retry_count", "r2_tool_call_count",
)


def scrub(value):
    if isinstance(value, str):
        return value.replace(str(ROOT), "<REPO>").replace(str(ROOT.parent.parent.parent.parent), "<HOME>")
    if isinstance(value, list): return [scrub(item) for item in value]
    if isinstance(value, dict):
        blocked = {"authorization", "api_key", "headers", "provider_url", "endpoint", "reasoning", "reasoning_content"}
        return {key: scrub(item) for key, item in value.items() if key.lower() not in blocked}
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    collections = {name: [] for name in ("metadata", "verifier", "events", "actions")}
    counts = {}
    for cohort, root in COHORTS.items():
        run_count = 0
        for meta_path in sorted(root.glob("*/metadata.json")):
            run_count += 1; run_dir = meta_path.parent; meta = json.loads(meta_path.read_text())
            base = {"cohort": cohort, "run_id": meta.get("run_id", run_dir.name)}
            collections["metadata"].append(base | {key: scrub(meta.get(key)) for key in META_FIELDS if key in meta})
            verifier = json.loads((run_dir / "verifier.json").read_text()) if (run_dir / "verifier.json").exists() else {}
            collections["verifier"].append(base | scrub(verifier))
            events = [json.loads(line) for line in (run_dir / "events.jsonl").read_text().splitlines()] if (run_dir / "events.jsonl").exists() else []
            for sequence, event in enumerate(events, 1):
                clean = scrub(event)
                collections["events"].append(base | {"sequence": sequence} | clean)
                if event.get("event") == "tool_result":
                    result = event.get("result") or {}
                    collections["actions"].append(base | {"sequence": sequence, "tool_name": event.get("tool_name"), "arguments": scrub(event.get("arguments")), "ok": result.get("ok"), "returncode": result.get("returncode"), "timed_out": result.get("timed_out")})
        counts[cohort] = run_count
    files = {}
    for name, rows in collections.items():
        path = OUT / f"{name}.jsonl"
        path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        files[path.name] = {"records": len(rows), "sha256": digest(path), "bytes": path.stat().st_size}
    manifest = {"scope":"completed pre-S7 r2 cohorts only","raw_responses_included":False,"cohorts":counts,"files":files,"sanitization":"absolute paths replaced; provider connection/auth/reasoning fields omitted"}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
