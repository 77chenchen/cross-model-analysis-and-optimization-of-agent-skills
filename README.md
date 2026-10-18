<a id="english"></a>
<p align="right"><strong>English</strong> &nbsp;|&nbsp; <a href="#zh">中文</a></p>

# How Written Skills Change Coding-Agent Performance?

Research question: when a coding agent receives a written skill, does it repair repository defects more successfully across models? Even when final pass rates do not change, does the skill alter how the agent reads, edits, and validates code?

## Key findings

- Across eight model configurations, the C1 effect is model dependent. The clearest positive result is GLM-5.3-Flash: verifier pass rises from 40/54 (74.1%) under C0 to 48/54 (88.9%) under C1, a task-paired gain of 14.8 percentage points with a 95% bootstrap interval of [3.7, 29.6] points ([S7_T1_model_condition_summary.csv](results/tables/s7/S7_T1_model_condition_summary.csv); [S7_T2_core_paired_differences.csv](results/tables/s7/S7_T2_core_paired_differences.csv)).
- For the weak target, qwen3.5:9b, C1 reduces the task-level rate of validation after the final edit by 25.0 percentage points while increasing verifier pass by 1.9 percentage points ([S7_T7_process_paired.csv](results/tables/s7/S7_T7_process_paired.csv); [S7_T2_core_paired_differences.csv](results/tables/s7/S7_T2_core_paired_differences.csv)).
- Ornith1.5:35b passed 45/52 usable C0 runs (86.5%) and 44/52 usable C1 runs (84.6%); its task-paired C1−C0 estimate was −1.9 percentage points with a 95% paired-bootstrap interval of [−16.7, 9.3] points ([Ornith completed summary](results/tables/s7/S7_T8_ornith_completed_summary.md)).
- For GLM-5.3-Flash, C1 also raises task-paired post-edit validation by 22.2 percentage points and increases the median trajectory from five to six tool calls. It is the clearest case in this panel where the fixed skill changes the prescribed process and improves verified repair.
- The central question is therefore not only whether a skill improves pass rate, but whether it changes the path through reading, writing, validating, and terminating. For qwen3.5:9b, C1 produces 25.0 percentage points less post-edit validation, slightly longer trajectories, and more rewrites and repeated actions; verifier pass moves from 48.3% to 50.6%. Relative to C1, v1 is explicitly referenced in 80% of runs and raises post-edit validation by 45.0 percentage points, yet does not change verifier pass ([S7_T4_process_metrics.csv](results/tables/s7/S7_T4_process_metrics.csv); [S7_T5_activation.csv](results/tables/s7/S7_T5_activation.csv); [S7_T6_exploratory.csv](results/tables/s7/S7_T6_exploratory.csv); [S7_T7_process_paired.csv](results/tables/s7/S7_T7_process_paired.csv)).
- A separate fresh-task mechanism study completed 192 qwen3.5:9b runs on 24 newly admitted development tasks. Relative to a length-matched generic prompt, C1, an externalized procedure, and trajectory imitation changed task-paired verifier pass by +6.25, 0.00, and +4.17 percentage points; all 95% paired-bootstrap intervals included zero. The externalized procedure nevertheless increased post-edit rereading by 31.3 points, directly reproducing the separation between workflow change and verified repair ([S8-b results](docs/s8b_results.md); [paired outcome table](results/tables/s8b/S8B_T2_task_paired_differences.csv)).

## Results at a glance

[![Eight-model verifier pass rates with model logos](figures/s7/verifier_pass_rates_by_model.png)](figures/s7/verifier_pass_rates_by_model.pdf)


### Fresh-task mechanism result

[![Fresh-task process variants](paper/figures/s8b_mechanism.png)](paper/figures/s8b_mechanism.pdf)

The left panel reports task-paired pass-rate differences from the length-matched generic control; the middle panel reports condition-level verifier pass; the right panel reports task-paired changes in validation and rereading.

## Paper

Read the complete report as a [PDF](paper/main.pdf) or inspect the [LaTeX source](paper/main.tex).

## Repository map

