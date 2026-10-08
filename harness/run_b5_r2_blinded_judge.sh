#!/usr/bin/env bash
# Fresh, single-worker judge batch. New packets only; no report kappa until human labels exist.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
packets="$root/data/b5_r2_human_review"
output="$root/data/b5_r2_blinded_annotations"
logs="$output/driver_logs"
mkdir -p "$output" "$logs"
for packet in "$packets"/packet_*.json; do
  id="$(basename "$packet" .json)"
  prompt="$logs/$id.prompt"
  {
    cat "$root/config/s5_blinded_judge_prompt.md"
    printf '\nPacket id: %s\nSet run_id to this packet id.\n\nPacket:\n' "$id"
    cat "$packet"
  } > "$prompt"
  codex exec --model gpt-5.6-sol --sandbox read-only --skip-git-repo-check --output-schema "$root/metadata/s5_blinded_annotation.schema.json" --output-last-message "$output/$id.json" --cd "$packets" "$(cat "$prompt")" >"$logs/$id.jsonl" 2>&1
  python3 "$root/harness/update_status.py"
done
