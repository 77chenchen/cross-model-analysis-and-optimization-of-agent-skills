# B0: Qwen3.5 direct Chat Completions probe

Date: 2026-10-08
Status: completed; gate closed pending user review
Scope: three S4 `qwen3.5:9b` tasks that had an empty final message under the
legacy Codex CLI runner (`pilot_a01_label_parser`,
`pilot_a02_config_parser`, and `pilot_a03_record_deduplication`), two direct
calls per task.  No frozen asset was modified and no test-split task ran.

## Method

The probe called the SoC LaaS Chat Completions endpoint directly with
`model=qwen3.5:9b`, `temperature=0.5`, the S4 calibration prompt wording, and
the four declared tool definitions (`list_directory`, `read_file`,
`write_file`, and `run_command`).  The wording is sourced from
`harness/run_calibration.sh`; the probe deliberately did **not** execute a
returned tool call or send a second turn.  That boundary makes this an
interface/field-observation probe, not a performance evaluation.

The complete provider responses, including reasoning and tool-call payloads,
are retained locally under
`data/b0_qwen35_direct_probe/exact_s4_prompt/` and ignored by Git.  The
tracked manifest contains the fields required to audit the conclusion.

## Results

| Task | Repetitions | finish_reason | visible text | parsed tool call | reasoning field |
|---|---:|---|---:|---|---|
| `pilot_a01_label_parser` | 2 | `tool_calls` | 0 chars | `read_file({"path":"task.md"})` | present |
| `pilot_a02_config_parser` | 2 | `tool_calls` | 0 chars | `read_file({"path":"task.md"})` | present |
| `pilot_a03_record_deduplication` | 2 | `tool_calls` | 0 chars | `read_file({"path":"task.md"})` | present |

All six direct responses had one parseable tool call, a provider
`finish_reason` of `tool_calls`, and nonempty `message.reasoning`.  A zero
length `message.content` is expected for this tool-call turn; it is not an
empty termination.

## Interpretation

For these samples, the Qwen endpoint does produce observable reasoning and a
valid request to inspect `task.md`.  Therefore the legacy CLI result pattern
(`final_empty`, no observed workspace edit) cannot be interpreted as evidence
that the model produced no output or made no tool request.  It is consistent
with the legacy runner failing to preserve/continue this tool-call state, but
B0 does **not** prove the exact point of loss: it did not execute the call and
does not reproduce the Codex CLI transport.

The B1 r2 loop may use this exact Chat Completions behavior to execute tool
calls and record every raw response.  It must remain a new runner cohort;
legacy `runner=codex-cli` observations are retained and never combined with
r2 statistics.

## Non-comparable preflight

An initial six-call preflight expanded `task.md` inside the prompt rather than
using the S4 wording.  It showed the same first-turn tool-call pattern, but it
is intentionally excluded from the table and any conclusion above.  Its raw
files remain local only; the canonical B0 manifest is
`data/b0_qwen35_direct_probe/exact_s4_prompt/manifest.json`.
