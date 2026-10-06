"""External verifier for pilot_b02_json_normalization."""
import importlib.util
import json
import sys
from pathlib import Path


def load(workspace):
    spec = importlib.util.spec_from_file_location("candidate", Path(workspace) / "event_normalizer.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.normalize_event


def main():
    checks = {}
    try:
        normalize = load(sys.argv[1])
        source = {"event": " Purchase ", "user_id": " u-1 ", "tags": " New,VIP, new, ,vip "}
        checks["string_tags"] = normalize(source) == {"event": "purchase", "user_id": "u-1", "tags": ["new", "vip"]}
        checks["no_mutation"] = source["event"] == " Purchase " and source["tags"].startswith(" New")
        checks["list_tags"] = normalize({"event": "x", "user_id": "y", "tags": [" A ", "a", "B"]}) == {"event": "x", "user_id": "y", "tags": ["a", "b"]}
        checks["invalid"] = normalize({"event": " ", "user_id": "u"}) is None and normalize({"event": "x", "user_id": " "}) is None
    except Exception as error:
        print(json.dumps({"passed": False, "checks": checks, "error": repr(error)}))
        return 1
    passed = all(checks.values())
    print(json.dumps({"passed": passed, "checks": checks, "error": None}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
