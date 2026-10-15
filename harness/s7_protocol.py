"""Pure protocol helpers shared by the S7 scheduler and formal runners."""
from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FINAL_SUFFIX = (
    "Read task.md, fix the implementation, and validate your result. Do not "
    "create or modify benchmark-owned verifier files."
)
SCHEDULE_SEEDS = {
    "qwen3.5:9b": 351009,
    "gemma4:26b": 426009,
    "qwen3.8:27b": 382709,
    "qwen3-coder-next": 303509,
    "llama3.1:8b": 318109,
    "gpt-5.6-sol": 560009,
    "ornith1.5:35b": 1535009,
    "glm-5.3-flash": 530009,
}
OPEN_MODELS = set(SCHEDULE_SEEDS) - {"gpt-5.6-sol"}


def skill_id_for(task_id: str) -> str:
    """Extract A/B/C from frozen formal identifiers such as test_in_a07_slug."""
    parts = task_id.split("_")
    if len(parts) < 3 or not parts[2] or parts[2][0].upper() not in {"A", "B", "C"}:
        raise ValueError(f"unsupported formal task identifier: {task_id}")
    return parts[2][0].upper()


def split_for(task_id: str) -> str:
    if task_id.startswith("test_in_"):
        return "test_in"
    if task_id.startswith("test_out_"):
        return "test_out"
    raise ValueError(f"unsupported formal task identifier: {task_id}")


def prompt_for(condition: str, task_id: str) -> tuple[str, str, str]:
    """Return exact prompt, semantic skill version, and source hash input."""
    if condition == "C0":
        return FINAL_SUFFIX, "none", ""
    skill_id = skill_id_for(task_id)
    version = "v1" if condition == "v1" else "v0"
    if condition == "v1" and skill_id == "C":
        raise ValueError("v1 is not applicable to Skill-C/test_out tasks")
    if condition not in {"C1", "v1", "l3b"}:
        raise ValueError(f"unknown condition: {condition}")
    skill = ROOT / "skills" / skill_id / f"{version}.md"
    text = skill.read_text(encoding="utf-8")
    prompt = (
        "You have been supplied the following benchmark skill protocol. Follow it "
        "as operational guidance, then complete the task in task.md. You have at "
        "most 40 tool steps.\n\n"
        "--- skill protocol begin ---\n"
        f"{text}"
        "--- skill protocol end ---\n\n"
        f"{FINAL_SUFFIX}"
    )
    return prompt, version, text


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_run_id(model: str, task_id: str, condition: str, repetition: int) -> str:
    normalized = "".join(char if char.isalnum() else "-" for char in model).strip("-")
    return f"s7-{normalized}-{task_id}-{condition}-r{repetition}"


def request_seed(run_id: str) -> int:
    """Stable per-run provider seed, distinct from the schedule-permutation seed."""
    return int(hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:8], 16) % (2**31)
