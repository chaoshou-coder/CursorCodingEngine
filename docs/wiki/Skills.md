# Skill 系统

## codingengine Skill（主工作流）

主工作流 Skill，包含：
- 4 阶段流程（plan → develop → verify → 完成）
- OMO "Just Do" 模式、Boulder 续航
- ECC 质量门禁（编辑后 lint、Confidence-Based Review）
- code-simplifier 调用时机

## code-simplifier Skill

- 来源：Anthropic code-simplifier 插件
- 触发：每个 task 提交前、或 develop 完成后
- 原则：Preserve Functionality、Apply Standards、Enhance Clarity

## Skill 格式

- YAML frontmatter（name, description）
- Markdown 正文（指令、示例）

## 何时启用

- codingengine：用户说「执行计划」「按计划执行」、或 @ .cursor/plans/*.plan.md
- code-simplifier：codingengine develop 中、或用户说「简化代码」