```text
config/           Locked protocol, prompt, split, runner, and schedule configuration.
tasks/            Frozen synthetic repair tasks, fixtures, manifests, and admission records.
harness/          Direct-agent runner, schedule execution, admission, and diagnostic utilities.
analysis/         Versioned outcome accounting, summaries, tests, table, and figure generators.
data/release/     De-identified released trajectory-derived records and their manifest.
results/tables/   Machine-readable tables, including formal S7 tables in results/tables/s7/.
figures/          Reproducible figures, plotting data, QA artefacts, and figure manifests.
docs/             Protocol locks, diagnostics, errata, result notes, and future-study plans.
paper/            Two-column manuscript source, bibliography, figures, and compiled PDF.
skills/           Frozen written-skill variants used by the experimental conditions.
```

## Research progression

### 1. Start with verifiable repository repairs

We used repository-repair tasks to capture complete trajectories of file reading, code editing, and test execution while retaining reproducible external evaluation. Each task contains a frozen buggy repository, a natural-language task specification, test fixtures, and a contract verifier. Scoring depends only on whether the modified code satisfies the task contract, not on the model's final natural-language response.

The formal task pool contains 18 tasks: 12 `test_in` tasks from Skill A/B and six `test_out` tasks from transfer category C. Before model evaluation, every task had to pass three admission checks: the expected fix passed, the buggy seed failed, and known shortcut solutions failed. The task split and admission results are recorded in the [split lock](docs/s3_split_lock.md), [task manifest](tasks/formal_manifest.json), and [admission record](tasks/s3_admission.json).

### 2. Check whether the model–task pairs leave room for an effect

Early pilot runs at temperature 0 were retained as a separate queue. We then tested which sampling parameters each model endpoint supported and ran calibration tasks across multiple models. Calibration identified model-task combinations near floor or ceiling effects, where the available range is too limited to estimate the effect of a skill reliably.

The calibration designated qwen3.5:9b as the weak target model and llama3.1:8b as the lower capability boundary. Stronger general-purpose and code models completed the comparison panel. See the [sampling probe](docs/s0_sampling_probe.md), [calibration protocol](docs/s4_calibration_protocol.md), and [calibration results](docs/s4_calibration_results.md).

### 3. Fix the runner and the definition of success

Early CLI runs showed that an empty final response and verifier success were not mutually exclusive. Timeouts, missing edits, tool errors, and verifier failures could also occur together, so a single terminal label could not describe an execution outcome adequately.

For directly accessible models, we used the locked r2 agent loop with a fixed tool set, a 40-step limit, process-group timeouts for command execution, and request-level retries only when a transport error returned no response. The runner recorded model responses, reasoning fields, tool calls, and tool results at every step. GPT was executed through Codex and reported separately as a sampling-uncontrolled reference anchor.

The primary outcome is read directly from `verifier.json.passed`. Retry-exhausted provider errors are excluded from the primary denominator; timeouts and `max_steps_reached` remain in the denominator and count as failures. The implementation and correction history are in the [runner design](docs/b1_r2_runner.md), [outcome-flag specification](docs/outcome_flags_revision.md), [verifier-pass erratum](docs/verifier_pass_erratum_20261010.md), and [analysis patch](docs/s7_verifier_pass_analysis_patch_20261010.md).

### 4. Use weak-model failures to decide what to test

We diagnosed qwen3.5:9b trajectories individually, separating failures that written instructions might address, such as missed constraints and absent post-edit validation, from file corruption, interface errors, and premature termination.

This diagnosis produced two development conditions:

- `v1` explicitly specified an inspect-edit-validate workflow.
- `L3b` injected one fixed reminder after the 32nd tool call to test a late-stage runtime guardrail.

Relative to C1, `v1` increased post-edit validation by 45.0 percentage points but left verifier pass unchanged. `L3b` was followed by some behavioral changes, although the relevant strata were small and differences were also present in the baseline stratum. The supporting records are the [trajectory diagnosis](docs/s4_qwen35_diagnosis.md), [`v1` record](docs/d4_intervention.md), [`L3b` results](docs/l3b_results.md), and [metric reconciliation](docs/l3b_metric_reconciliation.md).

### 5. Run the locked eight-model comparison

The core comparison used two conditions:

- C0 omitted the skill text.
- C1 included the frozen v0 skill.

