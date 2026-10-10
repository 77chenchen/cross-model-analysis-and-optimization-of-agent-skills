#!/usr/bin/env python3
"""Deterministically audit stored S7 C0/C1 prompts against the execution lock."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

try:
    from .s7_protocol import FINAL_SUFFIX, ROOT, prompt_for, skill_id_for
except ImportError:
    from s7_protocol import FINAL_SUFFIX, ROOT, prompt_for, skill_id_for

LOCKED_R2_AGENT_SHA256 = "270f2b15c502d5d184e2058609246f9f1a14ad2135eed33c72f5770f43559bae"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(run_dir: Path, locked_prompts: dict) -> dict:
    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    prompt = (run_dir / "prompt.md").read_text(encoding="utf-8")
    condition, task_id = metadata["condition"], metadata["task_id"]
    expected, version, _ = prompt_for(condition, task_id)
    skill = "none" if condition == "C0" else skill_id_for(task_id)
    locked = locked_prompts[condition][skill]
    task_template = ROOT / "tasks" / metadata["split"] / task_id / "template" / "task.md"
    task_workspace = run_dir / "workspace" / "task.md"
    return {
        "run_id": metadata["run_id"],
        "condition": condition,
        "task_id": task_id,
        "repetition": metadata["repetition"],
        "stored_prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "metadata_prompt_hash_matches": metadata.get("prompt_hash") == hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "locked_prompt_hash_matches": locked["sha256"] == hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "expected_prompt_matches": prompt == expected,
        "suffix_matches": prompt.endswith(FINAL_SUFFIX),
        "task_text_hash_matches_template": task_workspace.is_file() and sha256(task_workspace) == sha256(task_template),
        "c0_has_no_protocol_block": condition != "C0" or "--- skill protocol begin ---" not in prompt,
        "c0_has_no_v0_text": condition != "C0" or "Skill A — Code modification v0" not in prompt and "Skill B — File and data processing v0" not in prompt and "Skill C — Multi-step workflow v0" not in prompt,
        "c1_has_v0_protocol_block": condition != "C1" or "--- skill protocol begin ---" in prompt and version == "v0",
        "tool_schema_consistent": metadata.get("tool_schema_version") == 2,
        "tool_definition_source_matches_lock": sha256(ROOT / "harness" / "r2_agent.py") == LOCKED_R2_AGENT_SHA256,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "data" / "s7_runs")
    parser.add_argument("--seed", type=int, default=7102026)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "s7_monitoring" / "qwen_c0_c1_prompt_audit.json")
    args = parser.parse_args()
    prompts = json.loads((ROOT / "config" / "s7_prompt_templates.json").read_text(encoding="utf-8"))
    by_condition = {"C0": [], "C1": []}
    for metadata_path in sorted(args.runs.glob("*/metadata.json")):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("requested_model_id") == "qwen3.5:9b" and metadata.get("condition") in by_condition:
            by_condition[metadata["condition"]].append(metadata_path.parent)
    rng = random.Random(args.seed)
    samples = []
    for condition in ("C0", "C1"):
        candidates = by_condition[condition]
        if len(candidates) < 5:
            raise SystemExit(f"need five completed {condition} qwen runs, found {len(candidates)}")
        samples.extend(audit(path, prompts) for path in rng.sample(candidates, 5))
    fields = [key for result in samples for key, value in result.items() if isinstance(value, bool)]
    passed = all(result[field] for result in samples for field in fields if isinstance(result.get(field), bool))
    output = {"seed": args.seed, "model": "qwen3.5:9b", "sample_counts": {key: len(value) for key, value in by_condition.items()}, "audited": samples, "passed": passed, "checks": sorted(set(fields))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "passed": passed, "audited": len(samples)}))


if __name__ == "__main__":
    main()
