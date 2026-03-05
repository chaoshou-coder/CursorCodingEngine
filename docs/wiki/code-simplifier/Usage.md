# code-simplifier 使用指南

## 一、触发时机

- **每个 task 提交前**：develop 阶段每个 task 完成且 lint 通过后、执行 `git commit` 前，调用本 Skill 清理该 task 修改的代码
- **develop 完成后**：若未按 task 粒度调用，则在 develop 阶段全部完成、verify 前统一调用一次
- **用户显式请求**：「简化这段代码」「清理最近修改」「simplify」「refine」「clean up」

## 二、遵循项目约定

- 优先读取 `CLAUDE.md`、`AGENTS.md`、`.cursor/rules/`
- 无则使用通用最佳实践
- 不引入项目未约定的风格

## 三、泛化说明

原版 code-simplifier 有 ES 模块、React 等特定指令。本 Skill 已泛化：

- **语言栈**：不限定 ES/React，遵循项目实际技术栈（Python、TypeScript、Go 等）
- **规范来源**：优先读取项目约定文件，无则使用通用最佳实践
- **范围**：仅处理用户指定或 git 显示的最近修改部分

## 四、与主工作流的集成

在主工作流 Skill 中，develop 阶段每个 task 的流程为：

1. 修改代码
2. 立即 lint（ECC 质量门禁）
3. **调用 code-simplifier** 清理最近修改的代码
4. 原子提交

code-simplifier 不改变行为，只提升清晰度；修改后若引入问题，lint 会在下一轮捕获。
