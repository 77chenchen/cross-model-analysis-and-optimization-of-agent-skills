# D1 provider and function-calling preflight

This directory contains one minimal, non-benchmark smoke run for each selected model. Each model received the same request: invoke the shell once to run `pwd`, then report the observed directory.

| Requested model ID | Provider profile | JSONL events | Completed shell calls | Status |
|---|---|---:|---:|---|
| `gpt-5.6-sol` | default Codex CLI | 8 | 1 | passed |
| `qwen3.8:27b` | `soclaas` | 7 | 1 | passed |
| `qwen3.5:9b` | `soclaas` | 7 | 1 | passed |
| `gemma4:26b` | `soclaas` | 7 | 1 | passed |
| `llama3.1:8b` | `soclaas` | 7 | 1 | passed |
| `qwen3-coder-next` | `soclaas` | 7 | 1 | passed |

SoC LaaS runs are launched through a login shell so that the locally configured `SOCLAAS_API_KEY` is inherited by the Codex CLI. Credentials are not included in any artifact. These runs establish provider and tool connectivity only; they are excluded from formal pilot and benchmark analyses.
