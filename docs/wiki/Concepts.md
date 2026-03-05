# 核心概念

## 任务工程

弱模型通过工程手段达到强模型效果。编排、执行、迭代三者协同。

## 编排能力

- 按 `context_limit` 拆分任务
- DAG 依赖、并行执行
- 每个子任务预估上下文不超过 context_limit

## 执行能力

- **原子提交**：每 task 独立 git commit，message 含 task_id
- **解耦**：模块间通过接口约定，不直接跨模块修改
- **可回滚**：失败时 `git revert`

## 迭代能力

- verify 失败 → 诊断 → 回滚失败任务 → 重试（最多 3 轮）

## Skill 即胶水

SKILL.md 为唯一集成点，驱动 Agent 行为。不建 14 个 Agent，Cursor 内置 subagent 够用。

## 静态上下文优先

AGENTS.md 注入项目结构和约定，修改前先读取。

## Wisdom 积累

每个任务完成后可提取 learnings，写入 `wisdom.jsonl`，后续任务可引用。
