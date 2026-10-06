#!/usr/bin/env bash
set -euo pipefail

exec "$(cd "$(dirname "$0")" && pwd)/run_task.sh" cr_01 "${1:-gpt-6.1-sol}" "${2:-01}"
