# Formal harness contract

The formal runner must create a fresh workspace from an immutable task template, execute one agent run, invoke a verifier owned by the benchmark, archive all artifacts, then destroy the workspace. No run may reuse another run's modified state.

All model conditions use the same tool schema, 64K context cap, max-step limit, timeout, tool-output truncation, and agent scaffold. For every run, save the exact returned model ID and all fields defined by `metadata/run.schema.json`.

GPT runs use the normal Codex CLI profile. Non-GPT runs use `codex exec --profile soclaas --model <exact-model-id>`. The SoC LaaS profile is external configuration and must obtain its credential from `SOCLAAS_API_KEY`; the key is never written to repository files or logs.
## Pilot runner contract

Use `./harness/run_pilot.sh <pilot_task_id> <exact_model_id> <gpt|soclaas> [v0|v1]`.
It creates a new workspace for one run, retains the raw CLI JSONL trajectory,
runs the external verifier, and writes `metadata.json` plus normalized
`actions.jsonl`. The task must already have a template and verifier; test
splits are deliberately unsupported by this runner.

The optional skill version defaults to `v0`. A D5 comparison must supply the
version explicitly and use fresh timestamped workspaces; the chosen version
and its SHA-256 hash are recorded in `metadata.json`.

`./harness/run_d5_pilot.sh` executes the frozen qwen3.5:9b D5 calibration
matrix and writes a TSV that records every runner exit, including expected
external-verifier failures.

For SoC LaaS, the runner starts a login `zsh` so the user's local
`SOCLAAS_API_KEY` can be inherited without being read, logged, or written to
the repository.
