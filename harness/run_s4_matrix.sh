#!/usr/bin/env bash
# Run the locked S4 matrix with bounded concurrency.  Every condition is
# attempted once; nonzero agent/verifier exits are retained as observations.
set -u -o pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
workers="${S4_WORKERS:-3}"
matrix="$root/config/s4_calibration_matrix.tsv"
logs="$root/data/calibration_runs/driver_logs"
mkdir -p "$logs"

run_one() {
  local task="$1" model="$2" provider="$3" repetition="$4"
  local safe="${task}__${model//[^A-Za-z0-9._-]/_}__r${repetition}"
  "$root/harness/run_calibration.sh" "$task" "$model" "$provider" "$repetition" "S4_calibration" >"$logs/${safe}.log" 2>&1
}
export root logs
export -f run_one

expected=216
[ "$(($(wc -l < "$matrix") - 1))" -eq "$expected" ] || { echo "expected $expected locked rows in $matrix" >&2; exit 65; }
tail -n +2 "$matrix" | xargs -P "$workers" -n 4 bash -c 'run_one "$@"' _
