# CodingEngine

> 编排 + 执行 + 迭代的 AI 辅助开发工具。通过**任务工程**让弱模型达到强模型效果，目标将 SWE-bench ~50% 推到 70-80%+。

## 这是什么

CodingEngine 是 Cursor 专属的 Agentic Coding 基础设施。它不替代 Cursor，而是**把复杂开发任务拆成模型能处理的小任务**，按依赖并行执行，每个任务原子提交、失败可回滚，验证失败时自动诊断重试。

**核心思路**：类似 MapReduce —— 不可能的大任务 → 可能的小任务，每个原子化、可回滚、可并行。弱模型通过工程手段达到强模型效果。

## 工作原理

```
用户需求 → plan（拆分任务）→ develop（逐任务：修改→lint→清理→原子提交）→ verify（全量测试，失败则回滚重试）→ 完成
```

**三大能力**：

| 能力 | 做什么 | 为什么重要 |
|------|--------|------------|
| **编排** | 按 context_limit 拆分任务，DAG 依赖，无依赖可并行 | 避免超出模型窗口，提升吞吐 |
| **执行** | 每任务独立 git commit，失败 `git revert` | 精确定位、可回滚、不污染其它任务 |
| **迭代** | verify 失败 → 诊断 → 回滚失败任务 → 重试（最多 3 轮） | 不止一轮修复，预期 +10-15 pp |

**Skill 即胶水**：不建 14 个 Agent、60+ Skill。通过 `.cursor/skills/` 中的 SKILL.md 驱动 Cursor Agent，融入 simplerig、ECC、OMO、OpenSpec 的最佳实践。

**不污染项目目录**：所有 runs、events、artifacts 在 `~/.codingengine/runs/`，项目内零新增文件。

## 快速上手

- [快速开始](docs/wiki/快速开始.md)
- [使用教程](docs/wiki/使用教程.md) — 完整示例
- [安装指南](docs/wiki/安装指南.md)
- [CLI 参考](docs/wiki/CLI参考.md)

## 设计参考

simplerig、everything-claude-code (ECC)、oh-my-opencode (OMO)、OpenSpec 四项目胶水而成，详见 [参考项目与引用](docs/wiki/参考项目与引用.md)。
