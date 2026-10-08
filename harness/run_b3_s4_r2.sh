#!/usr/bin/env bash
# Execute the locked B3 S4 r2 matrix. Failed runs are observed outcomes, never retries.
set -u -o pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
workers="${B3_WORKERS:-3}"
matrix="$root/config/b3_s4_r2_matrix.tsv"
output="$root/data/b3_s4_r2_runs"
logs="$output/driver_logs"
mkdir -p "$logs"
run_one() {
  local task="$1" model="$2" repetition="$3"
  local safe="${task}__${model//[^A-Za-z0-9._-]/_}__r${repetition}"
  python3 "$root/harness/run_r2_pilot.py" "$task" "$model" --skill-version v0 --run-cohort B3_S4_r2 --split pilot --repetition "$repetition" --seed 20261008 --output-root "$output" >"$logs/$safe.log" 2>&1
}
export root output logs
export -f run_one
[ "$(($(wc -l < "$matrix") - 1))" -eq 180 ] || { echo "expected 180 locked rows" >&2; exit 65; }
tail -n +2 "$matrix" | tr -d '\r' | xargs -P "$workers" -n 3 bash -c 'run_one "$@"' _