Apart from the skill block, the task specification, tool definitions, verifier, runner, prompt suffix, and scheduling rules were held constant. qwen3.5:9b ran five times in each task-condition cell; the other seven models ran three times. `v1` and `L3b` were retained as exploratory conditions for the weak target model.

Tasks, conditions, and repetitions were interleaved using fixed-seed schedules rather than executed in condition-specific blocks. This reduced confounding from execution time and changes in provider state. Statistical analysis treated the task, not the repeated run, as the sampling unit. The full evaluation matrix contained 1,086 runs: 936 in the C0/C1 core comparison and 150 in the two exploratory conditions. Exact settings are available in the [execution plan](docs/s7_execution_plan.md), [execution lock](config/s7_execution_lock.yaml), and [schedule record](docs/s7_schedule_chain_20261010.md).

### 6. Read correctness and behavior as two different outcomes

Repeated runs were first summarized within each task-condition cell. We then calculated task-paired C1−C0 differences for each model. Verifier pass rate was the task outcome; post-edit validation, post-edit rereading, whole-file rewrites, debugging loops, tool steps, and terminal flags were reported as separate process metrics.

The C1−C0 difference varied across models:

- GLM-5.3-Flash increased from 40/54 passes under C0 to 48/54 under C1. The task-paired difference was +14.8 percentage points, with a 95% paired-bootstrap interval of [3.7, 29.6]; post-edit validation also increased by 22.2 percentage points.
- qwen3.5:9b gained 1.9 percentage points in verifier pass while post-edit validation decreased by 25.0 percentage points.
- Ornith1.5:35b had a difference of −1.9 percentage points, with a 95% paired-bootstrap interval of [−16.7, 9.3].
- llama3.1:8b remained at the capability floor under both conditions.

These results show that the observed effect of a skill depends on the underlying model and that process-level behavioral change cannot substitute for direct evaluation of functional correctness.

The main evidence is in the [condition summary](results/tables/s7/S7_T1_model_condition_summary.csv), [paired pass-rate table](results/tables/s7/S7_T2_core_paired_differences.csv), [process summary](results/tables/s7/S7_T4_process_metrics.csv), [paired process table](results/tables/s7/S7_T7_process_paired.csv), [figures](figures/s7/), and [paper](paper/main.pdf).

### 7. Repeat the mechanism comparison with new tasks and better controls

The mechanism experiment added 24 independently admitted tasks and compared four prompt conditions on qwen3.5:9b:

1. C1;
2. an externalized step-by-step procedure;
3. trajectory imitation; and
4. a length-matched generic prompt.

Each task-condition cell was repeated twice, producing 192 scheduled runs. The length-matched generic prompt controlled for prompt length and nonspecific additional text. The externalized procedure and trajectory-imitation conditions tested explicit rule specification and behavioral demonstration, respectively.

Relative to the length-matched generic prompt, the task-paired pass-rate differences were +6.25 percentage points for C1, 0.00 for the externalized procedure, and +4.17 for trajectory imitation. All three 95% paired-bootstrap intervals included zero. The externalized procedure increased post-edit rereading by 31.3 percentage points, with a 95% interval of [+14.6, +47.9]. These results further show that prompt interventions can produce measurable process-level behavioral changes without demonstrating improved functional repair performance.

See the [analysis plan](docs/s8b_analysis_plan_20261015.md), [execution lock](config/s8b_execution_lock.yaml), [result note](docs/s8b_results.md), [condition summary](results/tables/s8b/S8B_T1_condition_summary.csv), [paired outcomes](results/tables/s8b/S8B_T2_task_paired_differences.csv), [process contrasts](results/tables/s8b/S8B_T5_process_paired_differences.csv), and [figure](paper/figures/s8b_mechanism.pdf).

## Reproduction

Run all commands from the repository root. 
### Environment

Python 3.14.0 was used. Python 3.11 or newer is the intended baseline; the pinned plotting stack is in [analysis/requirements-figures.txt](analysis/requirements-figures.txt).

<pre><code>python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r analysis/requirements-figures.txt</code></pre>

Expected time: typically 1–3 minutes, depending on package-cache availability.

### Reproduce released analysis and figures

<pre><code>python -m analysis.make_tables
python analysis/check_paper_numbers.py
python -m unittest analysis.test_figures
python -m analysis.make_s7_figures
python analysis/s8b_paper_analysis.py
python paper/make_paper_figures.py --figure s8b</code></pre>

