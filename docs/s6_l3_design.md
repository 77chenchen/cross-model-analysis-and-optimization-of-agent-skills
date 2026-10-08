# S6 L3 runtime guardrail design

This is an independent runtime condition, not Skill A/B v2. It responds to
the D5.5 finding that empty termination and tool-mediated file damage were
not plausibly solvable by stronger text alone.

The initial v0-guided turn runs normally. The runner then hashes the candidate
workspace and compiles Python sources. If no source change is observed, or
compilation fails, it opens one bounded repair turn in the same workspace.
The repair notice says which guardrail fired but never exposes verifier output.
Repeated error markers add a fallback instruction to simplify the direct edit
and run one focused check. There is at most one repair turn, so failures remain
observable rather than being retried until pass.

The first evaluation is only `dev_validate`, gemma4:26b, with three fresh
repetitions on its six locked tasks. L3 changes the harness condition and must
never be interpreted as a text-skill comparison.
