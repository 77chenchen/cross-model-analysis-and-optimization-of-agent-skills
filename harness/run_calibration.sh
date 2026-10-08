#!/usr/bin/env bash
# Execute one fresh pilot-task observation for a named, versioned cohort.
set -euo pipefail

if [ "$#" -ne 5 ]; then
  echo "usage: $0 <pilot_task_id> <model_id> <gpt|soclaas> <repetition> <cohort>" >&2
  exit 64
fi
task_id="$1"; model="$2"; provider="$3"; repetition="$4"; cohort="$5"
root="$(cd "$(dirname "$0")/.." && pwd)"
run_root="${BENCHMARK_RUN_ROOT:-$root/data/calibration_runs}"
task_dir="$root/tasks/pilot/$task_id/template"
verifier="$root/verifiers/$task_id.py"
case "$task_id" in pilot_a*|pilot_b*) ;; *) echo "pilot task id required" >&2; exit 64;; esac
case "$provider" in gpt|soclaas) ;; *) echo "provider must be gpt or soclaas" >&2; exit 64;; esac
case "$repetition" in 1|2|3) ;; *) echo "repetition must be 1, 2, or 3" >&2; exit 64;; esac
[ -d "$task_dir" ] && [ -f "$verifier" ] || { echo "task or verifier not admitted" >&2; exit 66; }

skill_id="${task_id:6:1}"; skill_id="$(printf '%s' "$skill_id" | tr '[:lower:]' '[:upper:]')"
skill_file="$root/skills/$skill_id/v0.md"
safe_model="${model//[^A-Za-z0-9._-]/_}"
nonce="$(python3 -c 'import uuid; print(uuid.uuid4().hex[:10])')"
run_dir="$run_root/${task_id}__${safe_model}__v0__r${repetition}__$(date -u +%Y%m%dT%H%M%SZ)__${nonce}"
workspace="$run_dir/workspace"; mkdir -p "$workspace"; cp -R "$task_dir/." "$workspace/"
skill_text="$(cat "$skill_file")"
prompt="You have been supplied the following benchmark skill protocol. Follow it as operational guidance, then complete the task in task.md. You have at most 40 tool steps.\n\n--- skill protocol begin ---\n$skill_text\n--- skill protocol end ---\n\nRead task.md, fix the implementation, and validate your result. Do not create or modify benchmark-owned verifier files."

if [ "$provider" = "soclaas" ]; then
  export BENCHMARK_AGENT_PROMPT="$prompt"
  command=(zsh -lic "cd '$root' && exec codex exec --profile soclaas --model '$model' --sandbox workspace-write --skip-git-repo-check --json --output-last-message '$run_dir/final.md' --cd '$workspace' \"\$BENCHMARK_AGENT_PROMPT\"")
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
python3 "$root/harness/record_run.py" --root "$root" --task-id "$task_id" --skill-id "$skill_id" --skill-version v0 --model "$model" --provider "$provider" --run-dir "$run_dir" --trajectory "$run_dir/trajectory.jsonl" --process-outcome "$run_dir/process.json" --final-message "$run_dir/final.md" --workspace "$workspace" --run-cohort "$cohort" --repetition "$repetition"
echo "$run_dir"
if [ "$process_status" -ne 0 ]; then exit "$process_status"; fi
exit "$verifier_status"
