#!/usr/bin/env python3
"""Calculate Cohen's kappa for supplied blinded human failure-mode labels."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
human_path = ROOT / "data/s5_manual_review/human_annotations.jsonl"
manifest = json.loads((ROOT / "data/s5_manual_review/review_manifest.json").read_text())
judge_dir = ROOT / "data/s5_blinded_annotations"
human = {json.loads(line)["run_id"]: json.loads(line) for line in human_path.read_text().splitlines() if line.strip()}
labels = ["premature_implementation", "repeated_exploration", "ineffective_debugging_loop", "insufficient_validation", "missed_constraint", "premature_completion", "tool_misuse", "empty_termination", "file_corruption"]
pairs = []
for packet in manifest["packet_ids"]:
    if packet not in human: continue
    judge = json.loads((judge_dir / f"{packet}.json").read_text())
    for label in labels:
        pairs.append((label in judge["failure_modes"], label in human[packet]["failure_modes"]))
if not pairs: raise SystemExit("no human labels supplied")
po = sum(a == b for a, b in pairs) / len(pairs)
pa = sum(a for a, _ in pairs) / len(pairs); pb = sum(b for _, b in pairs) / len(pairs)
pe = pa * pb + (1 - pa) * (1 - pb)
kappa = (po - pe) / (1 - pe) if pe != 1 else None
print(json.dumps({"unit": "packet_failure_mode", "pairs": len(pairs), "observed_agreement": po, "expected_agreement": pe, "cohens_kappa": kappa}, indent=2))
