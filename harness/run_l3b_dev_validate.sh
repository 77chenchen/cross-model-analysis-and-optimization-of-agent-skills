#!/usr/bin/env bash
# Preregistered only. Do not execute without explicit post-commit authorization.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
while IFS=$'\t' read -r order task condition repetition model seed; do
  [[ "$order" == "order" ]] && continue
  args=("$root/harness/run_r2_pilot.py" "$task" "$model" --skill-version v0 --run-cohort l3b-dev-validate --split dev --repetition "$repetition" --output-root "$root/data/l3b_runs" --worker-concurrency 1)
  [[ "$condition" == "l3b" ]] && args+=(--l3b-trigger-at 32)
  python "${args[@]}"
  python "$root/harness/update_status.py"
done < "$root/config/l3b_dev_validate_matrix.tsv"
