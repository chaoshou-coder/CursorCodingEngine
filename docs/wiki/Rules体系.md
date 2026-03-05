# Rules 体系

CodingEngine 使用三个精简规则替代 ECC 的 Hook 适配层。Rules 为持久约束（alwaysApply），与 Skill 按场景启用形成互补。

## 一、codingengine-workflow.mdc

### 职责

- 复杂任务（3+ 文件或跨模块）必须走 **codingengine** 工作流
- 规划产出 plan.json
- 每任务独立 commit
- 验证失败必须迭代修复

### 与四项目的关系

- **simplerig**：阶段流程、plan.json 结构
- **OpenSpec**：任务依赖、模块解耦（体现在 plan 产出）

## 二、quality-standards.mdc

### 职责

- 编辑后立即 lint
- 测试覆盖（TDD）
- 安全底线（无硬编码密钥、输入校验）

### 与四项目的关系

- **ECC**：编辑后立即 lint、Confidence-Based Review、Severity 分级

## 三、context-management.mdc

### 职责

- 静态注入优先（AGENTS.md）
- 修改前必须先读取
- 跨文件修改前理解调用关系

### 与四项目的关系

- **ECC/OMO**：静态上下文注入理念

## 四、Rules 与 Skill 分工

- **Rules**：持久约束，alwaysApply，引导日常编辑行为
- **Skill**：按场景启用，含具体流程（如 plan → develop → verify）、执行纪律（Just Do、Boulder 续航）、code-simplifier 调用时机

Rules 不包含阶段流程细节，阶段流程由 Skill 定义。
