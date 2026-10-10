# B5-r2 blinded human failure-mode review

Open only `packet_001.json` through `packet_024.json` in
`data/b5_r2_human_review/`. Do not open `data/b5_r2_blinded_annotations/`,
`data/b5_r2_blinded_packets/`, or any original run directory.

Create `data/b5_r2_human_review/human_annotations.jsonl`: exactly one JSON
object per line, one per packet, with no Markdown or comments.

```json
{"run_id":"packet_001","annotator_id":"human_reviewer_01","blinded":true,"stage_events":[],"failure_modes":["none_observed"]}
```

| Field | Required format |
|---|---|
| `run_id` | Exact packet ID, `packet_001` through `packet_024`. |
| `annotator_id` | Your stable non-empty identifier. |
| `blinded` | Literal JSON boolean `true`. |
| `stage_events` | Literal empty array `[]`; stages are out of scope. |
| `failure_modes` | Non-empty array of allowed strings; no duplicates. |

Allowed labels: `premature_implementation`, `repeated_exploration`,
`ineffective_debugging_loop`, `insufficient_validation`, `missed_constraint`,
`premature_completion`, `tool_misuse`, `file_corruption`, `none_observed`,
`unscorable`.

`empty_termination` is not an available human label: it is mechanically
computed from terminal logs and excluded from agreement.

Use labels only for visible behavior, never for whether you think the solution
passed:

- **premature_implementation**: writes before enough task/target inspection.
- **repeated_exploration**: repeated listing/reading with no progress.
- **ineffective_debugging_loop**: repeated, unresponsive edit/check cycle.
- **insufficient_validation**: edits but has no meaningful later candidate-side check.
- **missed_constraint**: visible explicit requirement is ignored.
- **premature_completion**: stops while a plainly necessary next step remains.
- **tool_misuse**: malformed, invalid, or clearly inappropriate tool request.
- **file_corruption**: a write visibly truncates or mangles the target.
- **none_observed**: no above issue; use it alone.
- **unscorable**: packet absent/corrupt/too incomplete; use it alone.

One failed command is not automatically an ineffective debugging loop. An
empty final response is not a human failure label. Expect roughly 1–2 minutes
per packet, plus a consistency pass (about 30–45 minutes total).

When done, run:

```sh
python3 harness/check_b5_r2_human_review.py
```

It must report `"valid": true`. Then tell the research agent the file is
ready; agreement is not computed until that validation succeeds.
