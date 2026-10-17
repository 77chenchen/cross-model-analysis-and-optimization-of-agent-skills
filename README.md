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

The study developed in seven steps. The order is important: task validity and outcome accounting were settled before the formal skill comparison, and the later mechanism study used a new task set.

### 1. Start with verifiable repository repairs

We chose small repository-repair tasks because they expose the agent's full sequence of file reads, edits, and test commands. Each task has a frozen buggy repository, a written specification, fixtures, and an external contract verifier. This lets the verifier judge the code independently of the model's final explanation.

The formal pool has 18 tasks. Twelve `test_in` tasks belong to the A/B skill families, while six `test_out` tasks use transfer family C. Before any model was evaluated, every task had to accept the intended repair, reject the original buggy seed, and reject known shortcut solutions. The pool and its checks are recorded in the [split lock](docs/s3_split_lock.md), [task manifest](tasks/formal_manifest.json), and [admission record](tasks/s3_admission.json).

### 2. Check whether the model–task pairs leave room for an effect

The first pilots used temperature 0 and were kept separate. We then checked the sampling fields available on each execution path and ran a multi-model calibration. This was necessary because a task that every model passes, or no model can solve, says little about whether a written skill helps.

The calibration placed qwen3.5:9b in the weak-target role and llama3.1:8b at the lower boundary of the panel; stronger general and coding models filled out the comparison range. See the [sampling probe](docs/s0_sampling_probe.md), [calibration protocol](docs/s4_calibration_protocol.md), and [calibration results](docs/s4_calibration_results.md).

### 3. Fix the runner and the definition of success

The early CLI runs exposed an accounting problem. A run could end with no visible final message and still leave a correct repair, while timeouts, missing edits, tool errors, and verifier failures could overlap. A single terminal label could not represent these cases reliably.

For directly accessible models, we therefore used the locked r2 loop with a fixed tool set, a 40-step limit, process-group timeout, transport-only retries, and a step-by-step event log. GPT remained a Codex reference anchor. Success is read directly from `verifier.json.passed`; only retry-exhausted transport errors leave the primary denominator, while timeouts and step-limit runs remain failures. The implementation and correction history are in the [runner design](docs/b1_r2_runner.md), [outcome-flag specification](docs/outcome_flags_revision.md), [verifier-pass erratum](docs/verifier_pass_erratum_20261010.md), and [analysis patch](docs/s7_verifier_pass_analysis_patch_20261010.md).

### 4. Use weak-model failures to decide what to test

With the runner fixed, we read qwen3.5:9b trajectories to separate failures that instructions might address—such as a missed constraint or no validation after editing—from file corruption, interface errors, and early termination. This led to two development conditions. `v1` stated the inspect–edit–validate procedure more explicitly. `L3b` added a single fixed reminder after call 32 to test a simple late-trajectory guardrail.

`v1` raised post-edit validation by 45.0 percentage points relative to C1, but verifier pass did not change. `L3b` changed some behavior after the reminder fired, although the relevant strata were too small and differed at baseline. The supporting records are the [trajectory diagnosis](docs/s4_qwen35_diagnosis.md), [`v1` record](docs/d4_intervention.md), [`L3b` results](docs/l3b_results.md), and [metric reconciliation](docs/l3b_metric_reconciliation.md).

### 5. Run the locked eight-model comparison

The formal comparison used C0, which omitted the skill block, and C1, which added the frozen v0 skill. Everything else—the task text, tools, verifier, runner, suffix, and scheduling rules—was held fixed. qwen3.5:9b ran five times per task and condition; the other seven model configurations ran three times. `v1` and `L3b` were retained as weak-model exploratory conditions.

Tasks, conditions, and repetitions were mixed in deterministic schedules rather than run in separate blocks. This spreads each condition across the execution window and keeps the task, rather than the repeated run, as the statistical unit. The final schedule contained 1,086 runs: 936 in the C0/C1 comparison and 150 in the two exploratory conditions. All scheduled runs completed. Exact settings and progress are available in the [execution plan](docs/s7_execution_plan.md), [execution lock](config/s7_execution_lock.yaml), [schedule record](docs/s7_schedule_chain_20261010.md), and [run ledger](STATUS.md).

### 6. Read correctness and behavior as two different outcomes

For each model, repeated runs were averaged within task and condition before calculating the task-paired C1−C0 difference. We analyzed verifier pass separately from post-edit validation, rereading, rewrites, repeated action loops, tool steps, and terminal flags.

The results were not uniform across models. GLM-5.3-Flash moved from 40/54 usable passes under C0 to 48/54 under C1, a paired gain of 14.8 percentage points [3.7, 29.6]; its post-edit validation also rose by 22.2 points. qwen3.5:9b gained 1.9 pass-rate points while its post-edit validation fell by 25.0 points. Ornith1.5:35b changed by −1.9 points [−16.7, 9.3], and llama3.1:8b stayed at the floor. Thus, the same skill can help, do little, or fail to register depending on the underlying model, and a change in workflow does not by itself establish a better repair.

