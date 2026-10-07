# Alignment with the formal benchmark plan

## Retained as reusable infrastructure

- Immutable task seeds and per-run fresh workspaces.
- Raw JSONL trajectory retention and post-run external verification.
- Git-versioned runner, task source, verifier output, and aggregation code.
- Explicit classification of infrastructure interruptions instead of counting them as model failures.

## Reclassified as exploratory pilot only

The existing `cr_01`--`cr_04` tasks and all previous GPT-6.1-Sol, GPT-6-Luna, and GPT-5.5 runs remain available for runner debugging and task calibration. They are not part of the formal benchmark because they use the wrong model panel, have no A/B/C skill split, are not assigned to the locked `pilot/dev/test_in/test_out` splits, and do not yet collect all required metadata or adherence labels.

## Required changes for the formal benchmark

1. Use the locked six-model panel in `config/formal-benchmark.yaml` and record the exact returned model ID.
2. Create 36 frozen formal tasks: 10 dev, 14 test-in, and 12 test-out. Do not inspect test-out before the transformation is locked.
3. Separate visible task materials from verifier-owned checks, including positive, negative, and shortcut cases.
4. Record the full run metadata schema and standardize action types.
5. Instrument skill activation and observable checkpoint adherence.
6. Treat all current pilot results as calibration only; no claim about intervention effectiveness is permitted yet.

## D1 definition of done

- Harness contract and shared controls frozen.
- Skill A/B/C v0 files and task split protocol created.
- Verifier sanity protocol created.
- SoC LaaS CLI connectivity verified for the four non-GPT models.
- Candidate tasks admitted to `tasks/pilot/` only after verifier sanity checks.

## D1 freeze record (2026-10-07)

The 12-task pilot pool is now executable and admitted through the documented
positive/negative/shortcut checks in `tasks/pilot/admission.json`. The runner,
controls, action schema, annotation schema, and runtime fingerprint are
versioned in this repository. D1 is therefore frozen for pilot operation.

The annotation protocol is also frozen, but independent double annotation and
adjudication occur in D2 on the selected calibration trajectories. No formal
dev/test task has been created or inspected during D1.
