# 术语表

- **Agent** — 执行任务的 AI 实体。Cursor 内置 subagent 够用，CodingEngine 不建额外 Agent 层。

- **Skill** — 教 Agent 执行特定任务的指令集，以 SKILL.md 形式存在。CodingEngine 通过 Skill 胶水融合四个参考项目的最佳实践。

- **Rule** — 持久约束，以 .mdc 形式存在。codingengine-workflow、quality-standards、context-management 三个规则。

- **codingengine** — 独立编排引擎，提供 init/emit/run/status/tail 等 CLI，事件溯源、DAG 调度、断点续传、原子提交/回滚。

- **DAG** — 有向无环图，表达任务依赖。无依赖的任务可并行执行。来自 simplerig 与 OpenSpec。

- **事件溯源** — events.jsonl 记录所有事件，可重建状态、审计、统计。来自 simplerig。

- **断点续传** — `--resume` 从上次中断处继续，`--from-stage` 从指定阶段开始。依赖事件溯源。

- **原子提交** — 每 task 独立 git commit，message 含 task_id，失败可精确定位并 revert。

- **回滚** — verify 失败时 `git revert` 失败任务，不污染其他任务。

- **context_limit** — 模型上下文窗口大小，任务拆分的唯一依据。已废弃 performance_degradation_point、optimal_context。

- **plan.json** — 规划产物，含任务列表、dependencies、decoupled、atomic_commit、rollback_strategy。

- **artifacts** — 产物目录，位于 `~/.codingengine/runs/<run_id>/artifacts/`，含 plan.json、code_changes.json、verify_result.json 等。

- **Just Do** — OMO 模式，执行阶段禁止向用户提问，用最佳判断继续。

- **Boulder 续航** — OMO 模式，任务未完成不得停，不因需要用户确认而轻易停下。

- **Wisdom** — 跨任务学习记录，写入 wisdom.jsonl，后续任务可引用。来自 OMO。

- **Confidence-Based Review** — ECC 模式，只报 >80% 确信的问题。

- **Severity 分级** — ECC 模式，CRITICAL 阻塞，HIGH/MEDIUM/LOW 记录但不阻塞。