The main evidence is in the [condition summary](results/tables/s7/S7_T1_model_condition_summary.csv), [paired pass-rate table](results/tables/s7/S7_T2_core_paired_differences.csv), [process summary](results/tables/s7/S7_T4_process_metrics.csv), [paired process table](results/tables/s7/S7_T7_process_paired.csv), [figures](figures/s7/), and [paper](paper/main.pdf).

### 7. Repeat the mechanism comparison with new tasks and better controls

The final study added 24 newly written and independently admitted tasks. It compared four prompts on qwen3.5:9b: C1, an externalized step-by-step procedure, trajectory imitation, and a generic prompt matched for length. Two repetitions per task and condition produced 192 scheduled runs. The generic prompt controls for adding text alone; the other two conditions compare explicit rules with an example-like behavioral pattern.

Against the generic prompt, the task-paired pass-rate differences were +6.25 points for C1, 0.00 for the externalized procedure, and +4.17 for imitation. All three 95% paired-bootstrap intervals included zero. The externalized procedure did, however, raise post-edit rereading by 31.3 points [+14.6, +47.9]. This follow-up reaches the same practical distinction as the eight-model study: changing how an agent works is measurable, but it is not the same as improving the code it leaves behind.

See the [analysis plan](docs/s8b_analysis_plan_20261015.md), [execution lock](config/s8b_execution_lock.yaml), [run ledger](S8B_STATUS.md), [result note](docs/s8b_results.md), [condition summary](results/tables/s8b/S8B_T1_condition_summary.csv), [paired outcomes](results/tables/s8b/S8B_T2_task_paired_differences.csv), [process contrasts](results/tables/s8b/S8B_T5_process_paired_differences.csv), and [figure](paper/figures/s8b_mechanism.pdf).

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
python analysis/check_report_numbers.py
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

完整报告见 [PDF](paper/main.pdf) 与 [LaTeX 源码](paper/main.tex)。主图已更新为八模型版本：[PNG](paper/figures/main_results.png) / [矢量 PDF](paper/figures/main_results.pdf)。


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

## 研究过程

这项研究一共经历了七步。顺序不是按写作需要倒推出来的：先确认任务和计分方式，再做正式对照；最后一组机制实验则换用了全新的任务。

### 1. 先做能够独立验收的仓库修复题

我们选择小型仓库修复任务，是因为这类任务既能留下完整的读文件、改代码和跑测试记录，也能用外部程序验收。每道题都包括冻结的错误仓库、题面、测试夹具和合约 verifier。模型最后怎么解释不影响判分，真正决定结果的是修改后的代码是否满足合约。

正式任务池有 18 题。其中 12 题属于 skill A/B，对应 `test_in`；另外 6 题属于迁移类型 C，对应 `test_out`。在模型开始答题之前，每道题都必须满足三个条件：正确修复能够通过，原始错误版本不能通过，已知的捷径解也不能通过。任务划分和检查结果见[数据划分锁](docs/s3_split_lock.md)、[任务清单](tasks/formal_manifest.json)和[准入记录](tasks/s3_admission.json)。

### 2. 确认模型和任务之间还有可测的提升空间

最早一批 temperature=0 的 pilot 单独保留。之后，我们检查不同调用路径支持哪些采样字段，并用多种模型跑校准任务。原因很直接：如果一道题所有模型都能做对，或者某个模型一道也做不对，那么这组数据很难告诉我们 skill 是否有帮助。

校准后，qwen3.5:9b 被选作弱目标模型，llama3.1:8b 用来表示更低的能力边界，再加入更强的通用模型和代码模型形成对照。详细过程见[采样探测](docs/s0_sampling_probe.md)、[校准协议](docs/s4_calibration_protocol.md)和[校准结果](docs/s4_calibration_results.md)。

### 3. 先把 runner 和“成功”的定义理清楚

早期 CLI 运行暴露了一个计分问题：有些运行最后没有可见回复，但仓库已经被正确修复；与此同时，超时、没有编辑、工具错误和 verifier 失败又可能出现在同一条运行里。用一个单标签概括整条运行会丢失信息。

因此，可直接调用的模型统一使用锁定的 r2 loop：工具集合固定，最多运行 40 步，命令采用进程组超时，只对没有收到任何响应的传输错误重试，并逐步保存模型响应和工具记录。GPT 继续作为 Codex 参考锚点。最终是否成功直接读取 `verifier.json.passed`；只有重试耗尽的传输错误不进入主分母，超时和撞到步数上限仍算失败。实现与修订记录见[runner 设计](docs/b1_r2_runner.md)、[结局标志说明](docs/outcome_flags_revision.md)、[verifier-pass 勘误](docs/verifier_pass_erratum_20261010.md)和[分析补丁](docs/s7_verifier_pass_analysis_patch_20261010.md)。

### 4. 从弱模型的失败轨迹里决定下一步测什么

runner 稳定后，我们逐条查看 qwen3.5:9b 的轨迹，区分哪些失败可能通过文字要求改善，例如漏掉约束、修改后没有验证；哪些更像文件损坏、接口异常或提前终止。由此产生了两个开发条件：`v1` 把“检查—修改—验证”写得更明确，`L3b` 则在第 32 次调用后给一次固定提醒，用来测试简单的后段护栏。

