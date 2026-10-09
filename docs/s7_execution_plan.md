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

The task, rather than an individual repetition, is the inferential sampling
unit; repetitions estimate within-task random variation. `qwen3.5:9b` uses
five fresh repetitions in every assigned condition. Every other model uses
three repetitions in each core condition.

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

All assigned runs use the frozen 18-task test pool; the condition-specific
repetition counts are shown below.

| condition | exact content | status | qwen3.5:9b runs | each other model |
|---|---|---|---:|---:|
| C0 | no skill protocol | core | 18 × 5 = 90 | 18 × 3 = 54 |
| C1 | matching frozen v0 skill (A/B/C) | core | 18 × 5 = 90 | 18 × 3 = 54 |
| v1 | matching frozen v1 A/B skill | weak-model exploratory | 12 × 5 = 60 | not scheduled |
| L3b | frozen v0 skill plus the locked call-32 reminder | weak-model exploratory | 18 × 5 = 90 | not scheduled |

The v1 restriction is deliberate: frozen v1 exists only for Skills A/B, so it
does not apply to the six Skill-C `test_out` tasks. L3b uses v0 and does apply
to all 18 tasks.

The approved, fixed total is:

| component | `test_in` | `test_out` | total |
|---|---:|---:|
| qwen3.5:9b: C0, C1, v1, L3b | 240 | 90 | 330 |
| five other models: C0 and C1 | 360 | 180 | 540 |
| **all conditions** | **600** | **270** | **870** |

Of the 870 runs, the C0/C1 core is **720** (180 qwen3.5:9b plus 540 for the
other models); the weak-model exploratory portion is **150** (60 v1 plus 90
L3b). No token or currency estimate is part of this protocol.

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
non-exclusive outcome flags. It additionally records a separate
`verifier_timeout` flag: a verifier is stopped after **1,200 seconds**, and a
verifier timeout is a `timeout` outcome as well as `verifier_timeout: true`.
`provider_error` is excluded from the primary pass-rate denominator and
retained in the task-level report; a sensitivity view includes it in the
denominator as a non-pass.

## Interleaved deterministic schedule

Before execution, one schedule file is generated for each model from the
following fixed integer seeds:

| model | schedule seed |
|---|---:|
| `qwen3.5:9b` | 351009 |
| `gemma4:26b` | 426009 |
| `qwen3.8:27b` | 382709 |
| `qwen3-coder-next` | 303509 |
| `llama3.1:8b` | 318109 |
| `gpt-5.6-sol` | 560009 |

The schedule generator constructs every assigned task × condition × repetition
cell, assigns a deterministic unique `run_id`, and performs a seeded
stratified permutation. Its balancing checks require every condition, task,
and repetition to be distributed through the schedule rather than appearing
as a condition block. A completed `run_id` is skipped on resumption only when
its locked metadata and artifact-completeness check pass; every other entry is
continued in the original order. The generator, six TSV schedule files, their
SHA-256 digests, and the balancing-check report become execution-lock
artifacts. The schedules are not generated in this documentation stage.

For r2 direct runs, the concurrency is one unless a separately locked,
pre-execution transport analysis supports another value. GPT's Codex-anchor
runs are labelled `sampling_uncontrolled` in every table and report.

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
6. For each model separately, calculate the task-level paired C1-minus-C0
   difference and its bootstrap interval. Compare the weak model's difference
   with the other models only descriptively; do not make a significance claim.
7. Produce a task-level pass-distribution table. Mark every task that all
   models pass or all models fail, and discuss such ceiling/floor tasks as
   information-limited rather than evidence for a condition.
8. Automatically derive, for every run: steps, each available token field,
   first edit position, validation after editing, repeated-action rate,
   no-progress loop count, and `final_empty`. LLM-judge stage and pattern
   labels are collected only from a blinded, model-by-outcome stratified
   subsample; an independently blinded human-review subsample audits those
   labels. They are not collected for all trajectories.
9. v1 and L3b remain exploratory. Their report is limited to
   activation and descriptive trajectories/outcomes; it does not make an
   efficacy claim. Such a claim would in any case require both mechanism
   activation and observable improvement.

## Task-defect and erratum protocol

If S7 reveals a defect in an admitted task (including a task/verifier conflict,
a verifier error, or a verifier that does not terminate), do not modify the
task, verifier, fixture, schedule, or completed run. Register an immutable
erratum containing the evidence and affected run IDs. Every affected analysis
is then reported both with all scheduled tasks and with that task excluded.
There is no replacement run and no post-hoc task revision.

## Single-run freeze and gate

S7 is run once. Immediately before the first run, create an execution-lock
commit and Git tag. The accompanying manifest must include: the r2 formal-runner
patch identifier and hashes; `verifier_timeout_s=1200` and its outcome-flag
definition; all v0/v1 skills and the L3b protocol; task/verifier/fixture
manifests; the C0/C1 serialized prompt templates and SHA-256 hashes; the
skill-activation parser version and hash; schedule-generator and analysis-code
hashes; six schedules, seeds, and schedule hashes; and all controls above.
The existing pilot-only runner is not sufficient: the formal runner must be
implemented and reviewed before this lock, rather than silently reusing a
pilot entry point.

After the tag, no condition, task, split, sampling setting, concurrency, or
analysis definition may be modified. The only remaining gate is the user's
confirmation to build this execution lock and tag. Until then, this repository
remains in planning-only status and no test split may be run.
