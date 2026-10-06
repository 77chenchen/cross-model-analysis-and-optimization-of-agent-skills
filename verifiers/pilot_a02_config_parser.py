"""External verifier for pilot_a02_config_parser."""
import importlib.util
import json
import sys
from pathlib import Path


def load(workspace: Path):
    spec = importlib.util.spec_from_file_location("candidate", workspace / "config_reader.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.read_settings


def main() -> int:
    checks = {}
    try:
        read = load(Path(sys.argv[1]))
        checks["basic"] = read("host: example\nport: 443") == {"host": "example", "port": "443"}
        checks["comments_and_whitespace"] = read(" # not a comment\n# real\n host : api ") == {"host": "api"}
        checks["embedded_colon"] = read("url: https://a:b/path") == {"url": "https://a:b/path"}
        checks["malformed"] = read("good: yes\n: bad\nblank:  \nmissing\nlast: ok") == {"good": "yes", "last": "ok"}
        checks["last_wins"] = read("mode: old\nmode: new") == {"mode": "new"}
    except Exception as error:
        print(json.dumps({"passed": False, "checks": checks, "error": repr(error)}))
        return 1
    passed = all(checks.values())
    print(json.dumps({"passed": passed, "checks": checks, "error": None}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
