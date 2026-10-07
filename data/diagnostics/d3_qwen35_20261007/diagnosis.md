# D3 non-blinded trajectory diagnosis — qwen3.5:9b pilot batch (2026-10-07)

Scope: the four D2 pilot runs of exact model ID `qwen3.5:9b`
(provider `soclaas`) recorded in D2 commit `db37c39`. These are
**calibration data only**: no cross-model ranking, no causal claim, and
no formal dev/test conclusion may be drawn from this batch. All four
external verifiers failed; that is the retained experimental outcome and
is not treated here as evidence that the skill protocol is ineffective.

Annotator: non-blinded Codex agent (`annotator_id: d3-codex-agent`,
`blinded: false` in every annotation). The annotator knew the model
identity; these are not blinded human annotations. Sequence numbers refer
to the `sequence` field of each run's `actions.jsonl`.

## Run 1 — pilot_a03_record_deduplication (Skill A)

- Verifier outcome: `passed: false`; checks `normalization: true`,
  `no_mutation: false`, then exception
  `TypeError("argument of type 'NoneType' is not a container or iterable")`.
- Direct technical cause of the verifier failure: the candidate
  `deduplicate.py` appends the **original** dict by reference
  (`result.append(r)`) instead of a new dictionary, so
  `answer[0] is not original[0]` fails the `no_mutation` check. The
  verifier then crashed on the `invalid` input (`[{...}, None, ...]`)
  because the candidate only guards missing/None IDs, not non-mapping
  records: `"id" not in None` raises `TypeError`, which aborted the
  remaining checks (`invalid`, `order`).
- Checkpoints: inspect **observed** (seq5 `cat task.md`, seq7
  `cat deduplicate.py`); implement **observed** (seq9–22 rewrite
  `deduplicate.py` via repeated shell heredoc/echo/printf attempts;
  workspace file differs from the frozen seed); validate **observed**
  (seq23–26 two candidate-side validation attempts, both failed with
  Python syntax errors in the generated validation script itself).
- Earliest observable failure stage: **implement**. The first write
  attempt (seq9, `cat > deduplicate.py` heredoc) already produced the
  flawed by-reference design; seq11/13/15 were malformed attempts to
  rewrite the file and failed with syntax/indentation errors in the
  shell-embedded Python. Validation attempts (seq23/25) never executed
  because the generated validation scripts did not parse.
- Hypotheses for skill improvement:
  - The v0 protocol's "run the relevant validation" step is not
    operationalized enough for this model: the agent generated
    validation scripts inline in shell with heavy quoting, which
    repeatedly produced unparseable code. A protocol that prescribes
    writing the candidate file and a separate small test file with
    simple quoting (or `apply_patch`-style file edits) may reduce
    shell-quoting breakage.
  - The model's core defect here is a *spec-completeness* miss
    (by-reference append; no non-mapping guard), not tooling: even a
    working validation run against the spec would likely have caught
    the `no_mutation`/`invalid` gaps. A skill hint to "test every
    constraint sentence in the task statement" could be evaluated.

## Run 2 — pilot_a05_version_parser (Skill A)

- Verifier outcome: `passed: false`, checks empty, exception
  `IndentationError('expected an indented block after function
  definition on line 1', ...)` when importing the workspace
  `version_parser.py`.
- Direct technical cause: the workspace file is a 3-line uncompilable
  stub (`def parse_version(value):` followed only by a comment and a
  blank indented line). The first full write (seq11, `cat > ... << 'EOF'`)
  produced garbled, non-functional code; the second write (seq13,
  `cat > ... << 'ENDOFFILE'`) overwrote the file with a truncated
  2-line stub — both heredocs completed with exit 0, so the shell never
  signalled the problem.
- Checkpoints: inspect **observed** (seq5 `ls`, seq7 `cat task.md`,
  seq9 `cat version_parser.py`); implement **observed** (seq11 and seq13
  both rewrote `version_parser.py`); validate **not_observed** — after
  re-reading the stub (seq15) the agent emitted an empty
  `agent_message` (seq17) and the turn ended (seq18). No candidate-side
  validation command was attempted.
