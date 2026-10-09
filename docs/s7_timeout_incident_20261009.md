# S7 timeout incident and restart record

Date: 2026-10-09. During the first qwen3.5:9b schedule attempt, the eleventh
scheduled run (`s7-qwen3-5-9b-test_in_b09_phone-C1-r4`) exceeded the locked
20-minute process-group limit after host suspension. Its original wrapper used
`Popen.wait(timeout=...)`; the timeout budget did not catch up to elapsed wall
time after wake. At discovery, the run had lasted about 110 minutes.

The schedule and all preceding completed artifacts are unchanged. The partial
run's workspace, raw responses, and events are retained under
`data/s7_aborted_attempts/`; it has no `metadata.json`, no verifier result,
and is excluded from all analysis. It is not a provider-content retry record.

The only implementation correction changes the watchdog to poll UTC wall time
and terminate the child process group when elapsed wall time reaches 1,200
seconds, including immediately after wake. The S7 conditions, fixed schedule,
run ID, prompt, model request settings, and seed are unchanged. A new lock
tag supersedes the prior lock before restart. The resumed run uses the original
scheduled run ID and is the first complete observation for that cell, as
explicitly authorized by the user after this interruption.
