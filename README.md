<a id="english"></a>
<p align="right"><strong>English</strong> &nbsp;|&nbsp; <a href="#zh">中文</a></p>

# SkillTraj: Written Skills for Cross-Model Coding Agents

This project asks whether a written skill changes repair success and process behavior for coding agents across models.

## TL;DR

- In the controlled six-model C0/C1 panel, pass-rate differences are small and inconsistent across models ([S7_T1_model_condition_summary.csv](results/tables/s7/S7_T1_model_condition_summary.csv); [S7_T2_core_paired_differences.csv](results/tables/s7/S7_T2_core_paired_differences.csv)).
- Process behavior and success decouple for the weak target: C1 changes validation-after-edit by −25.0 percentage points and pass rate by +1.9 percentage points ([S7_T7_process_paired.csv](results/tables/s7/S7_T7_process_paired.csv); [S7_T2_core_paired_differences.csv](results/tables/s7/S7_T2_core_paired_differences.csv)).
- The exploratory v1 condition changes validation-after-edit by +45.0 percentage points but pass rate by 0.0 percentage points ([S7_T7_process_paired.csv](results/tables/s7/S7_T7_process_paired.csv); [S7_T6_exploratory.csv](results/tables/s7/S7_T6_exploratory.csv)).
- With 18 tasks, the study resolves effects only on the order of 9–12 percentage points; all findings are exploratory and use synthetic repair tasks ([report.md](report.md), with task-level inputs in [S7_T2_core_paired_differences.csv](results/tables/s7/S7_T2_core_paired_differences.csv)).

## Main result

![Figure 1: controlled C0/C1 results, process depth, and outcome flags](figures/s7/S7_F1_main_results.png)

The publication-quality vector version is [Figure 1 (PDF)](figures/s7/S7_F1_main_results.pdf). Read the full [technical report](report.md) or the [paper PDF](paper/main.pdf) ([LaTeX source](paper/main.tex)).

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

The table below records the decision path rather than retroactively presenting a smooth success story. Frozen tasks, verifiers, skills, schedules, and prior outcomes were not changed after their applicable locks.

| Phase | Question and approach | Result and primary record |
|---|---|---|
| 1. Task pool and split lock | Build synthetic repair tasks with external contract verifiers; separate development diagnosis, development validation, in-skill test, and transfer test before later interventions. | All 18 formal tasks passed admission. See [split lock](docs/s3_split_lock.md), [formal manifest](tasks/formal_manifest.json), and [admission record](tasks/s3_admission.json). |
| 2. Sampling and calibration | Probe transport controls, preserve temperature-0 pilots as legacy evidence, then calibrate model–task difficulty under the direct runner. | Controls and their limitations were recorded rather than assumed; the weak model was retained as a floor condition. See [sampling probe](docs/s0_sampling_probe.md), [calibration protocol](docs/s4_calibration_protocol.md), and [calibration results](docs/s4_calibration_results.md). |
| 3. Runner and outcome diagnosis | Replace the opaque CLI path for open-weight models with a minimal direct runner; distinguish empty finals, no edits, tool errors, timeouts, and verifier outcomes. | The r2 runner, non-exclusive outcome flags, and verifier-pass correction were locked. See [runner design](docs/b1_r2_runner.md), [outcome revision](docs/outcome_flags_revision.md), and [verifier-pass erratum](docs/verifier_pass_erratum_20261010.md). |
| 4. Development interventions | Diagnose weak-model trajectories without touching frozen assets; evaluate v1 wording and a fixed call-32 reminder only on development data. | The recorded pilot is a negative result; L3b is a mechanism observation, not an efficacy claim. See [qwen diagnosis](docs/s4_qwen35_diagnosis.md), [v1 pilot record](docs/d4_intervention.md), [L3b results](docs/l3b_results.md), and [metric reconciliation](docs/l3b_metric_reconciliation.md). |
| 5. Locked formal evaluation | Lock prompts, schedules, hashes, outcome rules, and task-paired analysis before any test execution; interleave conditions rather than run them in condition blocks. | 870 scheduled S7 runs completed. See [execution plan](docs/s7_execution_plan.md), [execution lock](config/s7_execution_lock.yaml), [schedule chain](docs/s7_schedule_chain_20261010.md), and [batch ledger](STATUS.md). |
| 6. Formal analysis and corrections | Use <code>verifier.json.passed</code> as the primary outcome; exclude only retry-exhausted provider errors from the primary denominator; retain legacy labels for audit. | The locked tables and figures show no consistent C1 advantage; corrections remain visible. See [formal result note](docs/s7_formal_results_20261011.md), [S7 tables](results/tables/s7/), [figures](figures/s7/), and [analysis patch](docs/s7_verifier_pass_analysis_patch_20261010.md). |
| 7. Interpretation and next study | Test whether observed behaviors distinguish success, document task and provider incidents, and formulate a dev-only successor without changing S7. | Behavior–outcome evidence does not identify a success mechanism. S8 is a draft awaiting authorization. See [behavior cross-tabulation](docs/behavior_outcome_crosstab.md), [failure taxonomy](docs/weak_failure_taxonomy.md), and [S8 plan](docs/s8_plan.md). |

