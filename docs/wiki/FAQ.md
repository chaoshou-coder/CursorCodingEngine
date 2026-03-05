# 常见问题

## 为什么用 codingengine 而不是自己写？

codingengine 已提供事件溯源、DAG 调度、断点续传、原子提交/回滚。参考 simplerig 设计，作为**独立工具**实现，**无需安装 simplerig**。四个参考项目（simplerig、ECC、OMO、OpenSpec）的最佳实践通过 Skill 胶水融入，无需从零开发编排骨架。

## 为什么不需要 14 个 Agent？

Cursor 内置 subagent 够用。**Skill 驱动行为**，不建额外 Agent 层。四个参考项目中 ECC 有大量 Agent 定义，CodingEngine 仅提炼其质量门禁、执行纪律等模式到 Skill 与 Rules，控制复杂度。

## 为什么废弃性能拐点？

用户要求仅保留 `context_limit` 作为任务拆分依据。`performance_degradation_point`、`optimal_context` 增加复杂性，收益不明确。RULER benchmark 等研究显示多数模型在 ~50% 上下文时性能下滑，但实际拆分逻辑简化后，单一 context_limit 足够。

## code-simplifier 会增加 token 消耗吗？

会，但通常可减少 20-30% 后续维护的 token。在 task 提交前调用，范围可控（仅处理本次修改部分）。遵循 Preserve Functionality、Apply Standards、Enhance Clarity 原则，避免过度简化。

## 支持非 Python 项目吗？

支持。config.yaml 可指定 linter、formatter、test_runner（如 eslint、prettier、jest）。code-simplifier 已泛化，不限定 ES/React，遵循项目 CLAUDE.md/AGENTS.md 约定。

## 如何扩展 Skill？

在 `.cursor/skills/` 下新建目录，含 `SKILL.md`。参考 codingengine、code-simplifier 格式（YAML frontmatter + Markdown 正文）。可融入 ECC 领域 Skill 的段落，但不建 60+ 独立 Skill。

## 数据存在哪里？会污染项目目录吗？

所有数据在 `~/.codingengine/runs/`，项目内零新增文件。可通过 `CODINGENGINE_DATA` 环境变量覆盖数据目录。

## 四个参考项目需要安装吗？

不需要。simplerig、everything-claude-code、oh-my-opencode、OpenSpec 为参考文件夹，CodingEngine 仅提炼其最佳实践到 Skill 与 Rules，不依赖任一项目。
