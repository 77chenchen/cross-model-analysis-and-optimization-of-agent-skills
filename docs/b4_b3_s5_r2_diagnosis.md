# B4: r2 Qwen dev-baseline terminal-path diagnosis

This diagnosis reads the completed B3 S5 r2 artifacts only. It does not modify
tasks, verifiers, fixtures, or skills, and it is not used to create an
intervention in this stage.

## Main result

The r2 runs do not reproduce the old CLI's missing-tool-call ambiguity:
all observed tool calls parsed successfully. The 36 terminal paths separate
into provider errors, runner max-step exits, and final-response exits. Eight
provider-error outcomes contain an explicit LaaS HTTP 502. These should not
be attributed to the skill or model strategy.

Several legacy `empty_termination` outcomes have high partial score because
the model made edits and then reached the 40-call limit without an assistant
final message. In particular, this includes all three A06 runs and two A05
runs, each with 40 valid tool calls. Therefore `final_empty` is an observation
flag, not evidence that no work occurred; `terminal_path=max_steps` is the
needed explanatory field.

The remaining verifier failures occur after normal, parseable tool use and
are the appropriate candidates for later specification/implementation
analysis. The task-level report should continue to show A04 both included and
excluded due to its known task defect.

## Consequence

Do not write a v2 text skill solely to address the combined 28/36 non-pass
count. The observed non-passes mix provider 502s, call-budget exhaustion, and
specification failures. A subsequent intervention decision should first choose
whether a fixed runtime budget/finalization guard is an independently
evaluated condition; it must not be silently folded into a skill-text change.

Machine-readable signals are in `data/diagnostics/b4_b3_s5_r2/`.
