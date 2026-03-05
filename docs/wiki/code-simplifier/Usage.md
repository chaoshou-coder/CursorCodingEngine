# code-simplifier 使用指南

## 触发时机

- **每个 task 提交前**：develop 阶段每个 task 完成且 lint 通过后
- **develop 完成后**：若未按 task 粒度调用，则统一调用一次
- **用户显式请求**：「简化这段代码」「清理最近修改」

## 遵循项目约定

- 优先读取 `CLAUDE.md`、`AGENTS.md`、`.cursor/rules/`
- 无则使用通用最佳实践

## 泛化说明

原版有 ES 模块、React 等特定指令。本 Skill 已泛化，适用于任意语言栈。
