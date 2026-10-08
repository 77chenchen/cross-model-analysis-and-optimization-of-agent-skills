# B3 r2 recalibration protocol

Date: 2026-10-08
Status: locked before B3 runs.

B3 repeats the descriptive S4 calibration under r2 on the five open-weight
models, all 12 locked pilot/dev tasks, and three fresh repetitions per
condition (180 observations). It uses frozen Skill v0, temperature 0.5, seed
20261008, and nonexclusive outcome flags. No test task is addressable.

GPT-5.6 cannot use r2 because no direct API credential is available. It stays
in the CLI-only, uncontrolled-sampling reference cohort and is not pooled into
the r2 selection or comparison.

After S4, the r2 S5 baseline will run only the pre-registered selected
open-weight target: it must have overall pass rate in [0.20, 0.80], then
maximizes the number of task conditions with pass rate in [0.20, 0.80]. Ties
choose lower overall pass rate, then lexical model ID. It will run every
locked pilot/dev task three times under r2. This selection rule is frozen
before results are read.
