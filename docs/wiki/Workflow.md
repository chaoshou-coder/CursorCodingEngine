# 工作流详解

## 一、阶段概览

CodingEngine 采用四阶段流水线：**plan → develop → verify → 完成**。前三个阶段对应 simplerig 阶段机，完成阶段汇总变更并向用户报告。

## 二、plan 阶段

### 输入

- 用户需求（来自 `codingengine init` 的描述或 @ 文档）
- `context_limit`（来自 config.yaml 模型配置）

### 流程

1. `codingengine emit stage.started --stage plan --run-id <run_id>`
2. 分析需求，按 context_limit 拆分任务
3. 产出 `plan.json`，包含：
   - **tasks**：任务列表，每任务含 id、description、预估上下文
   - **dependencies**：任务依赖，DAG 依据（来自 OpenSpec）
   - **decoupled**：模块解耦信息，减少跨模块修改
   - **atomic_commit**：true，每任务独立 commit
   - **rollback_strategy**：`"git_revert"`，失败时回滚
4. 保存到 `~/.codingengine/runs/<run_id>/artifacts/plan.json`
5. `codingengine emit stage.completed --stage plan --run-id <run_id>`

### 产出

- `plan.json` — 规划产物，develop 阶段依据

## 三、develop 阶段

### 输入

- `plan.json` 中的任务列表与依赖

### 流程

1. `codingengine emit stage.started --stage develop --run-id <run_id>`
2. 按 DAG 调度执行任务，无依赖可并行
3. **每个 task**：
   - 修改代码
   - **立即 lint**（ECC 质量门禁：编辑后立即验证）
   - 调用 **code-simplifier** 清理最近修改的代码（Anthropic 原则）
   - **原子提交**：`git add -A && git commit -m "[codingengine] <task_id>"`
4. 将变更记录到 `code_changes.json`
5. `codingengine emit stage.completed --stage develop --run-id <run_id>`

### 执行纪律（来自 OMO）

- **Just Do**：执行阶段禁止向用户提问，遇到不确定时用最佳判断继续
- **Boulder 续航**：任务未完成不得停，不因「需要用户确认」而轻易停下

### 产出

- `code_changes.json` — 变更记录
- 多个 git commit，每个含 task_id

## 四、verify 阶段

### 输入

- 全部代码变更

### 流程

1. `codingengine emit stage.started --stage verify --run-id <run_id>`
2. 全量 lint + 测试
3. **失败**：诊断失败原因 → 回滚失败任务（`git revert`）→ 重试（最多 3 轮）
4. **通过**：可选记录 wisdom 到 `wisdom.jsonl`（OMO 模式）
5. `codingengine emit stage.completed --stage verify --run-id <run_id>`

### 产出

- `verify_result.json` — Lint/Test 结果
- `wisdom.jsonl`（可选）— 跨任务学习记录

## 五、完成阶段

1. 汇总变更，向用户报告
2. `codingengine emit run.completed --run-id <run_id>`

## 六、断点续传

- **`--resume`**：从上次中断处继续，重读 events 重建状态
- **`--from-stage <stage>`**：从指定阶段开始（如 `plan`、`develop`、`verify`）

得益于事件溯源，断点续传无需额外状态文件。

## 七、事件溯源

`events.jsonl` 记录所有阶段事件，包括：
- `run.started`、`run.completed`
- `stage.started`、`stage.completed`
- `task.completed`、`task.failed`
- `llm.called`（若记录 token 消耗）

可重建状态、审计、统计。`codingengine tail --follow` 实时查看事件流。

## 八、产物目录

```
~/.codingengine/runs/<run_id>/
├── events.jsonl          # 事件流
├── artifacts/
│   ├── plan.json         # 规划产物
│   ├── code_changes.json # 变更记录
│   ├── verify_result.json # 验证结果
│   └── wisdom.jsonl     # 可选，跨任务学习
└── ...
```

项目目录零新增文件，不污染用户项目。
