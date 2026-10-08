#!/usr/bin/env bash
# One bounded L3 observation: initial v0 turn, then at most one repair turn.
set -euo pipefail
[ "$#" = 3 ] || { echo "usage: $0 <pilot_task_id> <repetition> <cohort>" >&2; exit 64; }
task_id="$1"; repetition="$2"; cohort="$3"
root="$(cd "$(dirname "$0")/.." && pwd)"; model="gemma4:26b"; provider="soclaas"
task_dir="$root/tasks/pilot/$task_id/template"; verifier="$root/verifiers/$task_id.py"
skill_id="${task_id:6:1}"; skill_id="$(printf '%s' "$skill_id" | tr '[:lower:]' '[:upper:]')"
nonce="$(python3 -c 'import uuid; print(uuid.uuid4().hex[:10])')"
run_dir="$root/data/s6_l3_runs/${task_id}__gemma4_26b__l3__r${repetition}__$(date -u +%Y%m%dT%H%M%SZ)__${nonce}"
workspace="$run_dir/workspace"; mkdir -p "$workspace"; cp -R "$task_dir/." "$workspace/"
hash_sources() { shasum "$workspace"/*.py 2>/dev/null | shasum | awk '{print $1}'; }
before="$(hash_sources)"; skill_text="$(cat "$root/skills/$skill_id/v0.md")"
base_prompt="Follow this benchmark skill protocol and complete task.md. Make the smallest correct code change and validate it. Do not modify benchmark-owned verifiers.\n\n$skill_text"
run_turn() {
  local label="$1" prompt="$2" seconds="$3"
  export BENCHMARK_AGENT_PROMPT="$prompt"
  set +e
  python3 "$root/harness/run_with_timeout.py" --timeout-seconds "$seconds" --stdout "$run_dir/${label}.jsonl" --outcome "$run_dir/${label}_process.json" -- zsh -lic "cd '$root' && exec codex exec --profile soclaas --model '$model' --sandbox workspace-write --skip-git-repo-check --json --output-last-message '$run_dir/${label}_final.md' --cd '$workspace' \"\$BENCHMARK_AGENT_PROMPT\""
  set -e
}
run_turn initial "$base_prompt" 900
after="$(hash_sources)"; compile_log="$run_dir/compile.txt"
set +e; python3 -m py_compile "$workspace"/*.py >"$compile_log" 2>&1; compile_status=$?; set -e
reason=""; [ "$before" = "$after" ] && reason="no_source_change"; [ "$compile_status" -ne 0 ] && reason="${reason:+$reason,}compile_error"
repeat_count="$({ rg -io 'traceback|syntaxerror|indentationerror|command not found' "$run_dir/initial.jsonl" || true; } | wc -l | tr -d ' ')"
if [ -n "$reason" ]; then
  repair="Runtime guardrail fired: $reason. You must now inspect the current target, make a direct repair, re-read it, and run one focused validation."
  [ "$repeat_count" -ge 2 ] && repair="$repair A prior error repeated; simplify the edit and avoid complex shell-generated source."
  run_turn repair "$repair" 300
  cat "$run_dir/initial.jsonl" "$run_dir/repair.jsonl" > "$run_dir/trajectory.jsonl"
  cp "$run_dir/repair_final.md" "$run_dir/final.md" 2>/dev/null || true
  cp "$run_dir/repair_process.json" "$run_dir/process.json"
else
  cp "$run_dir/initial.jsonl" "$run_dir/trajectory.jsonl"; cp "$run_dir/initial_final.md" "$run_dir/final.md" 2>/dev/null || true; cp "$run_dir/initial_process.json" "$run_dir/process.json"
fi
set +e; python3 "$verifier" "$workspace" > "$run_dir/verifier.json"; verifier_status=$?; set -e
python3 "$root/harness/record_run.py" --root "$root" --task-id "$task_id" --skill-id "$skill_id" --skill-version v0 --model "$model" --provider "$provider" --run-dir "$run_dir" --trajectory "$run_dir/trajectory.jsonl" --process-outcome "$run_dir/process.json" --final-message "$run_dir/final.md" --workspace "$workspace" --run-cohort "$cohort" --repetition "$repetition"
printf '{"guardrail_fired":%s,"reason":"%s","repeated_error_markers":%s}\n' "$([ -n "$reason" ] && echo true || echo false)" "$reason" "$repeat_count" > "$run_dir/guardrail.json"
echo "$run_dir"; exit "$verifier_status"
