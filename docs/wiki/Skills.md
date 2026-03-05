# Skill 系统

CodingEngine 通过 **Skill 即胶水** 融合四个参考项目的最佳实践。SKILL.md 为唯一集成点，驱动 Cursor Agent 行为，不建 14 个 Agent、60+ Skill。

## 一、codingengine Skill（主工作流）

**位置**：`.cursor/skills/simplerig/SKILL.md`

### 职责

- 4 阶段流程：plan → develop → verify → 完成
- 融入 **OMO** "Just Do" 模式、Boulder 续航
- 融入 **ECC** 质量门禁（编辑后 lint、Confidence-Based Review、Severity 分级）
- 定义 **code-simplifier** 调用时机（每个 task 提交前）

### 何时启用

- 用户 @ `.cursor/plans/*.plan.md`
- 用户说「执行计划」「按计划执行」「开发计划现在执行」
- 用户提出开发需求、要求按既有计划执行

### 来自各参考项目的融入

| 来源 | 模式 | 在 Skill 中的体现 |
|------|------|-------------------|
| OMO | Just Do | 「执行阶段禁止向用户提问」「遇到不确定时用最佳判断继续」 |
| OMO | Boulder 续航 | 「任务未完成不得停」「不因需要用户确认而轻易停下」 |
| OMO | Wisdom | verify 通过后可选写入 wisdom.jsonl |
| ECC | 编辑后立即 lint | 「每个 task：修改 → 立即 lint」 |
| ECC | Confidence-Based Review | 「只报 >80% 确信的问题」 |
| ECC | Severity 分级 | 「CRITICAL 阻塞，HIGH/MEDIUM/LOW 记录但不阻塞」 |
| simplerig | 阶段流程 | init/emit 命令、plan.json 结构、产物路径 |
| OpenSpec | 任务依赖 | plan.json 的 dependencies、decoupled |

## 二、code-simplifier Skill

**位置**：`.cursor/skills/code-simplifier/SKILL.md`

### 来源

Anthropic [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) / [claude-code](https://github.com/anthropics/claude-code) 的 code-simplifier 插件。

### 核心原则

1. **Preserve Functionality** — 不改变行为
2. **Apply Project Standards** — 遵循 CLAUDE.md/AGENTS.md、.cursor/rules
3. **Enhance Clarity** — 减少嵌套、改进命名
4. **Avoid Over-Simplification** — 不牺牲可读性
5. **Focus on Recently Modified** — 仅处理本次修改部分

### 触发时机

- **每个 task 提交前**：develop 阶段每个 task 完成且 lint 通过后、`git commit` 前
- **develop 完成后**：若未按 task 粒度调用，则 develop 全部完成后、verify 前统一调用一次
- **用户显式请求**：「简化这段代码」「清理最近修改」

### 泛化说明

原版有 ES 模块、React 等特定指令。本 Skill 已泛化，适用于任意语言栈，遵循项目 CLAUDE.md/AGENTS.md 约定。

## 三、Skill 格式

- **YAML frontmatter**：`name`、`description`
- **Markdown 正文**：指令、示例、何时启用、执行步骤

## 四、何时启用

- **codingengine**：用户说「执行计划」「按计划执行」、或 @ .cursor/plans/*.plan.md
- **code-simplifier**：codingengine develop 中自动调用、或用户说「简化代码」

## 五、如何扩展 Skill

在 `.cursor/skills/` 下新建目录，含 `SKILL.md`。参考 codingengine、code-simplifier 格式。可融入 ECC 领域 Skill 的段落（如 tdd-workflow），但不建 60+ 独立 Skill。
