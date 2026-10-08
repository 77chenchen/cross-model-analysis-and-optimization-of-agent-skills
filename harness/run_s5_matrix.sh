#!/usr/bin/env bash
# Run each locked S5 row once. Failures are observed outcomes, never retries.
set -u -o pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
workers="${S5_WORKERS:-3}"
matrix="$root/config/s5_dev_baseline_matrix.tsv"
logs="$root/data/s5_runs/driver_logs"
mkdir -p "$logs"
run_one() {
  local task="$1" model="$2" provider="$3" repetition="$4"
  local safe="${task}__${model//[^A-Za-z0-9._-]/_}__r${repetition}"
  BENCHMARK_RUN_ROOT="$root/data/s5_runs" bash "$root/harness/run_calibration.sh" "$task" "$model" "$provider" "$repetition" "S5_dev_v0" >"$logs/${safe}.log" 2>&1
}
export root logs
export -f run_one
[ "$(($(wc -l < "$matrix") - 1))" -eq 72 ] || { echo "expected 72 locked S5 rows" >&2; exit 65; }
tail -n +2 "$matrix" | tr -d '\r' | xargs -P "$workers" -n 4 bash -c 'run_one "$@"' _
