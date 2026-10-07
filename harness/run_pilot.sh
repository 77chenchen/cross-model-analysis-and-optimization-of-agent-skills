#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ] && [ "$#" -ne 4 ]; then
  echo "usage: $0 <pilot_task_id> <model_id> <gpt|soclaas> [v0|v1]" >&2
  exit 64
fi

task_id="$1"
model="$2"
provider="$3"
skill_version="${4:-v0}"
root="$(cd "$(dirname "$0")/.." && pwd)"
task_dir="$root/tasks/pilot/$task_id/template"
verifier="$root/verifiers/$task_id.py"

case "$task_id" in pilot_a*|pilot_b*) ;; *) echo "pilot task id required" >&2; exit 64;; esac
case "$provider" in gpt|soclaas) ;; *) echo "provider must be gpt or soclaas" >&2; exit 64;; esac
[ -d "$task_dir" ] && [ -f "$verifier" ] || { echo "task or verifier not admitted: $task_id" >&2; exit 66; }

skill_id="${task_id:6:1}"
skill_id="$(printf '%s' "$skill_id" | tr '[:lower:]' '[:upper:]')"
case "$skill_version" in v0|v1) ;; *) echo "skill version must be v0 or v1" >&2; exit 64;; esac
skill_file="$root/skills/$skill_id/$skill_version.md"
[ -f "$skill_file" ] || { echo "missing skill protocol: $skill_file" >&2; exit 66; }
safe_model="${model//[^A-Za-z0-9._-]/_}"
run_dir="$root/data/pilot_runs/${task_id}__${safe_model}__${skill_version}__$(date -u +%Y%m%dT%H%M%SZ)"
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
  command=(zsh -lic "cd '$root' && exec codex exec --profile soclaas --model '$model' --sandbox workspace-write --skip-git-repo-check --json --output-last-message '$run_dir/final.md' --cd '$workspace' '$prompt'")
else
  command=(codex exec --model "$model" --sandbox workspace-write --skip-git-repo-check --json --output-last-message "$run_dir/final.md" --cd "$workspace" "$prompt")
fi
set +e
python3 "$root/harness/run_with_timeout.py" --timeout-seconds 1200 --stdout "$run_dir/trajectory.jsonl" --outcome "$run_dir/process.json" -- "${command[@]}"
process_status=$?
set -e
set +e
python3 "$verifier" "$workspace" > "$run_dir/verifier.json"
verifier_status=$?
set -e
python3 "$root/harness/record_run.py" --root "$root" --task-id "$task_id" --skill-id "$skill_id" --skill-version "$skill_version" --model "$model" --provider "$provider" --run-dir "$run_dir" --trajectory "$run_dir/trajectory.jsonl" --process-outcome "$run_dir/process.json" --final-message "$run_dir/final.md" --workspace "$workspace"
echo "$run_dir"
if [ "$process_status" -ne 0 ]; then exit "$process_status"; fi
exit "$verifier_status"
