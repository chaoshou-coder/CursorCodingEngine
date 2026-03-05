# 核心概念

## 任务工程

**任务工程**：弱模型通过工程手段达到强模型效果。编排、执行、迭代三者协同，缺一不可。

核心思路类似 MapReduce：把不可能的大任务拆成可能的小任务，每个原子化、可回滚、可并行，失败自动诊断修复。SWE-bench 上 ~50% 的模型，经任务工程增强后可达 70-80%+。

---

## 编排能力

- **按 context_limit 拆分**：每个子任务预估上下文不超过模型的 context_limit，避免超出窗口
- **DAG 依赖**：任务间有依赖关系，无依赖的可并行执行
- **plan.json**：规划产物，含任务列表、dependencies、decoupled、atomic_commit、rollback_strategy

编排能力来自 simplerig 的 DAG 调度与 OpenSpec 的依赖模型，由 codingengine planner 实现。

---

## 执行能力

- **原子提交**：每 task 独立 git commit，message 含 task_id（如 `[codingengine] task_001`），失败可精确定位
- **解耦**：模块间通过接口约定，不直接跨模块修改；plan.json 的 decoupled 字段表达模块边界
- **可回滚**：失败时 `git revert` 对应 commit，不污染其他任务

执行能力由 git_ops 实现，参考 simplerig 的阶段机与产物管理。

---

## 迭代能力

- **verify 失败** → 诊断失败原因 → 回滚失败任务（git revert）→ 重试（最多 3 轮）
- 不止一轮修复，避免「一次失败就放弃」

迭代能力是 SWE-bench 提升的主要来源之一（预期 +10-15 pp）。

---

## Skill 即胶水

**SKILL.md** 为唯一集成点，驱动 Agent 行为。不建 14 个 Agent，Cursor 内置 subagent 够用。

四个参考项目的最佳实践通过 Skill 中的自然语言指令融入，无需额外代码或 Hook 适配层。主工作流 Skill 位于 `.cursor/skills/simplerig/SKILL.md`，包含 OMO Just Do、Boulder 续航、ECC 质量门禁、code-simplifier 调用时机等。

---

## 静态上下文优先

**AGENTS.md** 注入项目结构和约定，修改前先读取。减少 Agent 盲目探索，提升效率。

来自 ECC/OMO 的静态注入理念，由 context-management.mdc 规则强化。

---

## Wisdom 积累

每个任务完成后可提取 learnings，写入 `wisdom.jsonl`，后续任务可引用。跨任务学习，减少重复错误。

来自 OMO 的 Wisdom 模式，在 verify 阶段通过后可选执行。

---

## 事件溯源

`events.jsonl` 记录所有阶段事件，可重建状态、审计、统计。断点续传依赖事件流重建 RunState。

来自 simplerig 的核心机制。

---

## 断点续传

`--resume` 从上次中断处继续，`--from-stage <stage>` 从指定阶段开始。得益于事件溯源，重读 events 即可恢复。
