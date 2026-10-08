#!/usr/bin/env bash
# B5 replacement batch: deliberately sequential after observed 502 clustering.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
while IFS=$'\t' read -r task model repetition replacement; do
  [[ "$task" == "task_id" ]] && continue
  python3 "$root/harness/run_r2_pilot.py" "$task" "$model" --skill-version v0 --run-cohort b5-provider-replacement --split dev --repetition "$repetition" --replacement-of "$replacement" --worker-concurrency 1 --output-root "$root/data/b5_provider_replacements"
  python3 "$root/harness/update_status.py"
done < "$root/config/b5_provider_replacements.tsv"