## Reproduction

Run all commands from the repository root. The analysis commands below were executed once in a fresh, isolated clone with Python 3.14.0 on 2026-10-11. The model-execution command was syntax-checked with <code>--help</code>, but deliberately not executed: doing so would make new provider requests and create a new experimental cohort.

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

The public release supports table and figure reproduction, but **not a from-scratch reanalysis of formal S7 runs**: the necessary <code>data/s7_runs/</code> directories and raw provider responses are deliberately not released. If an authorized holder has those private, frozen run directories, the gated regeneration command is:

<pre><code>python -m analysis.formal_s7_results
python -m analysis.make_s7_figures</code></pre>

It refuses to run unless the 870/870 completion and analysis-patch hash gate pass. That limitation is intentional and is documented in [the data-release policy](docs/data_release_policy.md).

### Re-run the experimental schedule

This creates new run artifacts and must use a new cohort/output location; it must not overwrite or be pooled with S7. Open-weight runs require <code>SOCLAAS_API_KEY</code> in the environment. GPT uses the local authenticated Codex CLI and has no repository-stored credential. Do not put credentials, raw responses, or reasoning payloads in Git.

<pre><code>export SOCLAAS_API_KEY
python harness/run_s7_schedule.py config/s7_schedules/qwen3_5_9b.tsv \
  --output-root data/new_cohort_runs --execute

# GPT reference-anchor schedule only
python harness/run_s7_codex_schedule.py config/s7_schedules/gpt_5_6_sol.tsv \
  --output-root data/new_cohort_runs --execute</code></pre>

These are audit entry points, not commands for reproducing the locked S7 cohort. They cannot be meaningfully run from a clean public clone without local provider access, the required Codex login for GPT, and explicit authorization for a new cohort. The direct runner specification is [here](docs/b1_r2_runner.md); the frozen original schedules are in [config/s7_schedules/](config/s7_schedules/).

## Data release

[data/release/](data/release/) contains de-identified <code>metadata.jsonl</code>, <code>verifier.jsonl</code>, <code>events.jsonl</code>, <code>actions.jsonl</code>, and [manifest.json](data/release/manifest.json) for completed pre-S7 r2 cohorts. It replaces absolute paths with placeholders and removes provider connection/authentication fields and reasoning fields.

Raw provider responses and reasoning are not released. Formal S7 run directories are also withheld because they contain raw trajectory material. The alternatives and trade-offs are described in [docs/data_release_policy.md](docs/data_release_policy.md). A redacted history scan is recorded in [docs/secret_scan_20261010.json](docs/secret_scan_20261010.json); credentials are never part of the repository contract.

## Key protocol conventions

- The primary outcome is the Boolean <code>passed</code> field in each <code>verifier.json</code>, not the historical single outcome label.
- Retry-exhausted transport failures (<code>provider_error_protocol</code>) are excluded from the primary numerator and denominator, then included as failures in a scheduled-run sensitivity view.
- Timeouts and max-step outcomes remain denominator failures when a verifier outcome is available.
- Repetitions estimate within-task variation; paired inference treats tasks as the sampling units.
- GPT-5.6 Sol is a sampling-uncontrolled Codex reference anchor and is never pooled into controlled direct-runner comparisons.
- The formal protocol was specified in a hash-locked, timestamped plan and lock manifest; it was not registered with an independent third-party registry.
- Legacy outcome labels remain available only for audit and correction comparisons.

## Status and known issues

