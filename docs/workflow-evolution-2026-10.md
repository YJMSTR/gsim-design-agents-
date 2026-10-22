# Workflow Evolution 2026-10:自我迭代计划(工具即对象)

双轨协议:主线程(实验实感)与报告侧 pi(外部方法论对标)都可直接 commit 改进;每个改动带 rationale(哪个实验/哪份外部材料触发)。本文档是当前快照+迭代-1 清单。

## 现状快照(2026-10-23)

- **定义文件**:本仓(独立 git,ed3b2c7 起);核心=docs/agent-flow.md(循环:Profile→Diagnose→Plan→Implement→Validate→Measure→Record→Promote/Reject)、docs/spec-measurement-protocol.md(测量契约:同会话交错/静默守卫/锁)、docs/spec-evidence-records.md(证据 schema+outcome 词表,check-evidence.py 强制)、docs/rationales/(每条规则的事故来源)、docs/humanize-integration.md+scripts/gsim-humanize.sh(RLCR 半接入)
- **循环结构**:任务契约(目标/输入出/正确性/约束/验证命令/评价命令/晋升判据/回滚判据)→draft.md→plan.md→单候选实现→对单线程 gsim+参考 trace 验证→跨设计×线程数测量→benchmark.csv+candidates.jsonl+profile/<run>/→晋升/修订/拒绝
- **已有门**:NEMU 三门(coremark 67944/50000、linux 86469/30000、fulltrap GOOD TRAP 0x80001ca0)、knob-off 字节同一、check-evidence 合约(含 outcome 词表、parent 解析、promote 记录需 identity 元组)、knob-lint(旋钮活性)、doc-knob 一致性、champion-drift 分类、build-watchdog
- **在役资产**(本迭代新增,住在 task workspace):BubbleTool 归因(bubble CSV 三件)、campaign 驱动(--plan/--mask/--guard-cpu-scope/静默守卫/measurement.lock)、台账 73 条、analysis/ 判决文档族

## 迭代-1(已批准,五项)

| # | 项 | 落点 | 触发源 |
|---|---|---|---|
| 1 | 台账预注册预测字段(prediction 三负载 delta+机制链+kill_condition 必填) | spec-evidence-records.md + ledger-append.py + check-evidence.py | pi/KDA 方法论;我方"预期带"非正式实践 |
| 2 | holdout 第 4 负载(仅冠军更替触发) | spec-measurement-protocol.md + check-evidence promote 门 | KDA 防作弊六门;我方三负载特化风险从未形式化 |
| 3 | 判决宪法 JSON(机器可读,驱动器执行,agent 不可写) | constitution.json + 驱动器 | R1-R8 判决口径曾散在 IRC 消息 |
| 4 | 预筛 CLI(字节同一/静态评分/台账查重,零窗口成本) | scripts/pre-screen.py | R3/R8 纸面门、R1 静态评分的手工先行 |
| 5 | 窗口登记器(锁文件+状态文件,替代 IRC 广播纪律) | scripts/window-registrar.py + 协议修订 | piper 污染战役的编排教训 |

## 迭代-2(候选,按材料就绪度)

- 机制分计算器(prediction vs 归因位移;失败窗口买因果知识)— scripts/mechanism-score.py,依赖迭代-1#1
- flame_chase 双模式(重写跳出局点/微调攀峰)在候选生成的显式化 — 依赖 humanize-integration 深化
- KDA 六门剩余三项(合法输入规约/新输入重放/元素级误差界)对照我方字节同一+NEMU 门的差距审计
- 周度人类 meta-review 固化(RSI 降档:10 事件/天)

## 时序

R7/R8 落地后启动迭代-1(第一周基建,不动代理行为);第二周有界扫描 shakeout(现成试金石:R1 留下的 commw 二变体 cells)全自动闭环;两周期满按"省 >50% 编排消息且 verdict 质量不降"判成败。

## 迭代-1 修订(2026-10-23,吸收外部对标 ~/test/gda-external-gap-analysis-20261023.md)

外部结论:我方"测量诚实性"为全部对标对象(Humanize/RLCR、hmz、KDA、AlphaEvolve)最强;短板在"决策经济学"。裁决:

1. **机制分提前进迭代-1**:scripts/mechanism-score.py(prediction vs 归因位移对账)——族冻结与归因签名档案的数据底座
2. **niche-view.py**(~30 行,MAP-Elites 地板版):归因签名矩阵,round-brief 手工 CLOSURE 散文变查询(该散文已两次因归因更正重写)
3. **每 5 轮战略对齐轮**(~30 行 bash,astra slow-role):补"reviewer 只查最后一条台账、无同族打转检测"盲区,不依赖迭代-1 其余项
4. 判决宪法升级 sha256 校验+可审计("不可见"不可能,"不可改+可审计"可以)
5. **C50000 长跑升 promote 门**+合法输入规约成文(唯一暴露过非原子写 bug 的探针,对标 KDA 压力探针)
6. 族冻结+预算配额维持迭代-2(依赖机制分);task_class 观察

一周落地三件:prediction 三字段+checker(kill_condition↔review-brief 打通)/每5轮对齐轮/niche-view.py。
