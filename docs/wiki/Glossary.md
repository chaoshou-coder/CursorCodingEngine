# 术语表

- **Agent** — 执行任务的 AI 实体
- **Skill** — 教 Agent 执行特定任务的指令集（SKILL.md）
- **Rule** — 持久约束（.mdc）
- **simplerig** — 编排引擎
- **DAG** — 有向无环图，任务依赖
- **事件溯源** — events.jsonl 记录所有事件
- **断点续传** — --resume 从中断处继续
- **原子提交** — 每 task 独立 git commit
- **回滚** — git revert 失败任务
- **context_limit** — 模型上下文上限，任务拆分依据
- **plan.json** — 规划产物
- **artifacts** — 产物目录
