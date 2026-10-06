# Formal harness contract

The formal runner must create a fresh workspace from an immutable task template, execute one agent run, invoke a verifier owned by the benchmark, archive all artifacts, then destroy the workspace. No run may reuse another run's modified state.

All model conditions use the same tool schema, 64K context cap, max-step limit, timeout, tool-output truncation, and agent scaffold. For every run, save the exact returned model ID and all fields defined by `metadata/run.schema.json`.

GPT runs use the normal Codex CLI profile. Non-GPT runs use `codex exec --profile soclaas --model <exact-model-id>`. The SoC LaaS profile is external configuration and must obtain its credential from `SOCLAAS_API_KEY`; the key is never written to repository files or logs.
