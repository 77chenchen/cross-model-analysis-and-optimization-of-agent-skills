#!/usr/bin/env python3
"""Scan all reachable Git blobs for likely credentials without printing values."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs/secret_scan_20261010.json"
PATTERNS = {
    "openai_style_key": re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}"),
    "aws_access_key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    "google_api_key": re.compile(rb"\bAIza[0-9A-Za-z_-]{30,}"),
    "private_key_header": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main() -> None:
    objects = git("rev-list", "--objects", "--all").decode("utf-8", "replace").splitlines()
    findings=[]; scanned=0; skipped=0
    for entry in objects:
        oid, _, path = entry.partition(" ")
        if not path: continue
        kind=git("cat-file","-t",oid).strip()
        if kind != b"blob": continue
        size=int(git("cat-file","-s",oid)); scanned += 1
        if size > 10_000_000: skipped += 1; continue
        data=git("cat-file","-p",oid)
        if b"\x00" in data[:4096]: continue
        for name,pattern in PATTERNS.items():
            for match in pattern.finditer(data):
                line=data[:match.start()].count(b"\n")+1
                findings.append({"object":oid,"path":path,"line":line,"pattern":name})
    working_findings=[]; working_files=0
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "data/s7_runs" in str(path.relative_to(ROOT)):
            continue
        if path.stat().st_size > 10_000_000:
            continue
        data=path.read_bytes(); working_files += 1
        if b"\x00" in data[:4096]:
            continue
        for name,pattern in PATTERNS.items():
            for match in pattern.finditer(data):
                working_findings.append({"path":str(path.relative_to(ROOT)),"line":data[:match.start()].count(b"\n")+1,"pattern":name})
    payload={"scope":"all reachable Git history plus current non-S7 working tree","scanner":"analysis/scan_git_history_secrets.py","values_redacted":True,"blobs_scanned":scanned,"oversize_blobs_skipped":skipped,"working_files_scanned":working_files,"finding_count":len(findings)+len(working_findings),"history_findings":findings,"working_tree_findings":working_findings}
    OUTPUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({key:payload[key] for key in ("blobs_scanned","oversize_blobs_skipped","working_files_scanned","finding_count")}))


if __name__ == "__main__": main()
