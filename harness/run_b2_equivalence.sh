#!/usr/bin/env bash
# Run B2's fresh, descriptive Gemma comparison.  Both branches use pilot only.
set -u -o pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
output="$root/data/b2_runner_equivalence"
tasks=(pilot_a01_label_parser pilot_a02_config_parser pilot_a03_record_deduplication pilot_a04_dependency_order pilot_a05_version_parser pilot_a06_path_safety pilot_b01_csv_cleaning pilot_b02_json_normalization pilot_b03_duplicate_audit pilot_b04_multifile_reconciliation pilot_b05_date_validation pilot_b06_schema_conversion)
mkdir -p "$output/codex_cli" "$output/r2"
for task in "${tasks[@]}"; do
  echo "codex-cli $task"
  BENCHMARK_RUN_ROOT="$output/codex_cli" bash "$root/harness/run_calibration.sh" "$task" gemma4:26b soclaas 1 B2_runner_equivalence
  echo "r2 $task"
  python3 "$root/harness/run_r2_pilot.py" "$task" gemma4:26b --skill-version v0 --run-cohort B2_runner_equivalence --split dev --repetition 1 --seed 20261008 --output-root "$output/r2"
done
