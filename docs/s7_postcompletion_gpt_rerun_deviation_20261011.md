# S7 post-completion GPT rerun deviation

Date: 2026-10-11 (Asia/Singapore).

## What changed

The locked 870-run schedule initially completed with 104/108 GPT-5.6 Sol
reference-anchor records classified as protocol-level `provider_error`. Their
Codex logs reported an account usage-limit rejection; four GPT records were
usable. After S7 completion, the study owner explicitly instructed the
execution agent to discard those 104 active run directories and rerun them
under their original run IDs rather than retain a replacement cohort.

The first overwrite pass produced 62 usable records (49 verifier passes and 13
verifier failures) and 42 further usage-limit failures. After the five-hour
allowance reset, the remaining 42 run directories were overwritten again. The
active S7 tree now contains 108 usable GPT records: 88 verifier passes and 20
verifier failures, with zero GPT `provider_error` records.

Task text, frozen skills, C0/C1 prompt construction, verifier, schedule order,
run IDs, and repetition labels were unchanged. Codex sampling remained
uncontrolled. The five protocol-level provider errors remaining in S7 belong
to qwen3.5:9b and follow the preregistered primary/sensitivity denominator
rules.

## Consequence for interpretation

This owner-authorized overwrite is a deviation from the pre-execution rule
that S7 would run once and that failed samples would not be rerun. The original
104 GPT directories are not part of the active dataset or formal tables.
Therefore GPT remains a descriptive, sampling-uncontrolled reference anchor;
it cannot serve as a confirmatory controlled comparison. The five-model r2
core was not rerun and is unaffected by this deviation.

The formal report and every GPT figure mark this status. This note records the
deviation without changing any frozen task, verifier, skill, prompt template,
schedule, or r2 result.
