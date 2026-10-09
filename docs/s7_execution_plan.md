# S7 formal benchmark: pre-execution plan

Date: 2026-10-09. This is a documentation-only pre-execution plan. It does
not authorize a model call, inspect a test-task solution, or alter a frozen
task, verifier, fixture, or skill. S7 may start only after the user confirms
the final scope and this plan is converted into an immutable execution lock.

## Aim and scope

S7 has one confirmatory core: collect cross-model baselines for C0 (no skill)
and C1 (the frozen v0 skill). Skill v1 and L3b are exploratory conditions.
They are reported only with their mechanism-activation rates and descriptive
outcomes; neither can support an intervention-efficacy claim on its own.

The task pool is already frozen and admission-complete:

| split | tasks | status |
|---|---:|---|
| `test_in` | 12 (six A, six B) | 12/12 admitted; not run |
| `test_out` | 6 (six C) | 6/6 admitted; not run |
| total | 18 | 18/18 admitted; not run |

Each scheduled cell uses three fresh repetitions. The task, rather than an
individual repetition, is the inferential sampling unit; repetitions estimate
within-task random variation.

## Model panel and execution paths

| model | role | planned runner | sampling status |
|---|---|---|---|
| `qwen3.5:9b` | weak target | r2 direct SoC path | request temperature 0.5; record accepted request settings |
| `gemma4:26b` | cross-model model | r2 direct SoC path | same |
| `qwen3.8:27b` | medium model | r2 direct SoC path | same |
| `qwen3-coder-next` | specialized model | r2 direct SoC path | same |
| `llama3.1:8b` | lower-bound model | r2 direct SoC path | same |
| `gpt-5.6-sol` | reference anchor | Codex path unless direct API credentials are confirmed | reference anchor; sampling is not controlled by r2 |

For r2, a seed is sent only if the endpoint supports it. Metadata preserves
both the requested value and whether the transport accepted or echoed it; no
seed is described as effective without an endpoint echo. GPT remains clearly
labelled as a Codex-run reference anchor with uncontrolled sampling unless a
direct API credential is explicitly made available. Historical Codex CLI
artifacts are legacy evidence and are never pooled with r2 observations.

## Conditions and matrix

All runs use the frozen 18-task test pool and three repetitions.

| condition | exact content | status | runs per model | all six models |
|---|---|---|---:|---:|
| C0 | no skill protocol | core | 54 | 324 |
| C1 | matching frozen v0 skill (A/B/C) | core | 54 | 324 |
| v1 | matching frozen v1 skill | exploratory | 54 | 324 if fully crossed |
| L3b | frozen v0 skill plus the locked call-32 reminder | exploratory | 54 | 324 if fully crossed |

Thus the fixed core is **648 scheduled runs**. Two mutually exclusive,
unselected exploratory scopes are documented for the user's later choice:

| proposed scope | added exploratory runs | total scheduled runs |
|---|---:|---:|
| no exploratory test condition | 0 | 648 |
| v1 and L3b for `qwen3.5:9b` only | 108 | 756 |
| v1 and L3b fully crossed across all six models | 648 | 1,296 |

No token or currency estimate is part of this protocol.

## C0/C1 prompt construction

Both conditions use identical task text, system/tool schema, clean workspace,
tool-call cap (40), context budget, command timeout, process-group timeout,
verifier, retry policy, model request fields, and final-instruction suffix:

> Read `task.md`, fix the implementation, and validate your result. Do not
> create or modify benchmark-owned verifier files.

C1 prepends only the applicable frozen v0 document, delimited as a benchmark
skill protocol. C0 omits that delimited protocol block entirely. There is no
replacement prose, additional encouragement, or condition-specific tool
instruction in C0. This makes the presence versus absence of the v0 protocol
the sole intended C0/C1 prompt difference.

Before execution, the exact serialized C0 and C1 prompt templates and hashes
will be added to the lock manifest. The test-task content itself will not be
used to revise either template.

## Execution and metadata rules

For r2, preserve the currently locked controls: requested temperature 0.5,
at most 40 tool calls, 65,536-token conservative context estimate, commands
limited to 120 seconds, and a 20-minute process-group timeout. A transport
failure with no response may make up to three total attempts with fixed
exponential backoff; received model content, verifier failures, maximum-step
events, and timeouts are never retried. Exhaustion is recorded as
`provider_error`.

Every run records runner version, condition, prompt and skill hashes,
requested/accepted sampling settings, seed evidence, worker concurrency,
retry timestamps, raw responses, finish reason, tool-call parsing, usage, and
non-exclusive outcome flags. `provider_error` is excluded from the primary
pass-rate denominator and retained in the task-level report; a sensitivity
view includes it in the denominator as a non-pass.

## Analysis plan

1. Report `test_in` and `test_out` separately; do not pool them.
2. Aggregate repetitions within each task-condition first. C0/C1 comparisons
   use a task-level paired bootstrap across the 18 matched task units (and
   separately by split). Repetitions are not treated as independent benchmark
   tasks.
3. Wilson intervals describe an individual proportion only (for example pass,
   provider error, maximum-step, or activation rate). They are not used as a
   test of a between-condition difference.
4. For C1, report the pre-specified skill-activation field and stratified
   descriptive outcomes for activated versus non-activated trajectories. The
   operational activation parser and its version are locked before the first
   S7 run.
5. Report partial score both as absolute verifier fraction and as delta from
   each task's frozen no-op baseline. Outcome flags (`final_empty`, `no_edit`,
   `compile_error`, `verifier_fail`, `timeout`, `context_overflow`,
   `provider_error`, and `max_steps_reached`) remain non-exclusive.
6. v1 and L3b, if selected, remain exploratory. Their report is limited to
   activation and descriptive trajectories/outcomes; it does not make an
   efficacy claim. Such a claim would in any case require both mechanism
   activation and observable improvement.

## Single-run freeze and gate

S7 is run once. Immediately before the first run, tag the exact r2 runner,
all v0/v1 skill files, L3b protocol, task/verifier/fixture manifests, prompt
templates, matrix, and analysis code in a single execution-lock commit and
Git tag. After that point no condition, task, split, sampling setting,
concurrency, or analysis definition may be modified.

The remaining gate is user confirmation of: (1) whether exploration is absent,
weak-model-only, or fully crossed; and (2) whether a direct API credential for
`gpt-5.6-sol` exists. Until then, this repository remains in planning-only
status and no test split may be run.
