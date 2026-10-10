"""Regression tests for the formal verifier-pass S7 summary."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "harness" / "summarize_s7_verifier_pass.py"
SPEC = importlib.util.spec_from_file_location("s7_verifier_summary", MODULE_PATH)
SUMMARY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(SUMMARY)


def make_run(root: Path, name: str, *, outcome: str, verifier_pass: bool, final_empty: bool) -> None:
    run = root / name
    run.mkdir()
    (run / "metadata.json").write_text(json.dumps({"run_id": name, "requested_model_id": "fixture", "task_id": "task", "split": "test_in", "condition": "C0", "outcome_category": outcome, "outcome_flags": {"final_empty": final_empty, "provider_error": False}}))
    (run / "verifier.json").write_text(json.dumps({"passed": verifier_pass}))


class VerifierPassSummaryTests(unittest.TestCase):
    def test_no_empty_final_fixture_matches_legacy(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            make_run(root, "normal", outcome="pass", verifier_pass=True, final_empty=False)
            row = SUMMARY.read_records(root)[0]
            self.assertEqual(row["legacy_pass"], row["verifier_pass"])
            self.assertTrue(row["verifier_pass"])

    def test_empty_final_fixture_uses_frozen_verifier_not_legacy_label(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            make_run(root, "empty_but_passed", outcome="empty_termination", verifier_pass=True, final_empty=True)
            row = SUMMARY.read_records(root)[0]
            self.assertFalse(row["legacy_pass"])
            self.assertTrue(row["verifier_pass"])
            self.assertTrue(row["final_empty"])


if __name__ == "__main__":
    unittest.main()
