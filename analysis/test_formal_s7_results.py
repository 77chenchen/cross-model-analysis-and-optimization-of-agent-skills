from __future__ import annotations

import unittest
import json
from pathlib import Path

from analysis.formal_s7_results import bootstrap, summarize_runs, wilson


def row(*, passed: bool, provider: bool = False, final_empty: bool = False) -> dict:
    value = {
        "verifier_pass": passed,
        "provider_error_protocol": provider,
        "legacy_pass": passed and not final_empty,
    }
    for flag in (
        "final_empty", "no_edit", "compile_error", "verifier_fail", "timeout",
        "context_overflow", "provider_error", "max_steps_reached", "verifier_timeout",
    ):
        value[flag] = False
    value["final_empty"] = final_empty
    value["verifier_fail"] = not passed
    value["provider_error"] = provider
    return value


class FormalS7ResultsTests(unittest.TestCase):
    def test_provider_error_excluded_primary_and_failed_in_sensitivity(self) -> None:
        result = summarize_runs([row(passed=True), row(passed=False), row(passed=False, provider=True)])
        self.assertEqual(result["primary_n"], 2)
        self.assertEqual(result["verifier_pass"], 1)
        self.assertEqual(result["verifier_pass_rate"], 0.5)
        self.assertEqual(result["sensitivity_n"], 3)
        self.assertEqual(result["sensitivity_pass_rate"], 1 / 3)

    def test_empty_final_does_not_override_verifier_pass(self) -> None:
        result = summarize_runs([row(passed=True, final_empty=True)])
        self.assertEqual(result["verifier_pass"], 1)
        self.assertEqual(result["legacy_pass"], 0)
        self.assertEqual(result["final_empty"], 1)

    def test_task_bootstrap_uses_number_of_task_values(self) -> None:
        result = bootstrap([0.2, -0.2, 0.0], seed=7)
        self.assertEqual(result["n_tasks"], 3)
        self.assertAlmostEqual(result["mean_difference"], 0.0)

    def test_wilson_is_bounded(self) -> None:
        low, high = wilson(2, 3)
        self.assertIsNotNone(low)
        self.assertIsNotNone(high)
        self.assertGreaterEqual(low, 0.0)
        self.assertLessEqual(high, 1.0)

    def test_committed_formal_manifest_and_figures_are_complete(self) -> None:
        root = Path(__file__).resolve().parent.parent
        manifest = json.loads((root / "results/s7/analysis_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["run_count"], 870)
        self.assertEqual(manifest["verifier_available"], 870)
        figure_manifest = json.loads((root / "figures/s7/figure_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(figure_manifest["figures"]), 5)
        for stem in figure_manifest["figures"]:
            for suffix in (".pdf", ".png", ".svg"):
                self.assertTrue((root / "figures/s7" / f"{stem}{suffix}").is_file())


if __name__ == "__main__":
    unittest.main()