Expected outputs are refreshed Markdown/CSV tables under [results/tables/](results/tables/), a successful cross-check against [results/tables/s7/](results/tables/s7/), six figure tests, five held-out figures plus a contact sheet under [figures/s7/](figures/s7/), and the fresh-task mechanism figure at [paper/figures/s8b_mechanism.pdf](paper/figures/s8b_mechanism.pdf). In the isolated-clone check, the original held-out sequence took under one minute after dependency installation.


### Re-run the experimental schedule

This creates new run artifacts and must use a new cohort/output location; it must not overwrite or be pooled with S7. Open-weight runs require <code>SOCLAAS_API_KEY</code> in the environment. GPT uses the local authenticated Codex CLI and has no repository-stored credential. Do not put credentials, raw responses, or reasoning payloads in Git.

<pre><code>export SOCLAAS_API_KEY
python harness/run_s7_schedule.py config/s7_schedules/qwen3_5_9b.tsv \
  --output-root data/new_cohort_runs --execute

# GPT reference-anchor schedule only
python harness/run_s7_codex_schedule.py config/s7_schedules/gpt_5_6_sol.tsv \
  --output-root data/new_cohort_runs --execute</code></pre>

These are audit entry points, not commands for reproducing the locked S7 cohort. They cannot be meaningfully run from a clean public clone without local provider access, the required Codex login for GPT, and explicit authorization for a new cohort. The direct runner specification is [here](docs/b1_r2_runner.md); the frozen original schedules are in [config/s7_schedules/](config/s7_schedules/).



## License

Source code is licensed under MIT. Released data, figures, tables, and documentation are licensed under CC BY 4.0. See [LICENSE](LICENSE).



---

<a id="zh"></a>
<p align="right"><a href="#english">English</a> &nbsp;|&nbsp; <strong>中文</strong></p>

# Written Skill 如何影响Coding Agent？

研究问题：给coding agent加入一段skill后，它在不同模型上会不会更容易修好仓库中的缺陷；即使最终通过率不变，它的阅读、修改和验证路径又会怎样变化。

## 核心结论

- 八个模型配置表明，C1 的作用取决于模型。最清楚的正向结果来自 GLM-5.3-Flash：C0 通过 40/54（74.1%），C1 通过 48/54（88.9%）；按任务配对的提升为 14.8 个百分点，95% bootstrap 区间为 [3.7, 29.6]（[S7_T1_model_condition_summary.csv](results/tables/s7/S7_T1_model_condition_summary.csv)、[S7_T2_core_paired_differences.csv](results/tables/s7/S7_T2_core_paired_differences.csv)）。
- 对弱目标模型 qwen3.5:9b，C1 使“最终一次编辑后再验证”的任务级比例降低 25.0 个百分点，通过率增加 1.9 个百分点（[S7_T7_process_paired.csv](results/tables/s7/S7_T7_process_paired.csv)、[S7_T2_core_paired_differences.csv](results/tables/s7/S7_T2_core_paired_differences.csv)）。
- Ornith1.5:35b 在 C0 下通过 45/52 条可用运行（86.5%），在 C1 下通过 44/52 条（84.6%）；按任务配对的 C1−C0 为 −1.9 个百分点，95% 配对 bootstrap 区间为 [−16.7, 9.3]（[Ornith 完成结果](results/tables/s7/S7_T8_ornith_completed_summary.md)）。
- 对 GLM-5.3-Flash，C1 还使按任务配对的“最终编辑后验证”增加 22.2 个百分点，并使中位工具调用数从 5 增加到 6。它是当前面板中最清楚的“skill 同时改变执行过程并提高修复通过率”的案例。
- 本研究的核心不只在于“skill 有没有提高通过率”，还在于检验：**即使最终通过率没有明显变化，skill 是否会改变智能体读取代码、写入文件、执行验证以及结束任务的路径。** 对 qwen3.5:9b，C1 与 v1 都观察到了这类轨迹层变化，C1 相对 C0：编辑后的验证行为减少了 25.0 个百分点，同时平均轨迹略长，并出现更多重写和重复动作；通过率从 48.3% 到 50.6%。
v1 相对 C1：v1 明确要求编辑后验证，模型对该指令的显式引用达到 80%，编辑后验证行为增加 45.0 个百分点；但通过率没有变化。（[S7_T4_process_metrics.csv](results/tables/s7/S7_T4_process_metrics.csv)、[S7_T7_process_paired.csv](results/tables/s7/S7_T7_process_paired.csv)）。
- 独立的新任务机制实验在 24 个新准入的开发任务上完成了 192 条 qwen3.5:9b 运行。与等长通用提示相比，C1、外显流程和轨迹模仿的任务配对通过率差分别为 +6.25、0.00 和 +4.17 个百分点，三个 95% 配对 bootstrap 区间都跨过 0；但外显流程使编辑后重读增加 31.3 个百分点。这直接说明：提示可以改变执行流程，却不一定提高最终修复通过率。见 [S8-b 结果](docs/s8b_results.md)和[配对结果表](results/tables/s8b/S8B_T2_task_paired_differences.csv)。

