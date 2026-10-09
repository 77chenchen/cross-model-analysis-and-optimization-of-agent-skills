#!/usr/bin/env python3
"""Materialize the finite set of serialized S7 prompt templates and hashes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .s7_protocol import ROOT, prompt_for, sha256_text
except ImportError:
    from s7_protocol import ROOT, prompt_for, sha256_text


SAMPLES = {
    "C0": {"none": "test_in_a07_slug"},
    "C1": {"A": "test_in_a07_slug", "B": "test_in_b07_tags", "C": "test_out_c01_inventory"},
    "v1": {"A": "test_in_a07_slug", "B": "test_in_b07_tags"},
    "l3b": {"A": "test_in_a07_slug", "B": "test_in_b07_tags", "C": "test_out_c01_inventory"},
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "config" / "s7_prompt_templates.json")
    args = parser.parse_args()
    templates = {}
    for condition, skills in SAMPLES.items():
        templates[condition] = {}
        for skill, task in skills.items():
            prompt, version, _ = prompt_for(condition, task)
            templates[condition][skill] = {"task_id_for_template": task, "skill_version": version, "sha256": sha256_text(prompt), "prompt": prompt}
    args.output.write_text(json.dumps(templates, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
