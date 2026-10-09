# S7 execution-lock manifest template

Status: **template only; not an execution lock**. Date: 2026-10-09.

This checklist is completed, hashed, committed, and tagged only after the
user authorizes construction of the S7 execution lock. Empty fields are a
blocker, not permission to substitute a later value.

## Locked protocol

- [ ] Scope: 870 runs: qwen3.5:9b C0/C1/v1/L3b at five repetitions; five
  other models C0/C1 at three repetitions.
- [ ] C0/C1 core: 720 runs; weak-model exploratory runs: 150.
- [ ] `test_in`: 600 runs; `test_out`: 270 runs.
- [ ] GPT-5.6 Sol uses Codex as a reference anchor and is labelled
  `sampling_uncontrolled` in metadata, tables, and reports.
- [ ] v1 is restricted to A/B `test_in`; L3b uses v0 and covers both splits.
- [ ] Task is the statistical unit; repetitions estimate within-task variation.
- [ ] Provider-error primary denominator excludes exhausted transport errors;
  sensitivity denominator includes them as non-passes.
- [ ] Task defects follow the immutable erratum/no-replacement/two-view rule.

## Runner and outcome artifacts

- [ ] Formal runner patch identifier: `TBD`.
- [ ] `harness/r2_agent.py` SHA-256: `TBD`.
- [ ] Formal test-run entry point SHA-256: `TBD`.
- [ ] Formal runner test-suite command and passing result: `TBD`.
- [ ] Tool schema version and SHA-256: `TBD`.
- [ ] `verifier_timeout_s: 1200`.
- [ ] `verifier_timeout` is recorded independently and also implies the
  non-exclusive `timeout` outcome flag: `TBD` implementation hash.
- [ ] Retry policy, 40-step cap, 65,536 context estimate, command timeout,
  and process-group timeout: `TBD` configuration hash.

## Prompt, skill, task, and schedule artifacts

- [ ] Serialized C0 prompt template and SHA-256: `TBD`.
- [ ] Serialized C1 prompt template and SHA-256: `TBD`.
- [ ] Frozen v0/v1 skill file hashes, including the v1 A/B-only applicability
  map: `TBD`.
- [ ] Frozen L3b protocol hash: `TBD`.
- [ ] Task/template/verifier/fixture manifest hashes: `TBD`.
- [ ] Activation parser version: `skill-activation-heuristic-v1`; parser
  implementation hash and tests: `TBD`.
- [ ] No-op partial-score baseline manifest and hash: `TBD`.
- [ ] Schedule generator hash and balancing-check report hash: `TBD`.
- [ ] Schedule seed and TSV SHA-256 for each model:
  - [ ] qwen3.5:9b / 351009 / `TBD`
  - [ ] gemma4:26b / 426009 / `TBD`
  - [ ] qwen3.8:27b / 382709 / `TBD`
  - [ ] qwen3-coder-next / 303509 / `TBD`
  - [ ] llama3.1:8b / 318109 / `TBD`
  - [ ] gpt-5.6-sol / 560009 / `TBD`

## Analysis and reporting artifacts

- [ ] Task-level paired bootstrap implementation and hash: `TBD`.
- [ ] Per-task pass-distribution and floor/ceiling report implementation: `TBD`.
- [ ] Trajectory-metric implementation and hash: `TBD`.
- [ ] Blinded LLM-judge sampling and packet generator hashes: `TBD`.
- [ ] Human-review sampling plan: `TBD`.
- [ ] Result tables separate test-in/test-out, include/exclude erratum tasks,
  and provider-error denominator views: `TBD`.

## Final validation

- [ ] All `TBD` values resolved before the first run.
- [ ] Lock commit SHA: `TBD`.
- [ ] Lock tag: `TBD`.
- [ ] No test run exists before this tag.
