---
name: code-simplifier
description: "Anthropic Code-Simplifier 的 Cursor Skill 适配。在 codingengine develop 阶段每个 task 完成后、或 verify 前，对最近修改的代码进行清理与简化。遵循项目 CLAUDE.md/AGENTS.md 约定，泛化适用任意语言栈。"
---

# Code-Simplifier Skill

**来源**：Anthropic [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) / [claude-code](https://github.com/anthropics/claude-code) 的 code-simplifier 插件。

**何时启用**：codingengine develop 阶段每个 task 原子提交前、或 develop 全部完成后 verify 前；或用户明确说「简化这段代码」「清理最近修改的代码」时。

## 核心原则

1. **Preserve Functionality** — 不改变代码行为，只改变实现方式
2. **Apply Project Standards** — 遵循项目 CLAUDE.md、AGENTS.md、.cursor/rules 中的约定（命名、格式、模块化）
3. **Enhance Clarity** — 减少嵌套、消除冗余、改进命名、用 switch 替代嵌套三元
4. **Avoid Over-Simplification** — 不为了简短而牺牲可读性
5. **Focus on Recently Modified Code** — 仅处理本次任务修改过的文件/函数，不扩大范围

## 触发时机

- **每个 task 提交前**：在 codingengine 工作流中，每个 develop task 完成且 lint 通过后、执行 `git commit` 前，调用本 Skill 清理该 task 修改的代码
- **develop 完成后**：若未按 task 粒度调用，则在 develop 阶段全部完成、verify 前统一调用一次
- **用户显式请求**：用户说「simplify」「refine」「clean up」时

## 执行步骤

1. 识别最近修改的文件（git diff --name-only 或用户指定）
2. 逐文件分析：是否可简化、是否符合项目规范
3. 应用修改：保持功能不变，提升清晰度
4. 修改后立即运行 lint，确保无引入问题

## 泛化说明

原版 code-simplifier 有 ES 模块、React 等特定指令。本 Skill 已泛化：

- **语言栈**：不限定 ES/React，遵循项目实际技术栈
- **规范来源**：优先读取 `CLAUDE.md`、`AGENTS.md`、`.cursor/rules/`，无则使用通用最佳实践
- **范围**：仅处理用户指定或 git 显示的最近修改部分

## 与 codingengine 的集成

在 codingengine SKILL.md 的工作流中：

```
develop(task) → 修改代码 → lint → [code-simplifier 清理] → 原子提交
```
