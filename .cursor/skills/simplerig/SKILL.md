---
name: simplerig
description: "CodingEngine 核心工作流：规划→开发→验证→完成。融入 OMO Just Do 模式、Boulder 续航、ECC 质量门禁、code-simplifier 清理。用户提到「开发计划」「执行计划」「按计划执行」、或 @ .cursor/plans/*.plan.md 时启用。"
---

# SimpleRig 工作流（CodingEngine 增强版）

**何时启用**：用户 @ `.cursor/plans/*.plan.md`、或说「开发计划现在执行」「按计划执行」、或提出开发需求时。

## 执行纪律（OMO/ECC 融合）

### "Do NOT Ask — Just Do" 模式
- **执行阶段禁止向用户提问**：遇到不确定时用最佳判断继续，不因小问题中断
- 仅在 MT4/图形界面人工验证、业务决策需拍板、外部权限/数据缺失时，才进入等待人工

### Boulder 续航
- **任务未完成不得停**：若 session idle 且还有未完成 todo，注入 continuation prompt 继续执行
- 不因「需要用户确认」而轻易停下，优先推进可自动完成的部分

### 质量门禁（ECC）
- **编辑后立即验证**：每次文件修改后立即跑 lint，不攒到最后
- **Confidence-Based Review**：只报 >80% 确信的问题
- **Severity 分级**：CRITICAL 阻塞，HIGH/MEDIUM/LOW 记录但不阻塞

## Shell 与平台（必读）

- **Windows PowerShell 不支持 `&&`**：用分号 `;` 分隔命令
- **`codingengine init`**：优先用简短英文描述，详细需求写在 plan 或 @ 文档
- **命令入口**：`codingengine` 或 `ce`，不可用时用 `python -m codingengine.cli`
- **必须激活项目 .venv**：执行 pip/codingengine 前先激活
- **不污染项目目录**：所有数据在 `~/.codingengine/runs/`，项目内零新增文件

## 准备阶段

1. 进入项目根目录，激活 .venv
2. 检查 `pip show codingengine`、`codingengine --help`
3. 初始化：`codingengine init "Short English description"`
4. 取得 `run_id`，后续 emit 均带 `--run-id <run_id>`

## 阶段 1: 规划 (plan)

1. `codingengine emit stage.started --stage plan --run-id <run_id>`
2. 分析需求，制定 plan.json，包含：
   - 任务列表、依赖、context_limit 预估
   - `atomic_commit: true`、`rollback_strategy: "git_revert"`
3. 保存到 `~/.codingengine/runs/<run_id>/artifacts/plan.json`
4. `codingengine emit stage.completed --stage plan --run-id <run_id>`

## 阶段 2: 开发 (develop)

1. `codingengine emit stage.started --stage develop --run-id <run_id>`
2. 读取 plan.json，按任务执行
3. **每个 task**：
   - 修改代码 → **立即 lint**
   - 调用 **code-simplifier** 清理最近修改的代码（@code-simplifier）
   - **原子提交**：`git add -A && git commit -m "[codingengine] <task_id>"`
4. 将变更记录到 `code_changes.json`
5. `codingengine emit stage.completed --stage develop --run-id <run_id>`

## 阶段 3: 验证 (verify)

1. `codingengine emit stage.started --stage verify --run-id <run_id>`
2. 运行 `ruff check .`、`pytest`（exit 5 视为跳过）
3. 失败 → 诊断 → 回滚失败任务（`git revert`）→ 重试（最多 3 轮）
4. 通过 → 记录 wisdom（可选：`~/.codingengine/runs/<run_id>/artifacts/wisdom.jsonl`）
5. `codingengine emit stage.completed --stage verify --run-id <run_id>`

## 阶段 4: 完成

1. 汇总变更，向用户报告
2. `codingengine emit run.completed --run-id <run_id>`

## 工作流概览

```
plan → [并行] develop(task_1) + develop(task_2) + ...
     → [每个 task] 修改 → lint → code-simplifier 清理 → 原子提交
     → verify (全量测试)
     → 失败 → 诊断 → 回滚失败任务 → 重试（最多 3 轮）
     → 通过 → wisdom 记录 → 完成
```

## TDD / BDD（可选）

- `codingengine run "需求" --tdd` / `--bdd`

## 断点续传

中断后用户说「继续」时：
1. `codingengine status` 查看状态
2. `codingengine tail` 查看事件流
3. `codingengine run --resume` 从未完成阶段继续执行
