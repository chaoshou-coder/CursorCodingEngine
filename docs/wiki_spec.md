# CodingEngine Wiki 文档集规格

> 用于创建并上传至 GitHub 的详尽 Wiki 文档集。可置于 `docs/wiki/` 或作为 GitHub Wiki 源。

---

## 一、Wiki 目录结构

```
docs/wiki/
├── Home.md                          # 首页 / 总览
├── Getting-Started.md                # 快速开始
├── Installation.md                  # 安装指南
├── Configuration.md                 # 配置详解
├── Architecture.md                  # 架构设计
├── Concepts.md                      # 核心概念
├── Workflow.md                      # 工作流详解
├── Skills.md                        # Skill 系统
├── Rules.md                         # Rules 体系
├── simplerig/
│   ├── Overview.md                  # simplerig 概览
│   ├── Integration.md               # 集成方式
│   ├── Config-Reference.md          # config.yaml 完整参考
│   └── CLI-Reference.md             # CLI 命令参考
├── code-simplifier/
│   ├── Overview.md                  # code-simplifier 概览
│   └── Usage.md                     # 使用指南
├── Evaluation.md                    # 评估与基准
├── Troubleshooting.md               # 故障排查
├── FAQ.md                           # 常见问题
├── Contributing.md                  # 贡献指南
├── Glossary.md                      # 术语表
├── References.md                    # 参考项目与引用
└── Changelog.md                     # 变更日志
```

---

## 二、各文档内容大纲

### Home.md（首页）

- 项目一句话描述
- 核心价值主张（任务工程：50% → 70-80%）
- 三大能力：编排 + 执行 + 迭代
- 技术栈概览（codingengine + Cursor + Skill 胶水）
- 快速链接（安装、配置、工作流、评估）
- 参考项目致谢（simplerig, ECC, OMO, OpenSpec, Anthropic code-simplifier）

### Getting-Started.md（快速开始）

- 前置要求（Python 3.10+, Cursor, Git）
- 5 分钟上手流程
- 克隆/安装 codingengine
- 复制 Skill 到项目
- 第一次运行（示例需求）
- 预期输出（plan.json, events.jsonl, artifacts/）

### Installation.md（安装指南）

- 方式一：克隆 CursorCodingEngine 到项目
- 方式二：git submodule
- 方式三：pip install（若发布到 PyPI）
- 验证安装（codingengine --help, pip show codingengine）
- 虚拟环境要求（建议命名 CCEfor<项目名>）
- Windows / macOS / Linux 差异
- 常见安装问题

### Configuration.md（配置详解）

- config.yaml 位置与优先级
- 模型配置（context_limit, roles, provider）
- 废弃参数说明（performance_degradation_point, optimal_context）
- 项目结构（source_dirs, test_dirs）
- 工具链（linter, formatter, test_runner）
- 并行配置（max_agents, task_groups）
- 超时与重试
- 环境变量（CODINGENGINE_CONFIG, CODINGENGINE_DATA 等）

### Architecture.md（架构设计）

- 整体架构图（Mermaid）
- 三层能力：编排、执行、迭代
- codingengine 的角色（事件溯源、DAG、断点续传）
- Skill 即胶水的设计决策
- 数据流（用户需求 → init → plan → develop → verify → 完成）
- 与 ECC/OMO/OpenSpec 的概念映射
- 目录结构说明

### Concepts.md（核心概念）

- **任务工程**：弱模型通过工程手段达到强模型效果
- **编排能力**：按 context_limit 拆分、DAG 依赖、并行执行
- **执行能力**：原子提交、解耦、可回滚
- **迭代能力**：verify 失败 → 诊断 → 重试
- **Skill 即胶水**：SKILL.md 为唯一集成点
- **静态上下文优先**：AGENTS.md 注入
- **Wisdom 积累**：跨任务学习记录

### Workflow.md（工作流详解）

- plan 阶段：需求分析、任务拆分、plan.json 产出
- develop 阶段：DAG 并行、每 task 修改 → lint → code-simplifier → 原子提交
- verify 阶段：全量测试、失败诊断、重试策略
- 断点续传（--resume, --from-stage）
- 事件溯源（events.jsonl）
- 产物目录（artifacts/）

### Skills.md（Skill 系统）

- codingengine Skill：主工作流、阶段指令、执行纪律
- code-simplifier Skill：触发时机、核心原则、泛化说明
- Skill 格式（YAML frontmatter + Markdown）
- 何时启用、如何引用
- 从 ECC/OMO 提炼的模式在 Skill 中的体现

### Rules.md（Rules 体系）

- codingengine-workflow.mdc：复杂任务走 codingengine、规划产出、原子提交
- quality-standards.mdc：lint、测试覆盖、安全底线
- context-management.mdc：静态注入、修改前读取、跨文件理解
- Rules 与 Skill 的分工