## 主结果与论文

完整报告见 [PDF](paper/main.pdf) 与 [LaTeX 源码](paper/main.tex)。主图：[PNG](paper/figures/main_results.png) / [矢量 PDF](paper/figures/main_results.pdf)。


### 新任务机制结果

[![新任务流程条件结果](paper/figures/s8b_mechanism.png)](paper/figures/s8b_mechanism.pdf)

左图是各流程条件相对等长通用提示的任务配对通过率差；中图是各条件的 verifier 通过率；右图是验证与重读行为的任务配对变化。

## 目录

```text
config/           已锁定的实验协议、提示模板、数据划分、runner 与调度配置。
tasks/            冻结的合成修复任务、初始缺陷版本、测试夹具、清单和准入记录。
harness/          智能体运行、调度执行、任务准入和轨迹诊断工具。
analysis/         结局口径、统计汇总、单元测试、表格和图形生成代码。
data/release/     去标识化的轨迹派生数据及其完整性清单。
results/tables/   机器可读的结果表；正式 S7 表位于 results/tables/s7/。
figures/          可复现图、对应绘图数据、版式 QA 记录和图形清单。
docs/             协议锁、诊断报告、勘误记录、结果说明与后续研究方案。
paper/            论文源码、参考文献、论文专用图和已编译的 PDF。
skills/           各实验条件使用的、在锁定后不再改动的skill
```

## 研究设计与实施

### 1. 可验证 Repository-Repair Tasks 的构建

实验采用 repository-repair tasks，以同时获得完整的 file reading、code editing 与 trajectories，并支持 external verifier 的可重复验收。每个任务均包含冻结的 buggy repository、natural-language task specification、test fixtures 和 contract verifier。评分仅依据修改后的代码是否满足 task contract，不使用模型的 final natural-language response。

正式 task pool 包含 18 个任务，其中 12 个 `test_in` 任务属于 Skill A/B，6 个 `test_out` 任务属于 transfer category C。模型评估前，每个任务均须通过三项 admission checks：expected fix 通过、buggy seed 失败、known shortcut solution 失败。任务划分与检查结果见[数据划分锁](docs/s3_split_lock.md)、[任务清单](tasks/formal_manifest.json)和[准入记录](tasks/s3_admission.json)。

### 2. Model–Task Difficulty Calibration

temperature=0 的早期 pilot runs 作为独立队列保留。随后检查不同 model endpoint 对 sampling parameters 的支持情况，并使用多种模型运行 calibration tasks。Calibration 的目的是识别接近 floor effect 或 ceiling effect 的 model–task combinations，避免使用缺乏可辨识变化空间的任务估计 skill 的作用。

根据 calibration 结果，qwen3.5:9b 被设定为 weak target model，llama3.1:8b 用于表征更低的 capability floor，同时纳入更强的 general-purpose models 与 code models 构成比较 panel。详细过程见[采样探测](docs/s0_sampling_probe.md)、[校准协议](docs/s4_calibration_protocol.md)和[校准结果](docs/s4_calibration_results.md)。

### 3. Auditable Execution Harness 与 Primary Outcome

早期 CLI runs 表明，final response 为空与 verifier pass 并非互斥事件；timeout、no edit、tool error 和 verifier failure 也可能同时发生。因此，单一 terminal label 无法完整表示一次运行的 outcome。

