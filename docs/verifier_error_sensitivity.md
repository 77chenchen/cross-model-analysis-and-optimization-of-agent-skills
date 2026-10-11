# Verifier no-named-check sensitivity

This local-only sensitivity excludes eligible runs where `verifier.json` has no named checks and `passed` is false. It does not replace the preregistered primary outcome, which retains such runs as failures.

## Composition

Categories are mutually exclusive within the no-named-check subset. `verifier_exception_or_abnormal_exit` is a nonempty verifier error not matching timeout or parsing patterns; no non-zero agent-process exits were observed in this subset, so the non-zero entries are verifier exceptions. `output_unparseable` uses a literal parse/decode marker in that error. Zero values are retained for clarity.

| Model | Condition | Eligible n | Verifier timeout | Verifier exception / abnormal exit | Output unparseable | No named check, passed=false | Total excluded |
|---|---|---:|---:|---:|---:|---:|---:|
| qwen3.5:9b | C0 | 89 | 0 | 4 | 0 | 1 | 5 |
| qwen3.5:9b | C1 | 89 | 0 | 4 | 0 | 1 | 5 |
| gemma4:26b | C0 | 54 | 0 | 6 | 0 | 0 | 6 |
| gemma4:26b | C1 | 54 | 0 | 5 | 0 | 0 | 5 |
| qwen3.8:27b | C0 | 54 | 0 | 2 | 0 | 0 | 2 |
| qwen3.8:27b | C1 | 54 | 0 | 2 | 0 | 0 | 2 |
| qwen3-coder-next | C0 | 54 | 0 | 4 | 0 | 0 | 4 |
| qwen3-coder-next | C1 | 54 | 0 | 5 | 0 | 0 | 5 |
| llama3.1:8b | C0 | 54 | 0 | 0 | 0 | 0 | 0 |
| llama3.1:8b | C1 | 54 | 0 | 0 | 0 | 1 | 1 |
| gpt-5.6-sol | C0 | 54 | 0 | 2 | 0 | 0 | 2 |
| gpt-5.6-sol | C1 | 54 | 0 | 3 | 0 | 0 | 3 |

## Sensitivity pass rates and task-paired difference

The condition rows give verifier-pass rates after the exclusion. The difference row averages within-task C1-minus-C0 repeat pass rates over tasks with at least one retained run in both conditions; its interval is a fixed-seed 10,000-draw paired bootstrap and is descriptive.

| Model | Row | Primary n | Excluded | Sensitivity n | Pass n | Pass rate | C1-C0 task pp [95% bootstrap] |
|---|---|---:|---:|---:|---:|---:|---|
| qwen3.5:9b | C0 | 89 | 5 | 84 | 43 | 51.2% | |
| qwen3.5:9b | C1 | 89 | 5 | 84 | 45 | 53.6% | |
| qwen3.5:9b | C1-C0 paired tasks (n=18) | | | | | | +0.9 [-8.9, +10.0] |
| gemma4:26b | C0 | 54 | 6 | 48 | 33 | 68.8% | |
| gemma4:26b | C1 | 54 | 5 | 49 | 36 | 73.5% | |
| gemma4:26b | C1-C0 paired tasks (n=16) | | | | | | +6.2 [+0.0, +16.7] |
| qwen3.8:27b | C0 | 54 | 2 | 52 | 45 | 86.5% | |
| qwen3.8:27b | C1 | 54 | 2 | 52 | 46 | 88.5% | |
| qwen3.8:27b | C1-C0 paired tasks (n=18) | | | | | | +1.9 [-3.7, +7.4] |
| qwen3-coder-next | C0 | 54 | 4 | 50 | 33 | 66.0% | |
| qwen3-coder-next | C1 | 54 | 5 | 49 | 34 | 69.4% | |
| qwen3-coder-next | C1-C0 paired tasks (n=17) | | | | | | +3.9 [-7.8, +17.6] |
| llama3.1:8b | C0 | 54 | 0 | 54 | 0 | 0.0% | |
| llama3.1:8b | C1 | 54 | 1 | 53 | 0 | 0.0% | |
| llama3.1:8b | C1-C0 paired tasks (n=18) | | | | | | +0.0 [+0.0, +0.0] |
| gpt-5.6-sol | C0 | 54 | 2 | 52 | 44 | 84.6% | |
| gpt-5.6-sol | C1 | 54 | 3 | 51 | 44 | 86.3% | |
| gpt-5.6-sol | C1-C0 paired tasks (n=17) | | | | | | +2.0 [+0.0, +5.9] |

## Five-case artifact versus verifier review

This is a manual, descriptive audit of five existing exception cases; no task,
fixture, verifier, model run, or judge call was changed. “Task/verifier
interface defect” means the frozen task text describes a direct value/list/text
argument while the frozen contract invokes `transform` with an operation
wrapper dictionary. “Model-produced artifact” means the candidate conflicts
with that frozen contract independently of such a mismatch.

| Run | Frozen task and contract evidence | Candidate artifact / error | Assessment |
|---|---|---|---|
| `s7-qwen3-5-9b-test_in_b11_bucket-C0-r4` | Task says bucket a nonnegative integer; contract calls with `{op: "bucket", value: 10}`. | Candidate compares the whole request with `0`; verifier raises `TypeError: '<' not supported between dict and int`. | Task/verifier interface defect exposed by a task-literal implementation; not attributable solely to the model artifact. |
| `s7-gemma4-26b-test_out_c02_sessions-C0-r1` | Task says “from events”; contract calls with `{op: "sessions", events: [...]}`. | Candidate iterates the wrapper, then calls `.get` on string keys; verifier raises `AttributeError: 'str' object has no attribute 'get'`. | Task/verifier interface defect exposed by a task-literal implementation; not attributable solely to the model artifact. |
| `s7-qwen3-coder-next-test_in_a09_header-C1-r2` | Task specifies header text; contract calls with `{op: "header", text: " X-Id : abc "}`. | Candidate calls `.split` on the wrapper; verifier raises `AttributeError: 'dict' object has no attribute 'split'`. | Task/verifier interface defect exposed by a task-literal implementation; not attributable solely to the model artifact. |
| `s7-qwen3-5-9b-test_out_c01_inventory-C0-r3` | Contract supplies wrapper fields `rows` and `reorder`. | Candidate uses an invalid `getattr(...)(['rows'])` expression and does not implement the contract’s global `reorder`; verifier raises `TypeError: unhashable type: 'list'`. | Model-produced artifact under the frozen contract. |
| `s7-qwen3-5-9b-test_in_b09_phone-C1-r1` | Contract supplies wrapper field `text`; candidate itself branches for dictionary input. | Candidate’s normalization branch is incomplete and does not return the prescribed normalized value; verifier raises `TypeError: 'str' object cannot be interpreted as an integer`. | Model-produced artifact under the frozen contract. |

The five cases show that this aggregate category mixes frozen task/verifier
interface defects with candidate artifacts. Excluding all such failures is
therefore not a neutral correction and is reported only as an optimistic
sensitivity analysis.
