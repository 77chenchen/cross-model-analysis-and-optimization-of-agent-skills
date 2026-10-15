#!/usr/bin/env python3
"""Offline invariants for the locked S8-b prompt and schedule design."""
from __future__ import annotations

import csv
import json
import unittest

from s8b_protocol import (
    ARM_TEXT, CONDITIONS, REPETITIONS, ROOT, SCHEDULE_SEED, TASKS,
    prompt_for, request_seed, sha256_text, stable_run_id,
)


class S8BProtocolTest(unittest.TestCase):
    def test_matrix_and_arm_lengths(self) -> None:
        self.assertEqual(len(TASKS), 24)
        self.assertEqual(len(CONDITIONS), 4)
        self.assertEqual(REPETITIONS, 2)
        self.assertEqual({len(text.split()) for text in ARM_TEXT.values()}, {51})

    def test_prompt_manifest(self) -> None:
        manifest = json.loads((ROOT / "config" / "s8b_prompt_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["protocol"], "s8b-dev-only-v1")
        self.assertEqual(manifest["schedule_seed"], SCHEDULE_SEED)
        self.assertEqual(len(manifest["prompts"]), 96)
        for task in TASKS:
            for condition in CONDITIONS:
                prompt, _, _ = prompt_for(condition, task)
                self.assertEqual(manifest["prompts"][f"{task}/{condition}"]["prompt_sha256"], sha256_text(prompt))

    def test_schedule_is_complete_and_unique(self) -> None:
        with (ROOT / "config" / "s8b_schedule.tsv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(len(rows), 192)
        self.assertEqual(len({row["run_id"] for row in rows}), 192)
        self.assertEqual([int(row["position"]) for row in rows], list(range(1, 193)))
        expected = {
            stable_run_id(task, condition, repetition)
            for task in TASKS for condition in CONDITIONS
            for repetition in range(1, REPETITIONS + 1)
        }
        self.assertEqual({row["run_id"] for row in rows}, expected)
        for row in rows:
            self.assertEqual(int(row["request_seed"]), request_seed(row["run_id"]))


if __name__ == "__main__":
    unittest.main()
