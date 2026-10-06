"""External verifier for pilot_b01_csv_cleaning."""
import importlib.util
import json
import sys
from pathlib import Path


def load(workspace: Path):
    spec = importlib.util.spec_from_file_location("candidate", workspace / "csv_cleaner.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.clean_rows


def main() -> int:
    checks = {}
    try:
        clean = load(Path(sys.argv[1]))
        source = [{"name": " Ada ", "email": " ADA@EXAMPLE.COM ", "score": "42", "extra": "x"}]
        result = clean(source)
        checks["normalize"] = result == [{"name": "Ada", "email": "ada@example.com", "score": 42}]
        checks["no_mutation"] = source[0]["name"] == " Ada " and "extra" in source[0]
        checks["invalid_rows"] = clean([{"name": "", "email": "x@y", "score": "1"}, {"name": "B", "email": "", "score": "1"}, {"name": "C", "email": "c@y", "score": "3.2"}]) == []
        checks["order"] = clean([{"name": "B", "email": "B@X", "score": "2"}, {"name": "A", "email": "A@X", "score": "1"}]) == [{"name": "B", "email": "b@x", "score": 2}, {"name": "A", "email": "a@x", "score": 1}]
    except Exception as error:
        print(json.dumps({"passed": False, "checks": checks, "error": repr(error)}))
        return 1
    passed = all(checks.values())
    print(json.dumps({"passed": passed, "checks": checks, "error": None}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
