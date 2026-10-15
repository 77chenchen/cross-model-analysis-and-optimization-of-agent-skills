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

## Results at a glance

[![Eight-model verifier pass rates with model logos](figures/s7/verifier_pass_rates_by_model.png)](figures/s7/verifier_pass_rates_by_model.pdf)


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
paper/            Single-column manuscript source, bibliography, figures, and compiled PDF.
skills/           Frozen written-skill variants used by the experimental conditions.
```

## Research path


| Phase | Question and approach | Result and primary record |
|---|---|---|
| 1. Task pool and split lock | Build synthetic repair tasks with external contract verifiers; separate development diagnosis, development validation, in-skill test, and transfer test before later interventions. | All 18 formal tasks passed admission. See [split lock](docs/s3_split_lock.md), [formal manifest](tasks/formal_manifest.json), and [admission record](tasks/s3_admission.json). |
| 2. Sampling and calibration | Probe transport controls, preserve temperature-0 pilots as legacy evidence, then calibrate model–task difficulty under the direct runner. | Controls and their limitations were recorded rather than assumed; the weak model was retained as a floor condition. See [sampling probe](docs/s0_sampling_probe.md), [calibration protocol](docs/s4_calibration_protocol.md), and [calibration results](docs/s4_calibration_results.md). |
| 3. Runner and outcome diagnosis | Replace the opaque CLI path for open-weight models with a minimal direct runner; distinguish empty finals, no edits, tool errors, timeouts, and verifier outcomes. | The r2 runner, non-exclusive outcome flags, and verifier-pass correction were locked. See [runner design](docs/b1_r2_runner.md), [outcome revision](docs/outcome_flags_revision.md), and [verifier-pass erratum](docs/verifier_pass_erratum_20261010.md). |
| 4. Development interventions | Diagnose weak-model trajectories without touching frozen assets; evaluate v1 wording and a fixed call-32 reminder only on development data. | The recorded pilot is a negative result; L3b is a mechanism observation, not an efficacy claim. See [qwen diagnosis](docs/s4_qwen35_diagnosis.md), [v1 pilot record](docs/d4_intervention.md), [L3b results](docs/l3b_results.md), and [metric reconciliation](docs/l3b_metric_reconciliation.md). |
| 5. Locked formal evaluation | Lock prompts, schedules, hashes, outcome rules, and task-paired analysis before any test execution; interleave conditions rather than run them in condition blocks. | The eight-model schedule completed all 1,086 runs. See [execution plan](docs/s7_execution_plan.md), [execution lock](config/s7_execution_lock.yaml), [schedule chain](docs/s7_schedule_chain_20261010.md), and [batch ledger](STATUS.md). |
| 6. Formal analysis and corrections | Use <code>verifier.json.passed</code> as the primary outcome; exclude only retry-exhausted provider errors from the primary denominator; retain legacy labels for audit. | GLM adds a positive C1 contrast of +14.8 pp [3.7, 29.6], whereas high-baseline Ornith has −1.9 pp [−16.7, 9.3]. See the [formal tables](results/tables/s7/), [figures](figures/s7/), and [analysis patch](docs/s7_verifier_pass_analysis_patch_20261010.md). |
| 7. Fresh-task mechanism study | Use 24 newly authored and independently admitted development tasks to compare v0, an externalized process, trajectory imitation, and a length-matched generic control without changing S7. | S8-b is locked as 24 tasks × 4 conditions × 2 repetitions = 192 runs and is running sequentially. See the [S8-b status](S8B_STATUS.md), [execution lock](config/s8b_execution_lock.yaml), and [analysis plan](docs/s8b_analysis_plan_20261015.md). |

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
python -m analysis.make_s7_figures</code></pre>

Expected outputs are refreshed Markdown/CSV tables under [results/tables/](results/tables/), a successful cross-check against [results/tables/s7/](results/tables/s7/), six figure tests, and five S7 figures plus a contact sheet under [figures/s7/](figures/s7/). In the isolated-clone check, this sequence took under one minute after dependency installation.


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

## 主结果与论文

完整报告见 [PDF](paper/main.pdf) 与 [LaTeX 源码](paper/main.tex)。主图已更新为八模型版本：[PNG](paper/figures/main_results.png) / [矢量 PDF](paper/figures/main_results.pdf)。


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

## 研究推进



| 阶段 | 解决方案 | 产物 |
|---|---|---|
| 1. 建任务池并锁定数据划分 | 先制作带独立合约 verifier 的小型仓库修复题；在观察任何正式测试轨迹前，把任务划为诊断集、版本选择集、同类保留集和跨技能保留集。 | 18 个正式任务全部通过正例、错误种子和捷径解的准入检查。见[划分锁](docs/s3_split_lock.md)、[正式任务清单](tasks/formal_manifest.json)与[准入记录](tasks/s3_admission.json)。 |
| 2. 校准模型、任务与采样设置 | 先检查实际 API/CLI 能否接受温度和随机种子；将温度为 0 的早期试跑独立保留，再以直接 runner 测量模型在任务池上的难度分布。 | 不把“请求了某个参数”误写成“参数已受控”；qwen3.5:9b 被记录为下限条件而非干预优化对象。见[采样探测](docs/s0_sampling_probe.md)、[校准协议](docs/s4_calibration_protocol.md)与[校准结果](docs/s4_calibration_results.md)。 |
| 3. 重建 runner 与结局口径 | 针对 CLI 路径中难以观察的响应字段，构建最小直接 runner；把最终消息为空、源文件未变、工具调用错误、超时和 verifier 判定拆成可同时成立的标志。 | 锁定 r2 runner，并将主结局改为 verifier 的 Boolean 字段而非旧的单一标签。见[runner 设计](docs/b1_r2_runner.md)、[结局字段修订](docs/outcome_flags_revision.md)与[verifier-pass 勘误](docs/verifier_pass_erratum_20261010.md)。 |
| 4. 仅用开发集理解失败与测试干预 | 不改题目、verifier 或既有轨迹；只在允许设计干预的诊断/验证数据上检查失败模式，并比较 v1 文本和固定第 32 次调用提醒。 | v1 的早期结果是应保留的负结果；L3b 只证明某些触发后行为可被观测，不能支持效果结论。见[qwen 诊断](docs/s4_qwen35_diagnosis.md)、[v1 记录](docs/d4_intervention.md)、[L3b 结果](docs/l3b_results.md)和[指标对账](docs/l3b_metric_reconciliation.md)。 |
| 5. 正式运行前冻结设计 | 在任何保留测试任务运行前，固定提示序列化、条件、调度、哈希、分母规则和按任务配对的分析方式；同一模型的条件按交错顺序运行。 | 八模型正式调度的 1,086 条运行已经全部完成。见[执行计划](docs/s7_execution_plan.md)、[执行锁](config/s7_execution_lock.yaml)、[调度监督器说明](docs/s7_schedule_chain_20261010.md)和[状态账本](STATUS.md)。 |
| 6. 用 verifier 结果完成正式分析 | 正式结果统一读取 <code>verifier.json.passed</code>；只将重试耗尽的传输失败移出主分母，旧标签继续保留以便对账。 | GLM 的 C1 配对提升为 +14.8 个百分点 [3.7, 29.6]；高基线 Ornith 为 −1.9 个百分点 [−16.7, 9.3]。见[正式结果表](results/tables/s7/)、[S7 图](figures/s7/)与[分析补丁](docs/s7_verifier_pass_analysis_patch_20261010.md)。 |
| 7. 使用全新任务检验机制 | 另外制作 24 个通过独立准入的开发任务，比较 v0、外显流程、轨迹模仿和等长通用提示，不回头修改 S7。 | S8-b 已锁定为 24 个任务 × 4 个条件 × 2 次重复，共 192 条，目前正按单 worker 顺序运行。见 [S8-b 监控](S8B_STATUS.md)、[执行锁](config/s8b_execution_lock.yaml)和[分析计划](docs/s8b_analysis_plan_20261015.md)。 |

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
python -m analysis.make_s7_figures</code></pre>

预期产物包括：更新后的 [results/tables/](results/tables/) Markdown/CSV、针对 [results/tables/s7/](results/tables/s7/) 的数值一致性检查、6 项图形测试，以及 [figures/s7/](figures/s7/) 中的 5 张 S7 图与 contact sheet。依赖安装完成后，隔离克隆中这组命令运行时间不足 1 分钟。



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
