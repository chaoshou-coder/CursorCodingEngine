# simplerig 概览（设计参考）

## 一、项目定位

simplerig 是基于 **Event Sourcing（事件溯源）** 的多阶段工作流框架。LLM 由编辑器（Cursor / OpenCode）提供，simplerig 负责**事件记录、产物管理、断点续传与可观测性**。

## 二、核心机制

### 事件溯源

- **事实源**：`events.jsonl`，每行一个事件
- **优势**：可恢复、可观测、解耦统计
- **Token 记录**：通过 `llm.called` 事件或 stage.completed 中的 token_usage

### 阶段机

- **四阶段**：plan → develop → verify → integrate
- **StageMachine**：按顺序执行，写入 `stage.*` 事件
- **ArtifactStore**：写入产物并计算 SHA256，用于跳过已完成阶段

### DAG 调度

- **状态流转**：PENDING → READY → RUNNING → COMPLETED/FAILED
- **并发控制**：ThreadPoolExecutor，受 config 中 max_agents 限制
- **Tool Lock**：非线程安全工具自动加锁

### 断点续传

- 重读 events 重建 RunState
- 产物校验，完整则跳过
- 未完成阶段继续执行

## 三、与 CodingEngine 的关系

CodingEngine **参考 simplerig 设计**，作为**独立产品**实现：

- **不依赖 simplerig**，无需安装 simplerig
- **参数化改造**：仅保留 context_limit，废弃 performance_degradation_point、optimal_context
- **集成 git_ops**：原子提交、失败回滚
- **通过 Skill 融入** OMO/ECC 最佳实践
- **数据目录**：`~/.codingengine/`，不污染项目目录（simplerig 默认 simplerig_data/）

> 本仓库中的 `simplerig/` 目录为参考代码，不参与安装与运行。
