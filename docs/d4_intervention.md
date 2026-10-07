# D4 intervention specification

## Evidence source and scope

This intervention is motivated only by the four non-blinded, single-run
qwen3.5:9b pilot diagnoses in
`data/diagnostics/d3_qwen35_20261007/`. It is a prospective protocol change,
not evidence that it improves outcomes.

## Changes

| Failure signal in D3 | v1 intervention |
|---|---|
| A03 missed mutation/type constraints | Skill A requires a constraint checklist and boundary behavior check. |
| A05 left a syntactically broken file without validating | Skill A requires re-reading plus syntax/import and behavior checks. |
| B03/B05 ended after inspection without editing | Skill B requires explicit modify, re-inspect, and validate stages. |
| Shell-generated code and tests broke | Both skills prefer simple/direct edits and repair after command failures. |

## Locked comparison

D5 compares the immutable `skills/A/v0.md` or `skills/B/v0.md` against the
corresponding `v1.md` on fresh workspaces. The task, model ID, provider,
temperature, context limit, timeout, verifier, and runner revision must be
held fixed within each paired comparison. A verifier failure remains a retained
outcome. Pilot comparisons remain calibration only.

## Pre-registered outcomes

Primary: external verifier pass/fail. Secondary: syntax/import validity,
observed implementation checkpoint, observed validation checkpoint, action
count, and failed tool/edit attempts. D5 must not change v1 based on its
outcomes before its batch is complete.
