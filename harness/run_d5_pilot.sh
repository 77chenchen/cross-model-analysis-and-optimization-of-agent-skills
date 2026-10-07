#!/usr/bin/env bash
set -euo pipefail

# Executes the frozen D5 pilot matrix. Individual verifier failures are data,
# so the matrix continues after each run and records the exit status.
root="$(cd "$(dirname "$0")/.." && pwd)"
model="qwen3.5:9b"
provider="soclaas"
tasks=(
  pilot_a03_record_deduplication
  pilot_a05_version_parser
  pilot_b03_duplicate_audit
  pilot_b05_date_validation
)
summary="$root/data/pilot_runs/d5_qwen35_matrix_$(date -u +%Y%m%dT%H%M%SZ).tsv"
printf 'task_id\tskill_version\trunner_exit\trun_directory\n' > "$summary"

for task in "${tasks[@]}"; do
  for version in v0 v1; do
    set +e
    output="$("$root/harness/run_pilot.sh" "$task" "$model" "$provider" "$version")"
    status=$?
    set -e
    run_directory="$(printf '%s\n' "$output" | tail -n 1)"
    printf '%s\t%s\t%s\t%s\n' "$task" "$version" "$status" "$run_directory" >> "$summary"
  done
done

printf '%s\n' "$summary"
