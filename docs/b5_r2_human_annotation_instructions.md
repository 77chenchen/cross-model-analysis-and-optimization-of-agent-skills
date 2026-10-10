# B5-r2 blinded human trajectory annotation

This is the only instruction file for the 24-packet human review. It contains
no model identity, experimental condition, verifier result, outcome, or LLM
judge label. Do not open the sibling judge-output or private-manifest folders.

## What to open

Open only the 24 files named `packet_001.json` through `packet_024.json` in
`data/b5_r2_human_review/`. Each is an anonymous normalized action trajectory.
The packet array is ordered; use its **one-based array position** as the
`sequence` number (first item is `1`). Do not use
`data/b5_r2_blinded_annotations/`, `data/b5_r2_blinded_packets/`, or any run
directory during annotation.

## What to submit

Create `data/b5_r2_human_review/human_annotations.jsonl`. Add exactly one JSON
object per line, one line per packet, and no Markdown or comments. Use the
packet ID (not a source run ID) in `run_id`; use a stable personal ID in
`annotator_id`; set `blinded` to `true`.

```json
{"run_id":"packet_001","annotator_id":"human_reviewer_01","blinded":true,"stage_events":[{"sequence":1,"label":"understanding"},{"sequence":2,"label":"understanding"},{"sequence":3,"label":"exploration"}],"failure_modes":["none_observed"]}
```

Required fields and allowed values:

| Field | Format |
|---|---|
| `run_id` | Exact packet ID, `packet_001` through `packet_024`. |
| `annotator_id` | Your stable identifier, as a string. |
| `blinded` | Literal JSON boolean `true`. |
| `stage_events` | Array of zero or more `{ "sequence": positive integer, "label": allowed-stage }` objects. Label every usable packet-array event once; preserve array order. |
| `failure_modes` | Array of one or more allowed failure-mode strings. Use multiple labels only when each is directly observable. |

Allowed stages: `understanding`, `exploration`, `localization`,
`implementation`, `validation`, `debugging`, `closing`.

Allowed failure modes: `premature_implementation`, `repeated_exploration`,
`ineffective_debugging_loop`, `insufficient_validation`, `missed_constraint`,
`premature_completion`, `tool_misuse`, `empty_termination`,
`file_corruption`, `none_observed`, `unscorable`.

## Decision guide

Stages describe what an individual action is doing:

- **understanding** — reads/interprets requirements or an error that explains
  the task.
- **exploration** — lists files or otherwise surveys the workspace.
- **localization** — reads the candidate implementation or narrows a concrete
  defect location.
- **implementation** — writes or replaces the candidate artifact.
- **validation** — runs a candidate-side test, compilation, import, or direct
  behavior check. Harness verification is not visible here and never counts.
- **debugging** — reacts to a failed/contradictory check by inspecting or
  revising the attempted solution.
- **closing** — terminal response/stop with no additional work.

Failure modes describe an observable trajectory pattern, not whether the
solution ultimately passed:

- **premature_implementation**: writes before enough task/target inspection to
  ground the change.
- **repeated_exploration**: repeats listing/reading without narrowing or
  progressing to a change.
- **ineffective_debugging_loop**: repeats essentially the same edit/check
  cycle without responding to its result.
- **insufficient_validation**: changes an artifact but performs no meaningful
  candidate-side check afterward.
- **missed_constraint**: an explicit visible requirement is ignored in a
  visible action or write.
- **premature_completion**: stops while a plainly necessary next step remains
  (for example, inspection only with no implementation).
- **tool_misuse**: malformed, invalid, or clearly inappropriate tool request.
- **empty_termination**: terminal provider response has no visible content
  where a completion would normally be expected.
- **file_corruption**: a write visibly truncates, mangles, or makes the target
  unusable.
- **none_observed**: no failure mode above is observable. Do not combine it
  with any other failure label.
- **unscorable**: the packet is absent/corrupt or too incomplete to judge. Do
  not combine it with any other failure label; report it as-is.

## Quick workflow

1. Read the trajectory in order and assign a stage to each usable entry.
2. Add only directly observable failure labels. Do not guess correctness from
   an absent final result.
3. Repeat for all 24 packets (about 3–5 minutes each; allow roughly 1.5–2
   hours total, including a consistency pass).
4. Save the JSONL file at the path above and tell the research agent it is
   ready. The agent will validate completeness and schema before computing
   agreement.

Most common confusions: exploration is broad workspace discovery while
localization targets the candidate code/defect; validation is an actual command
or direct behavior check, not merely reading code; debugging requires a
response to evidence from a prior check. A failed command alone is not an
ineffective debugging loop, and an empty visible final message alone does not
prove task failure.