- **S7:** complete (870/870); formal tables and figures are available in [results/tables/s7/](results/tables/s7/) and [figures/s7/](figures/s7/).
- **S8-lite:** not started; the candidate-mechanism study is a draft awaiting owner authorization. The repository currently contains [docs/s8_plan.md](docs/s8_plan.md), rather than a separate <code>docs/s8_prereg.md</code> file.
- **A04:** a documented task-text/verifier conflict; applicable development analyses report included and excluded views. See [A04 known defect](docs/a04_known_task_defect.md).
- **b09_phone:** two clustered historical hard timeouts, retained as a sensitivity issue rather than a demonstrated verifier defect. See [b09 known issue](docs/s7_b09_phone_known_issue_20261010.md).
- **GPT overwrite deviation:** 104 usage-limit failures were later overwritten with a new active cohort; the potential bias and retained manifest are documented in [the audit](data/s7_gpt_overwrite_audit_20261011.json) and [deviation note](docs/s7_postcompletion_gpt_rerun_deviation_20261011.md).

## License

Source code is licensed under MIT. Released data, figures, tables, and documentation are licensed under CC BY 4.0. See [LICENSE](LICENSE).

## Citation

Authors are pending. Replace the placeholder before external citation.

<pre><code>@misc{skilltraj2026,
  title  = {SkillTraj: Written Skills for Cross-Model Coding Agents},
  author = {Authors to be added},
  year   = {2026},
  note   = {Repository and technical report}
}</code></pre>

---

<a id="zh"></a>
<p align="right"><a href="#english">English</a> &nbsp;|&nbsp; <strong>中文</strong></p>

# SkillTraj：跨模型编码智能体的书面技能研究

本项目研究：写成文本的 skill 是否会改变不同模型编码智能体的修复成功率与过程行为。

## 摘要

- 在受控的六模型 C0/C1 面板中，通过率差异小，且模型之间不一致（[S7_T1_model_condition_summary.csv](results/tables/s7/S7_T1_model_condition_summary.csv)、[S7_T2_core_paired_differences.csv](results/tables/s7/S7_T2_core_paired_differences.csv)）。
- 对弱目标模型，过程行为与成功率脱钩：C1 使“最后一次编辑后的验证”下降 25.0 个百分点，但通过率仅上升 1.9 个百分点（[S7_T7_process_paired.csv](results/tables/s7/S7_T7_process_paired.csv)、[S7_T2_core_paired_differences.csv](results/tables/s7/S7_T2_core_paired_differences.csv)）。
- 探索性的 v1 使该验证指标上升 45.0 个百分点，而通过率变化为 0.0 个百分点（[S7_T7_process_paired.csv](results/tables/s7/S7_T7_process_paired.csv)、[S7_T6_exploratory.csv](results/tables/s7/S7_T6_exploratory.csv)）。
- 18 个任务只能分辨约 9–12 个百分点量级的效应；结论均为探索性，并基于合成修复任务（[report.md](report.md)，任务级输入见 [S7_T2_core_paired_differences.csv](results/tables/s7/S7_T2_core_paired_differences.csv)）。

## 主图与完整产物

![Figure 1: controlled C0/C1 results, process depth, and outcome flags](figures/s7/S7_F1_main_results.png)

矢量主图见 [Figure 1 PDF](figures/s7/S7_F1_main_results.pdf)。完整结果见 [技术报告](report.md)，论文见 [PDF](paper/main.pdf) 与 [LaTeX 源码](paper/main.tex)。

## 目录

```text
config/           锁定的协议、prompt、数据划分、runner 与调度配置。
tasks/            冻结的合成修复任务、fixture、清单和 admission 记录。
harness/          直接 agent runner、调度执行、admission 与诊断工具。
analysis/         版本化结局口径、汇总、测试、表格和绘图代码。
data/release/     去标识化的已发布轨迹派生数据与清单。
results/tables/   机器可读结果表；正式 S7 表位于 results/tables/s7/。
figures/          可复现图、绘图数据、QA 产物和图形清单。
docs/             协议锁、诊断、勘误、结果说明与后续研究计划。
paper/            单栏论文源码、参考文献、图与编译后的 PDF。
skills/           实验条件中使用的冻结书面 skill 版本。
```

## 完整调研路径