`v1` 相对 C1 使修改后验证增加了 45.0 个百分点，但 verifier 通过率没有变化。`L3b` 触发后确实能看到一些行为变化，不过对应分层样本很少，基线层本身也有差异。相关材料见[轨迹诊断](docs/s4_qwen35_diagnosis.md)、[`v1` 记录](docs/d4_intervention.md)、[`L3b` 结果](docs/l3b_results.md)和[指标对账](docs/l3b_metric_reconciliation.md)。

### 5. 锁定八模型正式实验

正式对照只有一个核心区别：C0 不带 skill 文本，C1 加入冻结的 v0 skill。题面、工具、verifier、runner、结尾指令和调度规则都保持不变。qwen3.5:9b 的每个“任务 × 条件”运行 5 次，其余七个模型各运行 3 次；`v1` 和 `L3b` 保留为弱模型探索条件。

任务、条件和重复没有分块运行，而是按固定种子打散并交错排列。这样可以把不同条件分散到整个运行时段，统计时仍以任务而不是单次重复为单位。最终矩阵共有 1,086 条运行，其中 936 条属于 C0/C1，150 条属于两个探索条件；全部调度均已完成。完整设置见[执行方案](docs/s7_execution_plan.md)、[执行锁](config/s7_execution_lock.yaml)、[调度记录](docs/s7_schedule_chain_20261010.md)和[运行账本](STATUS.md)。

### 6. 把“代码是否修好”和“agent 怎么做”分开看

分析时，先在每个任务和条件内汇总重复运行，再计算各模型按任务配对的 C1−C0。verifier 通过率与修改后验证、修改后重读、重写、重复循环、工具步数和终止状态分别统计，而不是把执行流程当成正确性的替代指标。

不同模型给出了不同答案。GLM-5.3-Flash 在 C0 下通过 40/54 条，在 C1 下通过 48/54 条，任务配对提升为 14.8 个百分点 [3.7, 29.6]，修改后验证也增加了 22.2 个百分点。qwen3.5:9b 的通过率只增加 1.9 个百分点，修改后验证反而减少 25.0 个百分点。Ornith1.5:35b 的变化是 −1.9 个百分点 [−16.7, 9.3]，llama3.1:8b 则一直处在地板。也就是说，同一份 skill 在不同模型上可能有帮助、几乎没变化，或者根本看不出作用；执行路径变化也不能直接等同于修复质量提高。

主要数据见[模型与条件汇总](results/tables/s7/S7_T1_model_condition_summary.csv)、[任务配对通过率差](results/tables/s7/S7_T2_core_paired_differences.csv)、[过程指标](results/tables/s7/S7_T4_process_metrics.csv)、[过程指标配对差](results/tables/s7/S7_T7_process_paired.csv)、[正式图表](figures/s7/)和[论文](paper/main.pdf)。

### 7. 换一批新任务，再比较三种流程表达方式

最后一组实验新写了 24 道题，并重新做了独立准入。qwen3.5:9b 在四种 prompt 下运行：C1、外显化的逐步流程、轨迹模仿，以及长度匹配的通用提示。每个任务和条件重复 2 次，共 192 条调度。等长通用提示用来控制“只是多写了一段话”的影响；另外两组分别测试明确列步骤和展示行为模式。

相对等长通用提示，C1、外显流程和轨迹模仿的任务配对通过率差分别为 +6.25、0.00 和 +4.17 个百分点，三个 95% 配对 bootstrap 区间都跨过 0。外显流程确实让修改后重读增加了 31.3 个百分点 [+14.6, +47.9]。这组结果与八模型实验指出的是同一个区别：agent 的做法可以被 prompt 改变，但做法变了，不等于最后留下的代码更容易通过验证。

完整材料见[分析方案](docs/s8b_analysis_plan_20261015.md)、[执行锁](config/s8b_execution_lock.yaml)、[运行账本](S8B_STATUS.md)、[结果说明](docs/s8b_results.md)、[条件汇总](results/tables/s8b/S8B_T1_condition_summary.csv)、[任务配对结果](results/tables/s8b/S8B_T2_task_paired_differences.csv)、[过程指标配对差](results/tables/s8b/S8B_T5_process_paired_differences.csv)和[结果图](paper/figures/s8b_mechanism.pdf)。

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
python analysis/check_report_numbers.py
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

这两个入口是运行审计接口，并不是“重新生成原 S7”的手段。公开克隆如果没有本地 provider 权限、GPT 的 Codex 登录状态和针对新队列的明确授权，就不能实际启动它们。直接 runner 的设计见 [docs/b1_r2_runner.md](docs/b1_r2_runner.md)，原始冻结调度见 [config/s7_schedules/](config/s7_schedules/)。



## 许可证

代码采用 MIT 许可证；已发布的数据、图表和文档采用 CC BY 4.0。详见 [LICENSE](LICENSE)。
