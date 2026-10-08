#!/usr/bin/env bash
set -u -o pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; workers="${B3_WORKERS:-3}"
matrix="$root/config/b3_s5_r2_matrix.tsv"; output="$root/data/b3_s5_r2_runs"; logs="$output/driver_logs"
mkdir -p "$logs"
run_one() { local task="$1" model="$2" repetition="$3"; local safe="${task}__r${repetition}"; python3 "$root/harness/run_r2_pilot.py" "$task" "$model" --skill-version v0 --run-cohort B3_S5_r2 --split dev --repetition "$repetition" --seed 20261008 --output-root "$output" >"$logs/$safe.log" 2>&1; }
export root output logs; export -f run_one
[ "$(($(wc -l < "$matrix") - 1))" -eq 36 ] || { echo "expected 36 locked rows" >&2; exit 65; }
tail -n +2 "$matrix" | tr -d '\r' | xargs -P "$workers" -n 3 bash -c 'run_one "$@"' _
