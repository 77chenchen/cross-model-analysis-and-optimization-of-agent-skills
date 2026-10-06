#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <task-id> <model> <replicate>" >&2
  exit 2
fi

task_id="$1"
model="$2"
replicate="$3"
benchmark_root="$(cd "$(dirname "$0")" && pwd)"
task_root="$benchmark_root/tasks/code_repair/$task_id"
safe_model="${model//\//_}"
run_id="${task_id}__${safe_model}__rep_${replicate}__v0"
run_root="$benchmark_root/data/raw/$run_id"
workspace="$run_root/workspace"

test -f "$task_root/task.md"
test -d "$task_root/seed"
mkdir -p "$run_root"
rm -rf "$workspace"
mkdir -p "$workspace"
cp -R "$task_root/." "$workspace/"
cp "$task_root/seed/"* "$workspace/"

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

test_files=("$task_root"/test_*.py)
test_file="${test_files[0]}"
cp "$test_file" "$workspace/"
test_module="$(basename "$test_file" .py)"
(cd "$workspace" && python3 -m unittest -v "$test_module") > "$run_root/evaluation.txt" 2>&1
