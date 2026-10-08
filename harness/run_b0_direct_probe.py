#!/usr/bin/env python3
"""B0: direct LaaS Chat Completions observation; no tool calls are executed."""
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/b0_qwen35_direct_probe" / "exact_s4_prompt"
TASKS = ["pilot_a01_label_parser", "pilot_a02_config_parser", "pilot_a03_record_deduplication"]
TOOLS = [
    {"type":"function", "function":{"name":"list_directory", "description":"List a workspace directory.", "parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function", "function":{"name":"read_file", "description":"Read a workspace file.", "parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function", "function":{"name":"write_file", "description":"Write a workspace file.", "parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}}},
    {"type":"function", "function":{"name":"run_command", "description":"Run a workspace command.", "parameters":{"type":"object","properties":{"command":{"type":"string"}},"required":["command"]}}},
]

def prompt_for(task_id: str) -> str:
    skill = (ROOT / "skills/A/v0.md").read_text()
    # This is deliberately byte-for-byte equivalent in wording to the S4
    # calibration prompt, except that direct probing does not execute tools.
    return f"""You have been supplied the following benchmark skill protocol. Follow it as operational guidance, then complete the task in task.md. You have at most 40 tool steps.

--- skill protocol begin ---
{skill}
--- skill protocol end ---

Read task.md, fix the implementation, and validate your result. Do not create or modify benchmark-owned verifier files."""

def main() -> None:
    key = os.environ.get("SOCLAAS_API_KEY")
    if not key: raise SystemExit("SOCLAAS_API_KEY unavailable in this shell")
    OUT.mkdir(exist_ok=True)
    client = OpenAI(api_key=key, base_url="https://soclaas-api.comp.nus.edu.sg/v1")
    manifest = []
    for task in TASKS:
        for repetition in (1, 2):
            response = client.chat.completions.create(model="qwen3.5:9b", temperature=0.5, messages=[{"role":"user", "content":prompt_for(task)}], tools=TOOLS)
            payload = response.model_dump(mode="json")
            path = OUT / f"{task}__r{repetition}.json"
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            choice = payload.get("choices", [{}])[0]
            message = choice.get("message", {}) or {}
            manifest.append({"task":task,"repetition":repetition,"timestamp":datetime.now(UTC).isoformat(),"returned_model":payload.get("model"),"finish_reason":choice.get("finish_reason"),"visible_content_chars":len(message.get("content") or ""),"tool_call_count":len(message.get("tool_calls") or []),"reasoning_fields":[k for k in message if "reason" in k.lower()]})
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"runs":len(manifest), "output":str(OUT)}))

if __name__ == "__main__": main()
