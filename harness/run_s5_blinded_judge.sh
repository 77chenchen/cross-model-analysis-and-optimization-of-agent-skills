#!/usr/bin/env bash
# Judge S5 packets without exposing the private packet-to-model manifest.
set -u -o pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
packets="$root/data/s5_blinded_packets"
output="$root/data/s5_blinded_annotations"
logs="$output/driver_logs"
workers="${S5_JUDGE_WORKERS:-3}"
mkdir -p "$output" "$logs"

judge_one() {
  local packet="$1" packet_id prompt_file
  packet_id="$(basename "$packet" .json)"
  prompt_file="$logs/${packet_id}.prompt"
  {
    cat "$root/config/s5_blinded_judge_prompt.md"
    printf '\nPacket id: %s\nSet run_id to this packet id.\n\nPacket:\n' "$packet_id"
    cat "$packet"
  } > "$prompt_file"
  codex exec --model gpt-5.6-sol --sandbox read-only --skip-git-repo-check --output-schema "$root/metadata/s5_blinded_annotation.schema.json" --output-last-message "$output/${packet_id}.json" --cd "$packets" "$(cat "$prompt_file")" >"$logs/${packet_id}.jsonl" 2>&1
}
export root packets output logs
export -f judge_one
find "$packets" -maxdepth 1 -name 'packet_*.json' -print | sort | xargs -P "$workers" -n 1 bash -c 'judge_one "$1"' _
