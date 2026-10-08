# B1: r2 minimum direct agent runner

Date: 2026-10-08
Status: implemented and unit-tested; no r2 task observation collected.

## Scope and boundaries

The r2 runner is deliberately limited to the SoC LaaS OpenAI-compatible Chat
Completions endpoint and to copied workspaces from `tasks/pilot`.  It cannot
address a formal test task.  It is a new `runner=r2-direct-chat-completions`
cohort, not a repair or reinterpretation of historical `runner=codex-cli`
artifacts.

`data/legacy_runner_registry.csv` is a non-mutating overlay over the 322
existing historical run metadata files. It marks every one `runner=codex-cli`
and `analysis_cohort=legacy_not_pooled_with_r2`; the original artifacts are
left byte-for-byte unchanged.

The runner provides four functions: `list_directory`, `read_file`,
`write_file`, and `run_command`.  Path-based tools reject a path escaping the
workspace. Command output is capped at 12,000 characters; each command gets
at most 120 seconds and runs in a dedicated process group. The entire r2
process is wrapped by `run_with_timeout.py`, which terminates its process
group after 1,200 seconds.

## Evidence captured per run

Each provider response is written unchanged to `raw_responses/response_NNN.json`.
`events.jsonl` records response order, finish reason, visible and reasoning
character counts, parsed tool calls and every tool result. `runtime_r2.json`
records aggregate usage, parser categories, deadline/context status, and
sampling transmission/echo fields. `metadata.json` records runner version and
the actual request parameters separately from provider echo evidence.

The normal loop continues only by returning a tool result required by a valid
tool-call response. It does not retry a provider failure or append a
"continue" instruction. A provider error ends the run and is recorded as a
nonexclusive outcome flag.

## Controls and limitations

Temperature `0.5` is sent on every request. An optional seed is sent exactly
as supplied; success shows that the endpoint accepted the request syntax, not
that the provider applied or echoed a deterministic seed. Context is enforced
locally through a documented conservative JSON-character estimate, because
the endpoint does not expose an independently verifiable context override.
These distinctions are retained in the locked configuration rather than
treated as hidden controls.

## Verification

`python3 -m unittest harness.test_r2_agent harness.test_outcomes` passed (six
tests). The r2 tests cover a two-turn tool loop and raw-response archive, path
escape rejection, and single-attempt provider-error behavior. No provider task
run was performed in B1; B2 is the first authorized runner comparison.
