# simplerig 集成方式

## 方式一：Skill 驱动

Agent 按 simplerig Skill 执行流程，手动 emit 事件。适合 Cursor 内交互式开发。

## 方式二：CLI 直接调用

```bash
simplerig run "需求" --tdd
simplerig run "需求" --bdd
```

阶段处理器（plan_handler、develop_handler 等）自动执行。

## 参数化改造

- 已废弃 `performance_degradation_point`、`optimal_context`
- 任务拆分仅依据 `context_limit`
