# S1 / D5.5 non-blinded diagnosis

All eight runs received their skill text through the runner; this establishes
injection, not behavioral adherence. Current raw JSONL does not expose an API
finish reason, context-overflow flag, or thinking-token split, so these fields
are `unknown`, never inferred from an empty message.

| Task | v0 observed pattern | v1 observed pattern | Interpretation of action change |
|---|---|---|---|
| A03 | 33 actions; repeated malformed writes; final SyntaxError | 8 actions; task read then empty termination | Earlier abandonment, not efficiency. |
| A05 | edit with incomplete suffix behavior; no validation | edit and reread; no validation; all verifier checks false | Partial behavioral shift, but no completed validation gate. |
| B03 | 37 actions; repeated broken shell generation; no useful result | 15 actions; inspect only then empty termination | Earlier abandonment, not efficiency. |
| B05 | attempted write leaves IndentationError; no validation | 9 actions; inspect only then empty termination | Earlier abandonment, not efficiency. |

## Classification

The D5 outcomes divide into two mechanisms. A05 contains a plausible
specification/strategy component: v1 caused an edit and reread, but did not
cause validation or correct behavior. A03, B03, and B05 exhibit either fragile
shell-mediated source generation or empty termination before work begins.
Those patterns are not well addressed by stronger text instructions alone.

## Recommendation

Do **not** write text Skill v2 now. The immediate next condition should be an
L3 runtime guardrail, designed and evaluated as a distinct condition: detect
an unchanged target before completion; run a post-edit syntax/import check;
and classify empty termination separately. This is motivated by the observed
process failures, not claimed to be effective. S2 must first supply the
timeout, outcome-category, partial-score, and finish-reason instrumentation
needed to evaluate that condition.
