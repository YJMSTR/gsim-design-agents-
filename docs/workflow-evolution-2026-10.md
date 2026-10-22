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
