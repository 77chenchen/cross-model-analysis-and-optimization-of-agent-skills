"""Frozen prompt and schedule helpers for the dev-only S8 study.

S8 is deliberately separate from S7: it addresses pilot tasks only and has no
route to a formal test task.  This module holds the exact four prompt arms so
that the manifest can hash their serialized form before execution.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MODEL = "qwen3.5:9b"
TASKS = (
    "pilot_a02_config_parser",
    "pilot_a04_dependency_order",
    "pilot_a06_path_safety",
    "pilot_b02_json_normalization",
    "pilot_b04_multifile_reconciliation",
    "pilot_b06_schema_conversion",
)
CONDITIONS = ("C1", "externalized", "imitation", "generic_control")
REPETITIONS = 8
SCHEDULE_SEED = 20261011
FINAL_SUFFIX = (
    "Read task.md, fix the implementation, and validate your result. Do not "
    "create or modify benchmark-owned verifier files."
)

# Every non-C1 arm uses the same wrapper and exactly 51 whitespace-delimited
# words in the intervention block.  The count is recorded as an audit
# property, rather than claimed to be a provider tokenizer count.
ARM_TEXT = {
    "externalized": (
        "Use this process throughout: read task.md and the target implementation before editing. "
        "Make a targeted minimal edit and avoid rewriting a whole file unless required. "
        "After the final edit, run a focused validation covering stated constraints. Re-read the "
        "final target file before giving a final response. Keep work concise and task-specific."
    ),
    "imitation": (
        "Use this abstract process example throughout: read task.md and target code, make a targeted "
        "minimal edit, run a focused validation, re-read the final target file, then give a final "
        "response. Apply this sequence to the current task without copying task content. Keep work "
        "concise and task-specific at every stage from start."
    ),
    "generic_control": (
        "Use this general completion guidance throughout: understand task.md and target code, work carefully "
        "and efficiently, keep changes organized, review progress, then give a final response. Apply this "
        "guidance to the current task without assuming unstated requirements. Keep work concise and task-specific "
        "at every stage with deliberate clear organized completion work now."
    ),
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def skill_id_for(task_id: str) -> str:
    if task_id not in TASKS:
        raise ValueError(f"task outside frozen S8 dev_validate set: {task_id}")
    return task_id[6].upper()


def prompt_for(condition: str, task_id: str) -> tuple[str, str, str]:
    """Return serialized prompt, semantic condition ID, and source block."""
    skill_id = skill_id_for(task_id)
    if condition == "C1":
        block = (ROOT / "skills" / skill_id / "v0.md").read_text(encoding="utf-8")
        semantic = f"{skill_id}-v0"
    elif condition in ARM_TEXT:
        block = ARM_TEXT[condition]
        semantic = condition
    else:
        raise ValueError(f"unknown S8 condition: {condition}")
    prompt = (
        "You have been supplied the following benchmark guidance. Follow it as operational guidance, "
        "then complete the task in task.md. You have at most 40 tool steps.\n\n"
        "--- guidance begin ---\n"
        f"{block}\n"
        "--- guidance end ---\n\n"
        f"{FINAL_SUFFIX}"
    )
    return prompt, semantic, block


def request_seed(run_id: str) -> int:
    return int(hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:8], 16) % (2**31)


def stable_run_id(task_id: str, condition: str, repetition: int) -> str:
    return f"s8-qwen3-5-9b-{task_id}-{condition}-r{repetition}"
