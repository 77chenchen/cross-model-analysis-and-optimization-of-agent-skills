#!/usr/bin/env python3
"""Minimal, auditable Chat Completions tool loop for runner r2.

This is deliberately not a general-purpose agent framework.  It has one
provider call per turn, executes only returned tools, never retries a failed
provider call, and archives the unmodified provider response for each turn.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import signal
import subprocess
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from openai import OpenAI

MAX_TOOL_OUTPUT_CHARS = 12_000
CHARS_PER_TOKEN_ESTIMATE = 4
DEFAULT_TOOL_TIMEOUT_SECONDS = 120


TOOLS = [
    {"type": "function", "function": {"name": "list_directory", "description": "List a directory within the workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "Relative path, default ."}}, "additionalProperties": False}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read a UTF-8 text file within the workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "write_file", "description": "Create or replace a UTF-8 text file within the workspace.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "run_command", "description": "Run a shell command in the workspace with a timeout.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 120}}, "required": ["command"], "additionalProperties": False}}},
]


class ContextBudgetExceeded(RuntimeError):
    pass


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def truncate(text: str, limit: int = MAX_TOOL_OUTPUT_CHARS) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit] + "\n[tool output truncated]", True


def workspace_path(workspace: Path, raw_path: str) -> Path:
    if not isinstance(raw_path, str) or not raw_path:
        raise ValueError("path must be a nonempty string")
    candidate = (workspace / raw_path).resolve()
    root = workspace.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("path escapes workspace")
    return candidate


def run_command(workspace: Path, command: str, timeout_seconds: int) -> dict[str, Any]:
    if not isinstance(command, str) or not command.strip():
        raise ValueError("command must be a nonempty string")
    safe_env = {"PATH": os.environ.get("PATH", ""), "HOME": str(workspace), "LANG": "C.UTF-8"}
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        shell=True,
        cwd=workspace,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        env=safe_env,
    )
    timed_out = False
    try:
        stdout, _ = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, _ = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, _ = process.communicate()
    output, was_truncated = truncate(stdout or "")
    return {"returncode": process.returncode, "timed_out": timed_out, "elapsed_seconds": round(time.monotonic() - started, 3), "output": output, "output_truncated": was_truncated}


def execute_tool(workspace: Path, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute one well-formed tool call and return JSON-safe observation data."""
    workspace = workspace.resolve()
    if name == "list_directory":
        target = workspace_path(workspace, arguments.get("path", "."))
        if not target.is_dir():
            raise ValueError("path is not a directory")
        names = sorted(item.name + ("/" if item.is_dir() else "") for item in target.iterdir())
        shown = names[:200]
        return {"ok": True, "entries": shown, "entries_truncated": len(names) > len(shown)}
    if name == "read_file":
        target = workspace_path(workspace, arguments["path"])
        if not target.is_file():
            raise ValueError("path is not a file")
        content, was_truncated = truncate(target.read_text(encoding="utf-8"))
        return {"ok": True, "path": str(target.relative_to(workspace)), "content": content, "content_truncated": was_truncated}
    if name == "write_file":
        target = workspace_path(workspace, arguments["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(arguments["content"], encoding="utf-8")
        return {"ok": True, "path": str(target.relative_to(workspace)), "bytes_written": len(arguments["content"].encode("utf-8"))}
    if name == "run_command":
        timeout_seconds = arguments.get("timeout_seconds", DEFAULT_TOOL_TIMEOUT_SECONDS)
        if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= DEFAULT_TOOL_TIMEOUT_SECONDS:
            raise ValueError("timeout_seconds must be an integer between 1 and 120")
        return {"ok": True, **run_command(workspace, arguments["command"], timeout_seconds)}
    raise ValueError(f"unknown tool: {name}")


def message_token_estimate(messages: list[dict[str, Any]]) -> int:
    return (len(json.dumps(messages, ensure_ascii=False, separators=(",", ":"))) + CHARS_PER_TOKEN_ESTIMATE - 1) // CHARS_PER_TOKEN_ESTIMATE


@dataclass
class RunState:
    final_text: str = ""
    finish_reason: str | None = None
    returned_model_id: str | None = None
    response_count: int = 0
    tool_call_count: int = 0
    tool_parse: dict[str, int] = field(default_factory=lambda: {"valid": 0, "invalid_json": 0, "invalid_schema": 0, "unknown_tool": 0, "execution_error": 0})
    usage: dict[str, int] = field(default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "reasoning_tokens": 0})
    context_budget_exceeded: bool = False
    provider_error: str | None = None
    deadline_exceeded: bool = False
    sampling: dict[str, Any] = field(default_factory=dict)


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_event(path: Path, value: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def _usage(payload: dict[str, Any], state: RunState) -> None:
    usage = payload.get("usage") or {}
    for target, source in (("prompt_tokens", "prompt_tokens"), ("completion_tokens", "completion_tokens"), ("total_tokens", "total_tokens")):
        value = usage.get(source)
        if isinstance(value, int):
            state.usage[target] += value
    details = usage.get("completion_tokens_details") or {}
    reasoning = details.get("reasoning_tokens")
    if isinstance(reasoning, int):
        state.usage["reasoning_tokens"] += reasoning


def run_agent(*, workspace: Path, output: Path, model: str, prompt: str, temperature: float, seed: int | None, max_steps: int, context_limit: int, timeout_seconds: int, client: Any | None = None) -> RunState:
    """Run until a final assistant message, hard limit, or first provider error.

    `client` exists only for deterministic unit tests.  Production creates an
    OpenAI Chat Completions client from SOCLAAS_API_KEY.
    """
    if client is None:
        key = os.environ.get("SOCLAAS_API_KEY")
        if not key:
            raise RuntimeError("SOCLAAS_API_KEY unavailable in this shell")
        client = OpenAI(api_key=key, base_url="https://soclaas-api.comp.nus.edu.sg/v1")
    output.mkdir(parents=True, exist_ok=True)
    raw_dir = output / "raw_responses"
    events = output / "events.jsonl"
    messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
    state = RunState(sampling={"temperature_requested": temperature, "temperature_sent": temperature, "seed_requested": seed, "seed_sent": seed, "seed_accepted_by_transport": None, "seed_provider_echo": None})
    deadline = time.monotonic() + timeout_seconds

    while True:
        if time.monotonic() >= deadline:
            state.deadline_exceeded = True
            append_event(events, {"timestamp": utcnow(), "event": "runner_deadline_exceeded"})
            break
        estimate = message_token_estimate(messages)
        if estimate > context_limit:
            state.context_budget_exceeded = True
            append_event(events, {"timestamp": utcnow(), "event": "context_budget_exceeded", "estimated_tokens": estimate, "limit": context_limit})
            break
        if state.tool_call_count >= max_steps:
            append_event(events, {"timestamp": utcnow(), "event": "max_steps_reached", "max_steps": max_steps})
            break
        request: dict[str, Any] = {"model": model, "temperature": temperature, "messages": messages, "tools": TOOLS}
        if seed is not None:
            request["seed"] = seed
        try:
            response = client.chat.completions.create(**request)
        except Exception as error:  # No retry: the first provider failure terminates the run.
            state.provider_error = f"{type(error).__name__}: {error}"
            append_event(events, {"timestamp": utcnow(), "event": "provider_error", "error": state.provider_error})
            break
        payload = response.model_dump(mode="json") if hasattr(response, "model_dump") else response
        state.response_count += 1
        save_json(raw_dir / f"response_{state.response_count:03d}.json", payload)
        choice = (payload.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        state.finish_reason = choice.get("finish_reason")
        state.returned_model_id = payload.get("model") or state.returned_model_id
        _usage(payload, state)
        if seed is not None:
            state.sampling["seed_accepted_by_transport"] = True
            state.sampling["seed_provider_echo"] = payload.get("seed") or payload.get("system_fingerprint")
        calls = message.get("tool_calls") or []
        append_event(events, {"timestamp": utcnow(), "event": "provider_response", "response_index": state.response_count, "finish_reason": state.finish_reason, "visible_content_chars": len(message.get("content") or ""), "reasoning_chars": len(message.get("reasoning") or ""), "tool_call_count": len(calls), "estimated_context_tokens": estimate})
        if not calls:
            state.final_text = message.get("content") or ""
            break
        messages.append({"role": "assistant", "content": message.get("content") or "", "tool_calls": calls})
        for call in calls:
            if state.tool_call_count >= max_steps:
                break
            state.tool_call_count += 1
            function = call.get("function") or {}
            name = function.get("name")
            call_id = call.get("id") or f"call_{state.response_count}_{state.tool_call_count}"
            raw_arguments = function.get("arguments", "{}")
            result: dict[str, Any]
            try:
                arguments = json.loads(raw_arguments)
            except (TypeError, json.JSONDecodeError):
                state.tool_parse["invalid_json"] += 1
                result = {"ok": False, "error": "invalid_json_arguments"}
            else:
                if not isinstance(arguments, dict) or not isinstance(name, str):
                    state.tool_parse["invalid_schema"] += 1
                    result = {"ok": False, "error": "invalid_tool_schema"}
                else:
                    try:
                        result = execute_tool(workspace, name, arguments)
                        state.tool_parse["valid"] += 1
                    except ValueError as error:
                        category = "unknown_tool" if "unknown tool" in str(error) else "execution_error"
                        state.tool_parse[category] += 1
                        result = {"ok": False, "error": str(error)}
                    except Exception as error:  # Tool failure is observable and returned once, not retried.
                        state.tool_parse["execution_error"] += 1
                        result = {"ok": False, "error": f"{type(error).__name__}: {error}"}
            append_event(events, {"timestamp": utcnow(), "event": "tool_result", "response_index": state.response_count, "tool_call_id": call_id, "tool_name": name, "arguments": raw_arguments, "result": result})
            messages.append({"role": "tool", "tool_call_id": call_id, "content": json.dumps(result, ensure_ascii=False)})
    save_json(output / "runtime_r2.json", {"runner": "r2", "completed_at": utcnow(), **state.__dict__, "max_steps": max_steps, "context_limit": context_limit, "timeout_seconds": timeout_seconds, "token_estimation": f"characters/{CHARS_PER_TOKEN_ESTIMATE}"})
    (output / "final.md").write_text(state.final_text, encoding="utf-8")
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--temperature", type=float, default=0.5)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--max-steps", type=int, default=40)
    parser.add_argument("--context-limit", type=int, default=65536)
    parser.add_argument("--timeout-seconds", type=int, default=1200)
    args = parser.parse_args()
    run_agent(workspace=args.workspace.resolve(), output=args.output.resolve(), model=args.model, prompt=args.prompt_file.read_text(encoding="utf-8"), temperature=args.temperature, seed=args.seed, max_steps=args.max_steps, context_limit=args.context_limit, timeout_seconds=args.timeout_seconds)


if __name__ == "__main__":
    main()
