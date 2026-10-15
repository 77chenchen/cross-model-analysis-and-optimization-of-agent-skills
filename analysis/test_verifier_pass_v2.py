from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from analysis.verifier_pass_v2 import enforce_formal_s7_gate, summarize


def row(*, verifier: bool, legacy: bool, provider: bool = False, timeout: bool = False, task: str = "t") -> dict:
    return {"verifier_pass": verifier, "legacy_pass": legacy, "provider_error_protocol": provider,
            "timeout": timeout, "max_steps_reached": False, "task": task}


class VerifierPassV2Tests(unittest.TestCase):
    def test_nonempty_fixture_old_new_agree(self):
        result = summarize([row(verifier=True, legacy=True)])
        self.assertEqual(result["verifier_pass"], result["legacy_pass"])

    def test_empty_final_fixture_uses_verifier_not_legacy(self):
        result = summarize([row(verifier=True, legacy=False)])
        self.assertEqual(result["verifier_pass"], 1)
        self.assertEqual(result["legacy_pass"], 0)

    def test_provider_excluded_but_timeout_included(self):
        result = summarize([row(verifier=True, legacy=False, provider=True), row(verifier=False, legacy=False, timeout=True)])
        self.assertEqual(result["primary_n"], 1)
        self.assertEqual(result["verifier_pass"], 0)
        self.assertEqual(result["timeouts_in_primary_denominator"], 1)
        self.assertEqual(result["sensitivity_n_provider_as_failure"], 2)

    def test_known_task_sensitivity(self):
        rows = [row(verifier=True, legacy=True, task="pilot_a04_dependency_order"),
                row(verifier=False, legacy=False, task="test_in_b09_phone"),
                row(verifier=True, legacy=True, task="ordinary")]
        self.assertEqual(summarize(rows)["primary_n"], 3)
        self.assertEqual(summarize(rows, {"pilot_a04_dependency_order"})["primary_n"], 2)
        self.assertEqual(summarize(rows, {"test_in_b09_phone"})["primary_n"], 2)

    def test_formal_gate_refuses_incomplete_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            status = root / "STATUS.md"
            status.write_text("| S7 locked formal benchmark | 1086 | 400 | 686 | running |\n", encoding="utf-8")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({}), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "400/1086"):
                enforce_formal_s7_gate(status, manifest)


if __name__ == "__main__":
    unittest.main()
