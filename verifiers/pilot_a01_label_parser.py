"""External verifier for pilot_a01_label_parser."""

import importlib.util
import json
import sys
from pathlib import Path


def load(workspace: Path):
    source = workspace / "label_parser.py"
    spec = importlib.util.spec_from_file_location("candidate", source)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.parse_labels


def main() -> int:
    workspace = Path(sys.argv[1])
    checks = {}
    try:
        parse = load(workspace)
        checks["basic"] = parse("service=api;env=prod") == {"service": "api", "env": "prod"}
        checks["whitespace"] = parse(" service = api ; env= prod ") == {"service": "api", "env": "prod"}
        checks["embedded_equals"] = parse("token=abc=def=ghi") == {"token": "abc=def=ghi"}
        checks["malformed"] = parse("good=yes;broken;=missing;empty= ;tail=ok") == {"good": "yes", "tail": "ok"}
        checks["hidden_combination"] = parse(" a = b=c ; ; z= 9 ; =x") == {"a": "b=c", "z": "9"}
    except Exception as error:
        print(json.dumps({"passed": False, "checks": checks, "error": repr(error)}))
        return 1
    passed = all(checks.values())
    print(json.dumps({"passed": passed, "checks": checks, "error": None}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
