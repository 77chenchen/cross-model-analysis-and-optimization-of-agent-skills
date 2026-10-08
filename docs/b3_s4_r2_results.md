# B3 S4 r2 calibration result

The locked 180-run matrix completed: five open-weight models, 12 pilot/dev
tasks, and three repetitions. Under the pre-registered selection rule,
`qwen3.5:9b` is the only eligible model and is selected for the r2 S5 baseline:
its overall pass rate is 0.306 and it has 3 task conditions with pass rate in
[0.20, 0.80].

Gemma4:26b has 0.806 overall pass rate and is therefore ineligible under the
locked upper bound despite one middle-rate task. Qwen3.8:27b (0.889) and
Qwen3-Coder-Next (0.833) are likewise ineligible; Llama3.1:8b is at 0.000.
This is a calibration selection, not a performance ranking. A04 remains a
known task defect and will be reported both included and excluded in later
descriptive summaries; it was not excluded from this pre-locked selection
rule.
