# Methodology notes

## Design decisions adopted

1. Use deterministic, executable task oracles as the primary outcome rather than LLM judging.
2. Evaluate a full action trajectory in addition to final success: tool count, order, retries, validation, and time.
3. Keep model, prompt, tools, budget, and initial workspace constant within each task-model comparison.
4. Split tasks into development and held-out partitions before revising a skill, and report them separately.
5. Treat a skill change as successful only when weak-model improvement transfers to held-out tasks.

## Relevant work

- [AgentBench (ICLR 2024)](https://proceedings.iclr.cc/paper_files/paper/2024/hash/e9df36b21ff4ee211a8b71ee8b7e9f57-Abstract-Conference.html): supports multi-environment evaluation and shows large capability gaps among agent models.
- [TRAJECT-Bench (ICLR 2026)](https://openreview.net/pdf?id=TZWnWvsQ0X): motivates trajectory-level diagnostics beyond final-answer accuracy, including tool selection, arguments, and ordering.
- [SWE-bench](https://github.com/swe-bench): motivates executable evaluation for code-agent tasks using repository state and tests.

## Implication for this benchmark

The benchmark will treat test/validator success as the primary result. Trajectory metrics will explain model differences and motivate skill changes, rather than being used as a subjective substitute for correctness.
