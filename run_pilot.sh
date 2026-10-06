#!/usr/bin/env bash
set -euo pipefail

benchmark_root="$(cd "$(dirname "$0")" && pwd)"
task_root="$benchmark_root/tasks/code_repair/cr_01"
model="${1:-gpt-6.1-sol}"
replicate="${2:-01}"
safe_model="${model//\//_}"
run_id="cr_01__${safe_model}__rep_${replicate}__v0"
run_root="$benchmark_root/data/raw/$run_id"
workspace="$run_root/workspace"
mkdir -p "$run_root"
rm -rf "$workspace"
mkdir -p "$workspace"
cp "$task_root/task.md" "$task_root/test_label_parser.py" "$task_root/task.yaml" "$workspace/"
cp "$task_root/seed/label_parser.py" "$workspace/label_parser.py"

prompt="$(cat "$benchmark_root/configs/skills/code_repair_v0.md")

Read task.md and complete the task in the current directory."

codex exec \
  --model "$model" \
  --sandbox workspace-write \
  --skip-git-repo-check \
  --json \
  --output-last-message "$run_root/final_message.md" \
  --cd "$workspace" \
  "$prompt" > "$run_root/trajectory.jsonl"

(cd "$workspace" && python3 -m unittest -v) > "$run_root/evaluation.txt" 2>&1
