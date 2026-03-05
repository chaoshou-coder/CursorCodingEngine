# Rules 体系

## codingengine-workflow.mdc

- 复杂任务（3+ 文件或跨模块）必须走 simplerig
- 规划产出 plan.json
- 每任务独立 commit
- 验证失败必须迭代修复

## quality-standards.mdc

- 编辑后立即 lint
- 测试覆盖（TDD）
- 安全底线（无硬编码密钥、输入校验）

## context-management.mdc

- 静态注入优先（AGENTS.md）
- 修改前必须先读取
- 跨文件修改前理解调用关系

## Rules 与 Skill 分工

- **Rules**：持久约束，alwaysApply
- **Skill**：按场景启用，含具体流程
