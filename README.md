# CodingEngine

> CodingEngine 是在 **simplerig**、**everything-claude-code (ECC)**、**oh-my-opencode (OMO)**、**OpenSpec** 四个项目基础上，通过 Skill 与 Rules 胶水而成的「编排+执行+迭代」解决方案。以 codingengine 为独立 CLI 工具，融合各参考项目的 Agent 定义、执行纪律、质量门禁与任务依赖模型。

---

## 项目定位

CodingEngine 是 Cursor 专属的 Agentic Coding 基础设施。**目标**：将 SWE-bench 上 ~50% 水平的模型推到 70-80%+。

**增量不来自某个单一工具，而来自四个参考项目的协同与三个能力的叠加**：

1. **编排能力** — 把复杂任务拆成模型能处理的粒度，按依赖并行执行
2. **执行能力** — 每个子任务原子化，解耦可回滚，结果可验证
3. **迭代能力** — 验证失败时自动反馈修复，不止一轮

---

## 四项目胶水架构

CodingEngine 不 fork 任一项目，而是**提炼各项目的最佳实践，通过 SKILL.md 与 .mdc Rules 胶水到统一工作流**。各参考项目的贡献如下：

| 参考项目 | 贡献内容 | 在 CodingEngine 中的体现 |
|----------|----------|--------------------------|
| **simplerig** | 事件溯源、阶段机、DAG 调度、断点续传、产物管理 | codingengine CLI（init/emit/run/status/tail）、plan.json 结构、events.jsonl、~/.codingengine/runs/ 目录 |
| **oh-my-opencode (OMO)** | "Do NOT Ask — Just Do" 模式、Boulder 续航、3 层委派、Wisdom 积累 | 主工作流 Skill：执行阶段禁止向用户提问、任务未完成不结束 turn、wisdom.jsonl 记录 |
| **everything-claude-code (ECC)** | 质量门禁、编辑后立即 lint、Confidence-Based Review、Severity 分级 | quality-standards.mdc、SKILL 中「每次修改后立即 lint」、>80% 确信才报、CRITICAL 阻塞 |
| **OpenSpec** | Artifact 依赖图、任务解耦 | plan.json 的 dependencies、decoupled 字段，任务拆分时的模块边界 |
| **Anthropic code-simplifier** | 代码清理原则（Preserve Functionality、Apply Standards、Enhance Clarity） | code-simplifier Skill，develop 阶段每 task 提交前调用 |

**设计原则**：Skill 即胶水。不建 14 个 Agent、60+ Skill、Hook 适配层；Cursor 内置 subagent 够用，SKILL.md 为唯一集成点。

---

## 技术栈

- **codingengine** — 独立 Python CLI，提供事件溯源、DAG 调度、断点续传、原子提交/回滚
- **Cursor** — Agent 执行环境，读取 Skill 与 Rules
- **Skill 胶水** — `.cursor/skills/codingengine/SKILL.md`（主工作流）、`code-simplifier/SKILL.md`（代码清理）
- **Rules** — `codingengine-workflow.mdc`、`quality-standards.mdc`、`context-management.mdc`

---

## 核心价值主张

**任务工程**：按模型上下文空间拆分不可能的大任务为可能的小任务，每个原子化、可回滚、可并行，失败自动诊断修复。弱模型通过工程手段达到强模型效果。（类似 MapReduce 的思路）

**不污染项目目录**：所有 runs、events、artifacts 存储在 `~/.codingengine/runs/`，项目内零新增文件。可通过 `CODINGENGINE_DATA` 覆盖数据目录。

---

## 快速链接

- [快速开始](docs/wiki/快速开始.md)
- [使用教程](docs/wiki/使用教程.md) — 完整示例，手把手从 init 到完成
- [安装指南](docs/wiki/安装指南.md)
- [配置详解](docs/wiki/配置详解.md)
- [CLI 参考](docs/wiki/CLI参考.md)
- [工作流](docs/wiki/工作流详解.md)
- [架构设计](docs/wiki/架构设计.md)
- [参考项目详解](docs/wiki/参考项目与引用.md)
- [评估与基准](docs/wiki/评估与基准.md)

---

## 致谢

- **simplerig** — 编排骨架、事件溯源、DAG、断点续传
- **everything-claude-code (ECC)** — 质量门禁、Agent/Skill 模式
- **oh-my-opencode (OMO)** — Just Do、Boulder 续航、Wisdom 积累
- **OpenSpec** — Artifact 依赖图
- **Anthropic code-simplifier** — 代码清理原则

> 以上为参考项目，非项目依赖。本仓库中的 `simplerig`、`everything-claude-code`、`oh-my-opencode`、`OpenSpec` 目录仅作参考，不参与安装与运行。