对于可直接调用的模型，实验采用锁定的 r2 agent loop：固定 tool set 和 40-step limit，command execution 使用 process-group timeout；仅对未收到任何 response 的 transport errors 实施 request-level retry，并逐步记录 model response、reasoning field、tool calls 与 tool results。GPT 通过 Codex 运行，并作为 sampling-uncontrolled reference anchor 单独报告。

Primary outcome 直接读取 `verifier.json.passed`。Retry-exhausted provider errors 排除在 primary denominator 之外；timeout 和 `max_steps_reached` 均计入分母并视为失败。具体实现与修订记录见[runner 设计](docs/b1_r2_runner.md)、[结局标志说明](docs/outcome_flags_revision.md)、[verifier-pass 勘误](docs/verifier_pass_erratum_20261010.md)和[分析补丁](docs/s7_verifier_pass_analysis_patch_20261010.md)。

### 4. 基于 Weak-Model Trajectories 的 Intervention Design

对 qwen3.5:9b 开展逐 trajectory diagnosis，将 missed constraint、缺少 post-edit validation 等可能受 written skill 影响的失败，与 file corruption、interface error 和 premature termination 区分。

基于该 diagnosis 设置两个 development conditions：

- `v1`：显式规定 inspect–edit–validate workflow；
- `L3b`：在第 32 次 tool call 后注入一次固定 reminder，用于检验 late-stage runtime guardrail。

相较于 C1，`v1` 使 post-edit validation 增加 45.0 percentage points，但 verifier pass rate 保持不变。`L3b` 触发后观察到部分 behavioral changes，但相应 stratified sample 较小，且 baseline stratum 中同样存在差异。相关材料见[轨迹诊断](docs/s4_qwen35_diagnosis.md)、[`v1` 记录](docs/d4_intervention.md)、[`L3b` 结果](docs/l3b_results.md)和[指标对账](docs/l3b_metric_reconciliation.md)。

### 5. 八模型 Locked Controlled Evaluation

核心对比为 C0 与 C1：

- C0：不包含 skill text；
- C1：加入冻结的 v0 skill。

除 skill block 外，task specification、tool definitions、verifier、runner、prompt suffix 和 scheduling rules 均保持一致。qwen3.5:9b 在每个 task–condition cell 中重复 5 次，其余七个模型重复 3 次；`v1` 与 `L3b` 作为 weak-model exploratory conditions 保留。

Tasks、conditions 与 repetitions 采用 fixed-seed interleaved scheduling，不按 condition 分块运行，以降低 execution time window 与 provider state 变化造成的 confounding。Statistical analysis 以 task 为 sampling unit，不将 repeated runs 视为相互独立的样本。

完整 evaluation matrix 包含 1,086 条 runs，其中 936 条属于 C0/C1 core comparison，150 条属于两个 exploratory conditions；完整设置见[执行方案](docs/s7_execution_plan.md)、[执行锁](config/s7_execution_lock.yaml)和[调度记录](docs/s7_schedule_chain_20261010.md)。

### 6. Task Success 与 Process Behavior 的分离评估

Repeated runs 首先在每个 task–condition cell 内汇总，随后计算各模型 task-paired 的 C1−C0 difference。Verifier pass rate 作为 task outcome；post-edit validation、post-edit rereading、whole-file rewrite、debugging loop、tool steps 和 terminal flags 作为独立 process metrics 报告。

C1−C0 difference 呈现明显的 model heterogeneity：

- GLM-5.3-Flash 的通过数由 C0 的 40/54 增至 C1 的 48/54，task-paired difference 为 +14.8 percentage points，95% paired-bootstrap interval 为 [3.7, 29.6]；post-edit validation 同时增加 22.2 percentage points。
- qwen3.5:9b 的 verifier pass rate 增加 1.9 percentage points，而 post-edit validation 减少 25.0 percentage points。
- Ornith1.5:35b 的 difference 为 −1.9 percentage points，95% paired-bootstrap interval 为 [−16.7, 9.3]。
- llama3.1:8b 在 C0 与 C1 下均处于 capability floor。

这些结果表明，skill 的 observed effect 具有明显的 model dependence，process-level behavioral changes 不能替代对 functional correctness 的直接评价。

