# 工作流详解

## plan 阶段

- 需求分析、任务拆分
- 产出 `plan.json`：任务列表、依赖、context_limit、atomic_commit、rollback_strategy

## develop 阶段

- 按 plan.json 执行，DAG 并行
- **每个 task**：修改 → lint → code-simplifier 清理 → 原子提交

## verify 阶段

- 全量 lint + 测试
- 失败：诊断 → 回滚失败任务 → 重试（最多 3 轮）

## 断点续传

- `--resume`：从上次中断处继续
- `--from-stage <stage>`：从指定阶段开始

## 事件溯源

- `events.jsonl` 记录所有阶段事件
- 可重建状态、审计、统计

## 产物目录

- `~/.codingengine/runs/<run_id>/artifacts/`
  - plan.json
  - code_changes.json
  - verify_result.json
