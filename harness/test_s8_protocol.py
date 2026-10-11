"""Offline invariants for the S8 prompt manifest and interleaved schedule."""
from __future__ import annotations

import csv
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))
from s8_protocol import ARM_TEXT, CONDITIONS, REPETITIONS, SCHEDULE_SEED, TASKS, prompt_for, request_seed, sha256_text, stable_run_id

ROOT = Path(__file__).resolve().parent.parent


class S8ProtocolTest(unittest.TestCase):
    def test_candidate_guidance_is_word_matched(self) -> None:
        self.assertEqual({len(value.split()) for value in ARM_TEXT.values()}, {51})

    def test_manifest_and_schedule_are_complete(self) -> None:
        manifest = json.loads((ROOT / "config/s8_prompt_manifest.json").read_text(encoding="utf-8"))
        with (ROOT / "config/s8_dev_validate_schedule.tsv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(len(rows), len(TASKS) * len(CONDITIONS) * REPETITIONS)
        self.assertEqual(manifest["schedule_seed"], SCHEDULE_SEED)
        self.assertEqual({row["task_id"] for row in rows}, set(TASKS))
        self.assertEqual(Counter(row["condition"] for row in rows), Counter({condition: 48 for condition in CONDITIONS}))
        self.assertEqual(len({row["run_id"] for row in rows}), len(rows))
        for row in rows:
            expected = stable_run_id(row["task_id"], row["condition"], int(row["repetition"]))
            self.assertEqual(row["run_id"], expected)
            self.assertEqual(int(row["request_seed"]), request_seed(expected))

    def test_manifest_hashes_the_serialized_prompt(self) -> None:
        manifest = json.loads((ROOT / "config/s8_prompt_manifest.json").read_text(encoding="utf-8"))
        for task in TASKS:
            for condition in CONDITIONS:
                prompt, _, _ = prompt_for(condition, task)
                self.assertEqual(manifest["prompts"][f"{task}/{condition}"]["prompt_sha256"], sha256_text(prompt))


if __name__ == "__main__":
    unittest.main()
