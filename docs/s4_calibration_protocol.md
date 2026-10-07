# S4 calibration protocol

S4 is descriptive calibration, not formal inference or a model ranking.  It
uses frozen Skill v0 on all six configured models and all twelve frozen pilot
tasks.  The locked sampling policy calls for three fresh repetitions per
model-task condition (216 planned runs). Tasks are the eventual statistical
unit; repetitions only expose within-task variation.

`harness/run_calibration.sh` creates a unique, timestamped workspace under
`data/calibration_runs/` for every invocation. It invokes the S2 timeout and
outcome machinery and retains failed artifacts.  `harness/summarize_calibration.py`
emits a run-level table with pass/outcome, partial score, action count and all
provider-reported token fields. Cost is intentionally null when no reliable
provider price/card is available; it must not be estimated from unverified
rates.

The runner requests a maximum of 40 tool steps in the prompt and logs the
configured 20-minute hard timeout. The current CLI still does not expose a
verified temperature, seed, context-limit, or native max-step override. This
limitation is retained in metadata rather than silently treated as controlled.
