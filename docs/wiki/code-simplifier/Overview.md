# code-simplifier 概览

## 来源

Anthropic [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) / [claude-code](https://github.com/anthropics/claude-code) 的 code-simplifier 插件。

## 核心原则

1. **Preserve Functionality** — 不改变行为
2. **Apply Project Standards** — 遵循 CLAUDE.md/AGENTS.md
3. **Enhance Clarity** — 减少嵌套、改进命名
4. **Avoid Over-Simplification** — 不牺牲可读性
5. **Focus on Recently Modified** — 仅处理本次修改部分

## 与 CodingEngine 的 glue 方式

转为 Cursor Skill，在 codingengine develop 阶段每个 task 提交前调用。泛化语言栈，不限定 ES/React。
