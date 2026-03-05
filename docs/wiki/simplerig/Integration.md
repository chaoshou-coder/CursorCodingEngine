# simplerig 集成方式（设计参考）

CodingEngine 参考 simplerig 设计，实际使用 **codingengine** CLI。本节说明两种使用方式。

## 一、Skill 驱动（推荐）

Agent 按 codingengine Skill 执行流程，手动 emit 事件。适合 Cursor 内交互式开发。

**流程**：
1. `codingengine init "Short description"` 取得 run_id
2. 按阶段执行：`codingengine emit stage.started --stage plan --run-id <run_id>`
3. 完成规划后：`codingengine emit stage.completed --stage plan --run-id <run_id>`
4. develop、verify 同理
5. 最后：`codingengine emit run.completed --run-id <run_id>`

主工作流 Skill 会引导 Agent 按此流程执行，并融入 OMO Just Do、Boulder 续航、ECC 质量门禁。

## 二、CLI 直接调用

```bash
codingengine run "需求" --tdd
codingengine run "需求" --bdd
codingengine run "需求" --resume
```

阶段处理器（plan_handler、develop_handler 等）自动执行，适合脚本或本地调试。

## 三、参数化改造

simplerig 原支持 `performance_degradation_point`、`optimal_context`。CodingEngine 已废弃，任务拆分**仅依据 context_limit**。