- Earliest observable failure stage: **implement** (first write at seq11
  was already broken). The *turn-ending* failure — stopping with an
  uncompilable file and no validation — is also notable.
- Hypotheses for skill improvement:
  - The model failed to notice its own file corruption after the
    truncated heredoc. A skill checkpoint "after editing, re-read or
    compile the file (`python3 -m py_compile`) before declaring
    done" directly targets this observed gap.
  - Large code generation inside a single shell heredoc was fragile
    (garbled first attempt). Splitting generation into smaller edits
    plus a mandatory parse check is a candidate protocol change to
    evaluate later.

## Run 3 — pilot_b03_duplicate_audit (Skill B)

- Verifier outcome: `passed: false`; checks `duplicates: false`,
  `invalid: true`; no exception.
- Direct technical cause: the workspace `audit.py` is **byte-identical
  to the frozen buggy seed** (`def duplicate_ids(records): return []`)
  — verified by diff against
  `tasks/pilot/pilot_b03_duplicate_audit/template/audit.py`. The
  unmodified stub returns `[]`, so the `duplicates` check fails
  (expected non-empty list). The `invalid` check passes only by
  coincidence (empty list equals the expected empty result for
  all-ignorable input).
- Checkpoints: inspect **observed** (seq3/seq7 `cat task.md`, seq5
  `ls -la`, seq9 `cat audit.py`); implement **not_observed** — no file
  modification occurred in the workspace; validate **not_observed**.
- Earliest observable failure stage: the run ended right after
  inspection. At seq11 the agent emitted an empty `agent_message` and
  the turn completed (seq12) with no edit attempted. This is an
  early-termination/abstention pattern, not a defective implementation.
- Hypotheses for skill improvement:
  - For Skill B v0 ("inspect ... perform the required transformation,
    generate the requested artifact, and validate"), the model stopped
    after the inspect phase. A stronger completion criterion in the
    protocol ("do not end the turn until the target file has been
    modified and a validation command has been run") would convert
    this abstention into a testable behavior.
  - The empty final message suggests the model produced no answer text
    at all; whether this reflects the SoC endpoint, the scaffold, or
    the model is not distinguishable from this single run.

## Run 4 — pilot_b05_date_validation (Skill B)

- Verifier outcome: `passed: false`; check `dates: false`; no exception.
- Direct technical cause: the workspace `dates.py` is **byte-identical
  to the frozen buggy seed** (`def valid_dates(values): return
  list(values)`) — verified by diff against
  `tasks/pilot/pilot_b05_date_validation/template/dates.py`. The
  unmodified stub returns every input unfiltered, so the `dates`
  check fails.
- Checkpoints: inspect **observed** (seq5 `ls -la`, seq7 `cat task.md`,
  seq9 `cat dates.py`); implement **not_observed** — no workspace file
  modification; validate **not_observed**.
- Earliest observable failure stage: same early-termination pattern as
  B03 — after the last inspect command (seq10) the agent emitted an
  empty `agent_message` (seq11) and the turn completed (seq12).
- Hypotheses for skill improvement:
  - Identical to B03: the v0 Skill B protocol may need an explicit
    "no ending before modification + validation" completion gate for
    this model class.
  - B03 and B05 sharing the same stop pattern (two Skill B runs, same
    model) is the main calibration signal of this batch, but with two
    runs it is only a lead, not a conclusion.

## Cross-run notes (calibration only)

- No infrastructure interruption in any run: all four trajectories end
  in `turn.completed`; no reruns were performed. The `mcp_tool_call
  failed` events at the start of three runs (A03 seq4, A05 seq4, B05
  seq4) are failed attempts to read nonexistent MCP resources and did
  not stop the turn.
- Pattern summary: 2/4 runs (A03, A05, Skill A) attempted edits; both
  left the workspace in a failing state (one logically wrong, one
  syntactically uncompilable). 2/4 runs (B03, B05, Skill B) stopped
  after inspection with the workspace unmodified and an empty final
  message. This is four single-run observations on one weak-model
  pilot condition; no ranking, causal, or formal benchmark claim
  follows.
- No credentials, API keys, or environment values appear in any
  analyzed artifact; none were recorded here.
