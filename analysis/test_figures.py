"""Integrity and structure tests for publication figure generation."""
from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

from PIL import Image

from analysis.make_figures import CSV_SHA256, DATA, FIG, FIGURE_PANEL_COUNTS, FIGURE_STEMS, sha256, verify_csv_hashes


class FigureIntegrityTests(unittest.TestCase):
    def test_immutable_csv_hashes(self) -> None:
        verify_csv_hashes()
        observed = {path.name: sha256(path) for path in DATA.glob("*.csv")}
        self.assertEqual(observed, CSV_SHA256)

    def test_all_rendered_formats_exist(self) -> None:
        for stem in FIGURE_STEMS:
            for suffix in (".pdf", ".png", ".svg"):
                path = FIG / f"{stem}{suffix}"
                self.assertTrue(path.is_file(), path)
                self.assertGreater(path.stat().st_size, 1000, path)

    def test_png_resolution_and_qa_outputs(self) -> None:
        for stem in FIGURE_STEMS:
            with Image.open(FIG / f"{stem}.png") as image:
                dpi = image.info.get("dpi", (0, 0))
                self.assertGreaterEqual(dpi[0], 299)
                self.assertGreaterEqual(dpi[1], 299)
            for suffix in ("deuteranopia", "protanopia"):
                self.assertTrue((FIG / "qa" / f"{stem}_{suffix}.png").is_file())
        self.assertTrue((FIG / "contact_sheet.png").is_file())

    def test_every_main_figure_is_multipanel(self) -> None:
        manifest = json.loads((FIG / "panel_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["panel_counts"], FIGURE_PANEL_COUNTS)
        for stem in FIGURE_STEMS:
            self.assertGreaterEqual(FIGURE_PANEL_COUNTS[stem], 2, stem)

    def test_bar_calls_are_confined_to_f7_token_stack(self) -> None:
        source_path = Path(__file__).with_name("make_figures.py")
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        violations: list[tuple[str | None, str, int]] = []
        stack: list[str] = []

        class Visitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                stack.append(node.name)
                self.generic_visit(node)
                stack.pop()

            def visit_Call(self, node: ast.Call) -> None:
                if isinstance(node.func, ast.Attribute) and node.func.attr in {"bar", "barh"}:
                    function = stack[-1] if stack else None
                    if not (function == "draw_token_stack" and node.func.attr == "barh"):
                        violations.append((function, node.func.attr, node.lineno))
                self.generic_visit(node)

        Visitor().visit(tree)
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
