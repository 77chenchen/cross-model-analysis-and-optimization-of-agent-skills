# Skill Trajectory Benchmark

Reproducible pilot infrastructure for comparing agent skills across models.

The first pilot is `code_repair/cr_01`: repair a parser while preserving its public API.
Each execution records the raw Codex JSONL event stream, a final message, a test result, and a normalized summary.
