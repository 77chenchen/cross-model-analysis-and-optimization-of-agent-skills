# S5 descriptive trajectory cases

These non-blind case summaries are selected after the blinded-label pass.
They are illustrative dev-only examples, not independent evidence of an
intervention effect. “Strong” denotes the GPT-5.6 reference run and “weak”
denotes the selected gemma4:26b target run.

| task | reference observation | target observation | observable fork point |
|---|---|---|---|
| A02 config parser | GPT run `...e8af08084e` passed all 5 verifier checks after reading task/code, making a structured file change, and switching from unavailable `python` to `python3` validation. | gemma run `...c7e96cfcc1` ended `empty_termination`. | The target repeatedly wrote ad-hoc test content before a completed implementation/validation cycle; the reference re-ran validation with the available interpreter after its first command issue. |
| A03 record deduplication | GPT run `...c2e2cce4b5` passed after task/code inspection, a structured file change, and custom behavioral checks. | gemma run `...34db72c20a` was `verifier_fail`. | Both trajectories inspected and edited, but only the reference has a completed post-edit behavioral-check sequence recorded before completion. |
| A06 path safety | GPT run `...a58643b695` passed after inspection, structured editing, compilation and temporary-directory behavior checks. | gemma run `...4d7ace1135` ended `empty_termination`. | The target issued a long series of rewrites to an ad-hoc test file; the reference moved from the candidate implementation to compile/behavior checks. |
| B03 duplicate audit | GPT run `...d1b7fe2c00` passed after inspection, structured editing, compilation and edge-case checks. | gemma run `...009e0c517e` was `verifier_fail`. | The target did execute a local test after editing, but the external verifier still failed; this is a counterexample to treating “a validation command occurred” as sufficient. |

The observed reference behavior in these examples is not an unobserved
reasoning claim: it consists only of recorded inspect/edit/validation actions.
The B03 pair is retained as the planned anomaly case because local validation
and external correctness diverged.