主要数据见[模型与条件汇总](results/tables/s7/S7_T1_model_condition_summary.csv)、[任务配对通过率差](results/tables/s7/S7_T2_core_paired_differences.csv)、[过程指标](results/tables/s7/S7_T4_process_metrics.csv)、[过程指标配对差](results/tables/s7/S7_T7_process_paired.csv)、[正式图表](figures/s7/)和[论文](paper/main.pdf)。

### 7. Fresh-Task Mechanism Comparison

Mechanism experiment 新增 24 个 independently admitted tasks，并在 qwen3.5:9b 上比较四种 prompt conditions：

1. C1；
2. externalized step-by-step procedure；
3. trajectory imitation；
4. length-matched generic prompt。

每个 task–condition cell 重复 2 次，共形成 192 条 scheduled runs。Length-matched generic prompt 用于控制 prompt length 与 nonspecific text addition；externalized procedure 与 trajectory imitation 分别用于检验 explicit rule specification 和 behavioral demonstration。

相较于 length-matched generic prompt：

- C1 的 task-paired pass-rate difference 为 +6.25 percentage points；
- externalized procedure 的 difference 为 0.00 percentage points；
- trajectory imitation 的 difference 为 +4.17 percentage points。

三个 95% paired-bootstrap intervals 均包含 0。Externalized procedure 使 post-edit rereading 增加 31.3 percentage points，95% interval 为 [+14.6, +47.9]。

结果进一步表明，prompt intervention 可以产生可测量的 process-level behavioral changes，但这种变化本身不能证明 functional repair performance 得到改善。

完整材料见[分析方案](docs/s8b_analysis_plan_20261015.md)、[执行锁](config/s8b_execution_lock.yaml)、[结果说明](docs/s8b_results.md)、[条件汇总](results/tables/s8b/S8B_T1_condition_summary.csv)、[任务配对结果](results/tables/s8b/S8B_T2_task_paired_differences.csv)、[过程指标配对差](results/tables/s8b/S8B_T5_process_paired_differences.csv)和[结果图](paper/figures/s8b_mechanism.pdf)。

## 复现：

以下命令均从仓库根目录运行。

### 建立环境

实际验证使用 Python 3.14.0；

<pre><code>python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r analysis/requirements-figures.txt</code></pre>


### 从发布内容重建表格与图形

<pre><code>python -m analysis.make_tables
python analysis/check_paper_numbers.py
python -m unittest analysis.test_figures
python -m analysis.make_s7_figures
python analysis/s8b_paper_analysis.py
python paper/make_paper_figures.py --figure s8b</code></pre>

预期产物包括：更新后的 [results/tables/](results/tables/) Markdown/CSV、针对 [results/tables/s7/](results/tables/s7/) 的数值一致性检查、6 项图形测试、[figures/s7/](figures/s7/) 中的 5 张保留测试图与 contact sheet，以及 [paper/figures/s8b_mechanism.pdf](paper/figures/s8b_mechanism.pdf) 中的新任务机制图。原保留测试命令在依赖安装后的隔离克隆中运行时间不足 1 分钟。



### 启动一个新的实验队列

下列命令会创建新的运行记录。开源模型需要在环境中配置 <code>SOCLAAS_API_KEY</code>；GPT 通过本地已登录的 Codex CLI 运行。

<pre><code>export SOCLAAS_API_KEY
python harness/run_s7_schedule.py config/s7_schedules/qwen3_5_9b.tsv \
  --output-root data/new_cohort_runs --execute

# 仅用于 GPT 参考锚点的调度
python harness/run_s7_codex_schedule.py config/s7_schedules/gpt_5_6_sol.tsv \
  --output-root data/new_cohort_runs --execute</code></pre>
公开克隆如果没有本地 provider 权限、GPT 的 Codex 登录状态和针对新队列的明确授权，就无法完成实验。直接 runner 的设计见 [docs/b1_r2_runner.md](docs/b1_r2_runner.md)，原始冻结调度见 [config/s7_schedules/](config/s7_schedules/)。



## 许可证

代码采用 MIT 许可证；已发布的数据、图表和文档采用 CC BY 4.0。详见 [LICENSE](LICENSE)。
