#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: $0 <pilot_task_id> <model_id> <gpt|soclaas>" >&2
  exit 64
fi

task_id="$1"
model="$2"
provider="$3"
root="$(cd "$(dirname "$0")/.." && pwd)"
task_dir="$root/tasks/pilot/$task_id/template"
verifier="$root/verifiers/$task_id.py"

case "$task_id" in pilot_a*|pilot_b*) ;; *) echo "pilot task id required" >&2; exit 64;; esac
case "$provider" in gpt|soclaas) ;; *) echo "provider must be gpt or soclaas" >&2; exit 64;; esac
[ -d "$task_dir" ] && [ -f "$verifier" ] || { echo "task or verifier not admitted: $task_id" >&2; exit 66; }

skill_id="${task_id:6:1}"
skill_id="$(printf '%s' "$skill_id" | tr '[:lower:]' '[:upper:]')"
skill_file="$root/skills/$skill_id/v0.md"
[ -f "$skill_file" ] || { echo "missing skill protocol: $skill_file" >&2; exit 66; }
safe_model="${model//[^A-Za-z0-9._-]/_}"
run_dir="$root/data/pilot_runs/${task_id}__${safe_model}__$(date -u +%Y%m%dT%H%M%SZ)"
workspace="$run_dir/workspace"
mkdir -p "$workspace"
cp -R "$task_dir/." "$workspace/"
skill_text="$(cat "$skill_file")"
prompt="You have been supplied the following benchmark skill protocol. Follow it as operational guidance, then complete the task in task.md.

--- skill protocol begin ---
$skill_text
--- skill protocol end ---

Read task.md, fix the implementation, and validate your result. Do not create or modify benchmark-owned verifier files."

if [ "$provider" = "soclaas" ]; then
  zsh -lic "cd '$root' && codex exec --profile soclaas --model '$model' --sandbox workspace-write --skip-git-repo-check --json --output-last-message '$run_dir/final.md' --cd '$workspace' '$prompt' > '$run_dir/trajectory.jsonl'"
else
  codex exec --model "$model" --sandbox workspace-write --skip-git-repo-check --json --output-last-message "$run_dir/final.md" --cd "$workspace" "$prompt" > "$run_dir/trajectory.jsonl"
fi
set +e
python3 "$verifier" "$workspace" > "$run_dir/verifier.json"
verifier_status=$?
set -e
python3 "$root/harness/record_run.py" --root "$root" --task-id "$task_id" --skill-id "$skill_id" --model "$model" --provider "$provider" --run-dir "$run_dir" --trajectory "$run_dir/trajectory.jsonl"
echo "$run_dir"
exit "$verifier_status"
