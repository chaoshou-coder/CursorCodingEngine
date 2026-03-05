# CodingEngine

> 以 simplerig 为编排骨架，融合 ECC/OMO 的 Agent 定义、Skill 模式和反馈机制，构建「编排+执行+迭代」解决方案。

## 核心价值

**目标**：将 SWE-bench ~50% 模型推到 70-80%+。

**增量不来自某个工具，而来自三个能力的协同**：

1. **编排能力** — 把复杂任务拆成模型能处理的粒度，按依赖并行执行
2. **执行能力** — 每个子任务原子化，解耦可回滚，结果可验证
3. **迭代能力** — 验证失败时自动反馈修复，不止一轮

## 技术栈

- **simplerig** — 事件溯源、DAG 调度、断点续传、质量门禁
- **Cursor** — Agent 执行环境
- **Skill 胶水** — SKILL.md 为唯一集成点

## 快速链接

- [快速开始](Getting-Started.md)
- [安装指南](Installation.md)
- [配置详解](Configuration.md)
- [工作流](Workflow.md)
- [评估与基准](Evaluation.md)

## 致谢

- simplerig
- everything-claude-code (ECC)
- oh-my-opencode (OMO)
- OpenSpec
- Anthropic code-simplifier
