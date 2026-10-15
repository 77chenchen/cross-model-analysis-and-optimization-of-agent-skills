#!/usr/bin/env python3
"""External JSON-contract verifier for fresh S8-b tasks.

Each contract lists named literal input/output checks. It lives outside the
agent workspace and therefore cannot be modified by a candidate run.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_transform(workspace: Path):
    root = workspace.resolve()
    solution = (root / "solution.py").resolve()
    if solution.parent != root or not solution.is_file():
        raise RuntimeError("solution.py must be a file directly inside the task workspace")
    spec = importlib.util.spec_from_file_location("candidate", solution)
    if not spec or not spec.loader:
        raise RuntimeError("cannot load candidate solution.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.transform


def json_compatible(value):
    """Compare Python tuple outputs using their JSON list representation."""
    if isinstance(value, tuple):
        return [json_compatible(item) for item in value]
    if isinstance(value, list):
        return [json_compatible(item) for item in value]
    if isinstance(value, dict):
        return {key: json_compatible(item) for key, item in value.items()}
    return value


def main() -> int:
    task_id, workspace_text = sys.argv[1], sys.argv[2]
    contract_path = ROOT / "verifiers" / "s8b_contracts" / f"{task_id}.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    try:
        transform = load_transform(Path(workspace_text))
        for case in contract["cases"]:
            original = deepcopy(case["input"])
            actual = transform(case["input"])
            checks[case["name"]] = json_compatible(actual) == case["expected"]
            checks[f"{case['name']}__input_unchanged"] = case["input"] == original
            if contract.get("ordered_mapping_output") and isinstance(actual, dict) and isinstance(case["expected"], dict):
                checks[f"{case['name']}__mapping_order"] = list(actual) == list(case["expected"])
    except Exception as error:
        print(json.dumps({"passed": False, "checks": checks, "error": repr(error)}))
        return 1
    passed = all(checks.values()) and len(checks) >= 3
    print(json.dumps({"passed": passed, "checks": checks, "error": None}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
