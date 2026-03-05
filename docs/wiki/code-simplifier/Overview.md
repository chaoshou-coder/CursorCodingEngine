# code-simplifier 概览

## 一、来源

Anthropic [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) / [claude-code](https://github.com/anthropics/claude-code) 的 code-simplifier 插件。

## 二、核心原则

1. **Preserve Functionality** — 不改变代码行为，只改变实现方式
2. **Apply Project Standards** — 遵循项目 CLAUDE.md、AGENTS.md、.cursor/rules 中的约定
3. **Enhance Clarity** — 减少嵌套、消除冗余、改进命名
4. **Avoid Over-Simplification** — 不为了简短而牺牲可读性
5. **Focus on Recently Modified** — 仅处理本次任务修改过的文件/函数，不扩大范围

## 三、与 CodingEngine 的 glue 方式

转为 Cursor Skill（`.cursor/skills/code-simplifier/SKILL.md`），由主工作流 `.cursor/skills/codingengine/SKILL.md` 定义调用时机，在 **codingengine develop 阶段**每个 task 提交前调用。泛化语言栈，不限定 ES/React。

**集成流程**：
```
develop(task) → 修改代码 → lint → [code-simplifier 清理] → 原子提交
```

## 四、与四项目胶水的关系

code-simplifier 来自 Anthropic，作为第五个参考融入。CodingEngine 主工作流 Skill 定义其调用时机，与 simplerig 阶段机、ECC 质量门禁协同：在 lint 通过后、commit 前执行清理，确保提交的代码既通过质量检查又保持清晰。
