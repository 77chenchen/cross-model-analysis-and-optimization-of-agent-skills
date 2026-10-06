#!/usr/bin/env bash
set -euo pipefail

model="$1"
provider="$2"
root="$(cd "$(dirname "$0")/.." && pwd)"
task_id="pilot_a01_label_parser"
run_dir="$root/data/pilot_runs/${task_id}__${model//:/_}"
workspace="$run_dir/workspace"
mkdir -p "$run_dir"
rm -rf "$workspace"
mkdir -p "$workspace"
cp -R "$root/tasks/pilot/$task_id/template/." "$workspace/"
prompt="Read task.md, fix the implementation, and validate your result. Do not create or modify benchmark-owned verifier files."

if [ "$provider" = "soclaas" ]; then
  zsh -lic "cd '$root' && codex exec --profile soclaas --model '$model' --sandbox workspace-write --skip-git-repo-check --json --output-last-message '$run_dir/final.md' --cd '$workspace' '$prompt' > '$run_dir/trajectory.jsonl'"
else
  codex exec --model "$model" --sandbox workspace-write --skip-git-repo-check --json --output-last-message "$run_dir/final.md" --cd "$workspace" "$prompt" > "$run_dir/trajectory.jsonl"
fi
python3 "$root/verifiers/$task_id.py" "$workspace" > "$run_dir/verifier.json"
