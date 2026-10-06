# Pilot 1: Cross-model code repair

## Fixed conditions

- Task: `code_repair/cr_01`
- Skill: `code_repair_v0`
- Initial state: identical fresh copy of the buggy parser
- Oracle: `python3 -m unittest -v`
- Repetitions: one per model; this is a pilot, not a statistical comparison

## Result

| Model | Tests | Trajectory events | Effective command executions | Observation |
|---|---:|---:|---:|---|
| `gpt-6.1-sol` | 4/4 | 16 | 4 | Direct inspection, minimal patch, final validation. |
| `gpt-6-luna` | 4/4 | 18 | 4 | Same successful pattern; initially tried `python`, then recovered with `python3`. |
| `gpt-5.5` | 4/4 | 28 | 8 | Repeated discovery and reads; tried unavailable `python` twice before recovery. |

`effective command executions` counts completed shell commands once. The raw JSONL represents command start and completion as separate events, so it must not be counted directly as tool-call count.

## Interpretation

All models solved this easy task, so final success does not distinguish them. The weak model nevertheless showed avoidable exploration and recovery overhead. This makes it a useful calibration task but not sufficient evidence for a skill change. Subsequent tasks should require nontrivial localization and include task-specific acceptance commands in the skill to test whether explicit validation guidance reduces these inefficient trajectories.
