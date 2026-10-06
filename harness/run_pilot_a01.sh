#!/usr/bin/env bash
set -euo pipefail
"$(cd "$(dirname "$0")" && pwd)/run_pilot.sh" pilot_a01_label_parser "$1" "$2"
