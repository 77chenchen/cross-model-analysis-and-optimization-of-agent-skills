"""External verifier for pilot_a03_record_deduplication."""
import importlib.util
import json
import sys
from pathlib import Path


def load(workspace):
    spec = importlib.util.spec_from_file_location("candidate", Path(workspace) / "deduplicate.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.deduplicate_records


def main():
    checks = {}
    try:
        dedupe = load(sys.argv[1])
        original = [{"id": " A ", "v": 1}, {"id": "a", "v": 2}, {"id": "B", "v": 3}]
        answer = dedupe(original)
        checks["normalization"] = answer == [{"id": " A ", "v": 1}, {"id": "B", "v": 3}]
        checks["no_mutation"] = original[0]["id"] == " A " and answer[0] is not original[0]
        checks["invalid"] = dedupe([{}, {"id": " "}, None, {"id": "X"}, {"id": "x"}]) == [{"id": "X"}]
        checks["order"] = dedupe([{"id": "b"}, {"id": "a"}, {"id": "B"}]) == [{"id": "b"}, {"id": "a"}]
    except Exception as error:
        print(json.dumps({"passed": False, "checks": checks, "error": repr(error)}))
        return 1
    passed = all(checks.values())
    print(json.dumps({"passed": passed, "checks": checks, "error": None}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