| 阶段 | 解决思路 | 得到的结果与证据 |
|---|---|---|
| 1. 任务池与划分锁定 | 先构建带外部合约 verifier 的合成修复任务，再把诊断、版本选择、in-skill 测试和迁移测试分开。 | 18 个正式任务全部通过 admission。见[划分锁](docs/s3_split_lock.md)、[任务清单](tasks/formal_manifest.json)和[admission 记录](tasks/s3_admission.json)。 |
| 2. 采样与校准 | 先探测 transport 控制，保留 temperature-0 旧 pilot，再用直接 runner 校准模型×任务难度。 | 记录“实际能控制什么”，不把未被端点证实的控制当作事实；弱模型作为 floor 条件保留。见[采样探测](docs/s0_sampling_probe.md)、[校准协议](docs/s4_calibration_protocol.md)和[校准结果](docs/s4_calibration_results.md)。 |
| 3. Runner 与结局诊断 | 用最小直接 runner 替代不透明 CLI 路径；把空最终输出、未编辑、工具错误、超时和 verifier 结果拆开记录。 | 锁定 r2 runner、非互斥标志与 verifier-pass 勘误。见[runner 设计](docs/b1_r2_runner.md)、[结局修订](docs/outcome_flags_revision.md)和[verifier-pass 勘误](docs/verifier_pass_erratum_20261010.md)。 |
| 4. 开发集干预 | 不动冻结资产，只诊断弱模型轨迹；仅在开发集评估 v1 文本与固定第 32 次调用提醒。 | v1 pilot 是保留的负结果；L3b 是机制观察而非疗效结论。见[qwen 诊断](docs/s4_qwen35_diagnosis.md)、[v1 记录](docs/d4_intervention.md)、[L3b 结果](docs/l3b_results.md)和[指标对账](docs/l3b_metric_reconciliation.md)。 |
| 5. 正式评测锁定 | 在任何 test 运行前锁定 prompt、调度、哈希、结局规则与任务配对分析，并交错安排条件。 | 完成 870 条 S7 调度运行。见[执行计划](docs/s7_execution_plan.md)、[执行锁](config/s7_execution_lock.yaml)、[调度链](docs/s7_schedule_chain_20261010.md)和[状态账本](STATUS.md)。 |
| 6. 正式分析与勘误 | 主结局改用 <code>verifier.json.passed</code>；只有重试耗尽的 provider error 才从主分母排除；旧标签保留用于审计。 | 锁定表和图未显示一致的 C1 优势，且勘误证据仍可追溯。见[正式结果](docs/s7_formal_results_20261011.md)、[S7 表](results/tables/s7/)、[S7 图](figures/s7/)和[分析补丁](docs/s7_verifier_pass_analysis_patch_20261010.md)。 |
| 7. 解释与下一研究 | 检验所观察行为能否区分成功；记录任务/provider 事件；写 dev-only 后续设计而不回改 S7。 | 行为—结果证据不足以识别成功机制。S8 仍是待批准草案。见[行为交叉表](docs/behavior_outcome_crosstab.md)、[失败分类](docs/weak_failure_taxonomy.md)和[S8 计划](docs/s8_plan.md)。 |

## 复现

所有命令从仓库根目录运行。下列分析命令已于 2026-10-11 在隔离的干净克隆中用 Python 3.14.0 实际执行。模型运行入口仅做了 <code>--help</code> 语法检查；本次没有执行它，因为这会创建新的 provider 请求和实验队列。

### 环境

实际使用 Python 3.14.0；预期最低版本为 Python 3.11。锁定的绘图依赖在 [analysis/requirements-figures.txt](analysis/requirements-figures.txt)。

<pre><code>python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r analysis/requirements-figures.txt</code></pre>

通常需 1–3 分钟，取决于本地包缓存。

### 复现已发布分析与图

<pre><code>python -m analysis.make_tables
python analysis/check_report_numbers.py
python -m unittest analysis.test_figures
python -m analysis.make_s7_figures</code></pre>

预期得到：更新的 [results/tables/](results/tables/) Markdown/CSV，针对 [results/tables/s7/](results/tables/s7/) 的数值核对通过，6 个图形测试通过，以及 [figures/s7/](figures/s7/) 下的 5 张 S7 图和 contact sheet。隔离克隆中依赖安装完成后该序列少于 1 分钟。

公开发布包可以复现表和图，但不能从零重算正式 S7：需要的 <code>data/s7_runs/</code> 目录和原始 provider response 并未发布。如获授权并持有冻结的私有运行目录，可执行：

<pre><code>python -m analysis.formal_s7_results
python -m analysis.make_s7_figures</code></pre>

