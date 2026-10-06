# Cross-Model Agent Skill Trajectory Benchmark

## Scope

This code-repair pilot evaluates the same `code_repair_v0` skill on GPT-6.1-Sol, GPT-6-Luna, and GPT-5.5. Every completed run starts from an independent buggy task copy and is scored by benchmark-controlled `unittest` modules.

## Main result

Across `cr_02`--`cr_04`, each model completed three primary repetitions per task with a 100% external-test success rate. Success alone therefore does not distinguish the models.

| Model | Mean completed shell commands | Mean trajectory events |
|---|---:|---:|
| GPT-6.1-Sol | 4.78 | 18.44 |
| GPT-6-Luna | 4.33 | 18.22 |
| GPT-5.5 | 11.89 | 37.22 |

The GPT-5.5 trajectories are about 2.5--2.8 times longer by completed command count. Manual trace inspection attributes the difference to repeated workspace discovery, repeated reads, and failed interpreter selection followed by recovery.

## Reliability note

Nine initial `cr_04` launches were interrupted before any tool call by a transient platform quota refusal. They were rerun under the identical settings and all nine replacement runs passed. The raw attempt history remains in Git; the primary analysis uses the completed `rep_01`--`rep_03` runs.

## Reproduction

Run one task-model-repetition combination:

```bash
bash run_task.sh cr_02 gpt-6.1-sol 01
```

Then rebuild result tables:

```bash
python3 analysis/summarize_runs.py
python3 analysis/aggregate_results.py
```

The full Chinese LaTeX narrative report is delivered separately as `benchmark_report.tex`; `assets/trajectory-concept.png` is an explanatory image, not a quantitative chart.
