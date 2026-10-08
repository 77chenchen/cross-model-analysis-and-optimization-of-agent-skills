# S5 dev-only v0 baseline

S5 ran 72 fresh observations: GPT-5.6 and gemma4:26b on the 12 locked dev
tasks, with three repetitions per model-task condition. This is a dev-only
baseline, not held-out evaluation and not a model ranking.

| model | runs | passes | mean partial score | mean normalized events |
|---|---:|---:|---:|---:|
| GPT-5.6 | 36 | 33 | 0.972 | 22.78 |
| gemma4:26b | 36 | 26 | 0.896 | 23.47 |

The blinded LLM judge received 72 packets with model, provider, outcome,
verifier result, and final message withheld. All 72 annotations passed the
schema/identity boundary validation. Across 1,374 labelled trajectory events,
validation was the most frequent stage (0.301); the most frequent non-null
judge failure label was `tool_misuse` (17/72, 0.236). These are descriptive
blind-label frequencies, not causal effects or correctness judgements.

The automatically derived activation heuristic is reported only as a runner
signal, not as an independent blind annotation. It gave different rates across
models because it requires observable edit-plus-validation commands; this is a
measurement limitation to be audited during human review.

## Human review and agreement

A fixed, blinded sample of 24 packets (12 selected from each model before
copying) is prepared in `data/s5_manual_review/`. The reviewer receives only
the packets and must add one JSON object per line to
`human_annotations.jsonl`, using the same `run_id` packet ID and
`failure_modes` array as the S5 schema. Run
`python3 harness/score_s5_human_review.py` after all 24 labels are supplied;
it reports Cohen's kappa over packet-by-failure-mode binary decisions. Kappa
is intentionally not reported before independent human labels exist.
