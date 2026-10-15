#!/usr/bin/env python3
"""Frozen prompt and identity helpers for the fresh-task S8-b study."""
from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MODEL = "qwen3.5:9b"
TASKS = tuple(
    [f"a{index:02d}_{name}" for index, name in enumerate((
        "label_fields", "config_lines", "version_parts", "duration_units",
        "safe_extension", "date_format", "path_segments", "header_names",
        "phone_digits", "query_pairs", "slug_text", "range_clamp",
    ), 1)]
    + [f"b{index:02d}_{name}" for index, name in enumerate((
        "record_dedup", "json_cleanup", "csv_totals", "tag_merge",
        "schema_rename", "event_filter", "inventory_delta", "contact_group",
        "invoice_cents", "log_summary", "manifest_diff", "bucket_assign",
    ), 1)]
)
CONDITIONS = ("C1", "externalized", "imitation", "generic_control")
REPETITIONS = 2
SCHEDULE_SEED = 20261015
FINAL_SUFFIX = (
    "Read task.md, repair solution.py, and validate the result. Do not create "
    "or modify benchmark-owned verifier files. You have at most 40 tool calls."
)

# The three experimental arms have the same 51 whitespace-delimited words.
# This is a transparent string-level control, not a provider-token claim.
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
        raise ValueError(f"task outside locked S8-b pool: {task_id}")
    return task_id[0].upper()


def prompt_for(condition: str, task_id: str) -> tuple[str, str, str]:
    skill_id = skill_id_for(task_id)
    if condition == "C1":
        block = (ROOT / "skills" / skill_id / "v0.md").read_text(encoding="utf-8").strip()
        semantic = f"{skill_id}-v0"
    elif condition in ARM_TEXT:
        block = ARM_TEXT[condition]
        semantic = condition
    else:
        raise ValueError(f"unknown S8-b condition: {condition}")
    prompt = (
        "You have been supplied the following benchmark guidance. Follow it as operational guidance, "
        "then complete the repository task.\n\n"
        "--- guidance begin ---\n"
        f"{block}\n"
        "--- guidance end ---\n\n"
        f"{FINAL_SUFFIX}"
    )
    return prompt, semantic, block


def stable_run_id(task_id: str, condition: str, repetition: int) -> str:
    if task_id not in TASKS or condition not in CONDITIONS or repetition not in range(1, REPETITIONS + 1):
        raise ValueError("invalid S8-b run identity")
    return f"s8b-qwen3-5-9b-{task_id}-{condition}-r{repetition}"


def request_seed(run_id: str) -> int:
    return int(hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:8], 16) % (2**31)
