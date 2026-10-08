#!/usr/bin/env bash
set -u -o pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; matrix="$root/config/s6_l3_dev_validate_matrix.tsv"
logs="$root/data/s6_l3_runs/driver_logs"; workers="${S6_WORKERS:-3}"; mkdir -p "$logs"
run_one() { bash "$root/harness/run_l3_guardrail.sh" "$1" "$2" S6_L3_dev_validate >"$logs/${1}__r${2}.log" 2>&1; }
export root logs; export -f run_one
[ "$(($(wc -l < "$matrix") - 1))" -eq 18 ] || exit 65
tail -n +2 "$matrix" | tr -d '\r' | xargs -P "$workers" -n 2 bash -c 'run_one "$@"' _
