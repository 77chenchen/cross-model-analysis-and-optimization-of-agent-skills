import importlib.util, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
def main():
    task_id, workspace = sys.argv[1], Path(sys.argv[2])
    spec = importlib.util.spec_from_file_location("candidate", workspace / "solution.py")
    module = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
    checks = {}
    try:
        for case in json.loads((ROOT / "verifiers/formal_contracts" / f"{task_id}.json").read_text())["cases"]:
            checks[case["name"]] = module.transform(case["input"]) == case["expected"]
    except Exception as error:
        print(json.dumps({"passed":False,"checks":checks,"error":repr(error)})); return 1
    print(json.dumps({"passed":all(checks.values()),"checks":checks,"error":None})); return 0 if all(checks.values()) else 1
if __name__ == "__main__": raise SystemExit(main())