若 870/870 完成状态或分析补丁哈希不匹配，命令会拒绝运行。这是有意的发布限制，详见[数据发布策略](docs/data_release_policy.md)。

### 重新运行实验

这会创建新运行产物，应使用新的队列/输出目录，不能覆盖或并入 S7。开源权重模型需要环境变量 <code>SOCLAAS_API_KEY</code>；GPT 使用本地已登录的 Codex CLI，不使用仓库内凭证。绝不可把凭证、原始 response 或 reasoning 写入 Git。

<pre><code>export SOCLAAS_API_KEY
python harness/run_s7_schedule.py config/s7_schedules/qwen3_5_9b.tsv \
  --output-root data/new_cohort_runs --execute

# 仅用于 GPT 参考锚点调度
python harness/run_s7_codex_schedule.py config/s7_schedules/gpt_5_6_sol.tsv \
  --output-root data/new_cohort_runs --execute</code></pre>

这两个入口仅供审计，不是重现锁定 S7 队列的方式。没有本地 provider 访问、GPT 的 Codex 登录和明确的新队列授权时，干净公开克隆无法实际运行它们。直接 runner 说明见 [docs/b1_r2_runner.md](docs/b1_r2_runner.md)，原始冻结调度位于 [config/s7_schedules/](config/s7_schedules/)。

## 数据发布

[data/release/](data/release/) 包含已完成 pre-S7 r2 队列的去标识化 <code>metadata.jsonl</code>、<code>verifier.jsonl</code>、<code>events.jsonl</code>、<code>actions.jsonl</code> 和 [manifest.json](data/release/manifest.json)。其中绝对路径被替换为占位符，provider 连接/认证字段与 reasoning 字段已移除。

原始 provider response 与 reasoning 不发布；正式 S7 运行目录也不发布，因为包含原始轨迹材料。替代发布方案见 [docs/data_release_policy.md](docs/data_release_policy.md)。已脱敏的历史密钥扫描记录见 [docs/secret_scan_20261010.json](docs/secret_scan_20261010.json)。

## 关键口径

- 主结局是每次运行 <code>verifier.json</code> 中的 Boolean <code>passed</code>，不是历史单标签。
- 仅重试耗尽的传输失败（<code>provider_error_protocol</code>）从主分子和分母排除；敏感性分析将其视为失败。
- 当存在 verifier 结果时，timeout 与 max-step 仍是分母内失败。
- 重复用于估计任务内随机性；配对推断以任务为抽样单位。
- GPT-5.6 Sol 是采样未受控的 Codex 参考锚点，不并入受控直接 runner 对比。
- 正式协议是带时间戳、哈希锁定的计划与 lock manifest，而非第三方注册的 preregistration。
- 旧结局标签只用于审计和勘误对照。

## 状态与已知问题

- **S7：** 已完成（870/870）；正式表和图分别位于 [results/tables/s7/](results/tables/s7/) 与 [figures/s7/](figures/s7/)。
- **S8-lite：** 尚未开始；候选机制研究仍在等待所有者授权。当前仓库存在 [docs/s8_plan.md](docs/s8_plan.md)，没有单独的 <code>docs/s8_prereg.md</code>。
- **A04：** 题面与 verifier 存在已记录冲突；有关开发集分析均报告含/不含该任务的视图。见 [A04 known defect](docs/a04_known_task_defect.md)。
- **b09_phone：** 存在两次聚集的历史硬超时，作为敏感性问题保留，而非已证明的 verifier 缺陷。见 [b09 known issue](docs/s7_b09_phone_known_issue_20261010.md)。
- **GPT 覆盖偏差：** 104 条 usage-limit 失败后来被新活动队列覆盖；潜在偏差和保留清单见 [审计文件](data/s7_gpt_overwrite_audit_20261011.json) 与 [偏差说明](docs/s7_postcompletion_gpt_rerun_deviation_20261011.md)。

## 许可证

代码采用 MIT；已发布的数据、图表和文档采用 CC BY 4.0。见 [LICENSE](LICENSE)。

## 引用

作者信息待补充；在对外引用前请替换下列占位符。

<pre><code>@misc{skilltraj2026,
  title  = {SkillTraj: Written Skills for Cross-Model Coding Agents},
  author = {Authors to be added},
  year   = {2026},
  note   = {Repository and technical report}
}</code></pre>