### simplerig/Overview.md

- simplerig 简介与定位（设计参考）
- 事件溯源、阶段机、DAG 调度
- 与 CodingEngine 的关系

### simplerig/Integration.md

- 如何集成到 CodingEngine
- Skill 驱动 vs CLI 直接调用
- 参数化改造（context_limit）

### simplerig/Config-Reference.md

- config.yaml 完整字段参考
- 每个字段说明、默认值、示例

### simplerig/CLI-Reference.md

- init, emit, list, status, tail, stats
- 每个命令的用法、参数、示例

### code-simplifier/Overview.md

- Anthropic code-simplifier 来源
- 核心原则（Preserve Functionality, Apply Standards, Enhance Clarity）
- 与 CodingEngine 的 glue 方式

### code-simplifier/Usage.md

- 触发时机（每个 task 前 / develop 完成后）
- 遵循项目 CLAUDE.md/AGENTS.md
- 泛化说明（非 ES/React 项目）

### Evaluation.md（评估与基准）

- 目标：SWE-bench 50% → 70-80%
- 能力分解与预期贡献表
- 评估框架：SWE-bench Verified/Pro、HumanEval+、MBPP+、真实项目
- 手工测试流程
- 自动化评测搭建（可选）

### Troubleshooting.md（故障排查）

- codingengine 命令不可用
- 虚拟环境错误（装到错误 venv）
- config.yaml 未找到
- plan 阶段卡住
- develop 阶段 lint 失败
- verify 阶段测试失败
- 原子提交冲突
- 断点续传失败

### FAQ.md（常见问题）

- 为什么用 codingengine 而不是自己写？
- 为什么不需要 14 个 Agent？
- 为什么废弃性能拐点？
- code-simplifier 会增加 token 消耗吗？
- 支持非 Python 项目吗？
- 如何扩展 Skill？

### Contributing.md（贡献指南）

- 代码贡献流程
- 文档贡献流程
- Skill/Rules 改进建议
- Issue 与 PR 规范

### Glossary.md（术语表）

- Agent、Skill、Rule、Hook
- codingengine、DAG、事件溯源、断点续传
- 原子提交、回滚、Wisdom
- context_limit、plan.json、artifacts

### References.md（参考项目与引用）

- codingengine（chaoshou-coder/CursorCodingEngine）
- everything-claude-code
- oh-my-opencode
- OpenSpec
- Anthropic code-simplifier
- SWE-bench、HumanEval、MBPP
- 行业研究与论文引用

### Changelog.md（变更日志）

- 版本号、日期、变更内容
- 保持与 releases 同步

---

## 三、GitHub Wiki 部署方式

### 方式 A：Wiki 内容放在 docs/wiki/

- 在仓库中维护 `docs/wiki/*.md`
- 通过脚本或手动同步到 GitHub Wiki（wiki 是独立 git 仓库）
- 或使用 GitHub Pages 渲染 docs/ 下的 Markdown

### 方式 B：启用 GitHub Wiki

- 仓库设置 → Features → Wiki 勾选
- 克隆 `https://github.com/xxx/CursorCodingEngine.wiki.git`
- 将 docs/wiki/ 内容复制到 wiki 仓库
- 推送后自动出现在 Wiki 标签页

### 方式 C：docs/ 即文档

- 不启用独立 Wiki，将 docs/wiki/ 作为主文档目录
- README 链接到 docs/wiki/Home.md
- 可用 MkDocs、Docusaurus 等生成静态站点

**建议**：采用 **方式 B + 方式 C 并行** — docs/wiki/ 为源文件，定期同步到 GitHub Wiki；同时 docs/ 可被 CI 或本地工具生成文档站。

---

## 四、文档规范

- **语言**：中文为主，技术术语保留英文（如 context_limit, plan.json）
- **格式**：Markdown，兼容 GitHub Flavored Markdown
- **图表**：Mermaid 优先，必要时配图
- **代码块**：标注语言（yaml, bash, json）
- **链接**：相对路径链接同目录文档，绝对路径链接外部
- **版本**：文档头部可加「最后更新」日期

---

## 五、与实施计划的衔接

在融合计划的 todo 中增加：

- **wiki-scaffold**：创建 docs/wiki/ 目录结构及 Home.md、Getting-Started.md 骨架
- **wiki-core**：完成 Architecture、Concepts、Workflow、Skills、Rules、Configuration
- **wiki-reference**：完成 simplerig（设计参考）、code-simplifier 子目录文档
- **wiki-ops**：完成 Troubleshooting、FAQ、Contributing、Glossary
- **wiki-sync**：配置 GitHub Wiki 同步（若采用方式 B）
