# CodingEngine 需求与解决方案

> 本文档为项目开发的单一参考，整合需求、解决方案与实施路线。后续开发请以此为准。

**最后更新**：2025-03-05

---

## 一、项目概览

### 1.1 一句话描述

CodingEngine 是 Cursor 专属的 Agentic Coding 基础设施，通过**任务工程**让 SWE-bench 上 ~50% 水平的模型达到 70-80%+。

### 1.2 核心价值主张

**任务工程**：按模型上下文空间拆分不可能的大任务为可能的小任务，每个原子化、可回滚、可并行，失败自动诊断修复。弱模型通过工程手段达到强模型效果。（类似 MapReduce 的思路）

### 1.3 三大能力

| 能力 | 含义 | 实现载体 |
|------|------|----------|
| **编排能力** | 把复杂任务拆成模型能处理的粒度，按依赖并行执行 | simplerig DAG + planner |
| **执行能力** | 每个子任务原子化，解耦可回滚，结果可验证 | git_ops 原子提交 |
| **迭代能力** | 验证失败时自动反馈修复，不止一轮 | verify → 诊断 → 重试 |

---

## 二、需求规格

### 2.1 功能需求

| ID | 需求 | 优先级 |
|----|------|--------|
| R1 | 按模型 context_limit 拆分任务，不依赖性能拐点 | P0 |
| R2 | 任务按 DAG 依赖并行执行 | P0 |
| R3 | 每个任务完成后原子 git commit，失败可回滚 | P0 |
| R4 | verify 失败时诊断、回滚失败任务、重试（最多 3 轮） | P0 |
| R5 | 事件溯源（events.jsonl），可审计、可重放、可断点续传 | P0 |
| R6 | 在 develop 流程中集成 code-simplifier 清理代码 | P1 |
| R7 | 通过 Skill 引导 Agent 执行纪律（Just Do、Boulder 续航、Wisdom 积累） | P1 |
| R8 | 通过 Rules 引导质量门禁（编辑后 lint、测试覆盖、安全底线） | P1 |
| R9 | 静态上下文注入（AGENTS.md） | P1 |
| R10 | 详尽 Wiki 文档集，可上传 GitHub | P2 |

### 2.2 非功能需求

| ID | 需求 | 说明 |
|----|------|------|
| NFR1 | 控制复杂度 | 不建 14 Agent、60+ Skill、Hook 适配层 |
| NFR2 | 利用已有技术 | simplerig 为基座，ECC/OMO/OpenSpec 为参考 |
| NFR3 | Skill 即胶水 | SKILL.md 为唯一集成点，不引入额外运行时依赖 |
| NFR4 | Cursor only | 不做多平台适配 |
| NFR5 | 可配置 | 模型、工具链、超时等从 config.yaml 读取，不硬编码 |

### 2.3 约束

- **技术栈**：Python（simplerig）+ Cursor + Markdown（Skill/Rules）
- **参考项目**：simplerig（自有）、ECC、OMO、OpenSpec、Anthropic code-simplifier（只读参考）
- **不采用**：TypeScript 工具链、ECC hooks/adapter、OpenSpec CLI 完整集成

### 2.4 成功标准

- SWE-bench 上 50% 模型经 CodingEngine 增强后达到 70-80%+（手工验证 3-5 个 Issue）
- 任务可断点续传、可审计
- 文档完整，新开发者可依 Wiki 上手

---

## 三、解决方案

### 3.1 架构总览

```
用户需求 → Cursor Agent 读 SKILL.md
         → 调用 simplerig init/emit
         → simplerig: plan → develop(DAG 并行) → verify
         → 每 task: 修改 → lint → code-simplifier → 原子提交
         → 失败: 诊断 → revert → 重试
```

**设计决策**：
- **simplerig** 为编排骨架（事件溯源、DAG、断点续传）
- **Skill 即胶水**：OMO/ECC/OpenSpec 的最佳实践提炼为 SKILL.md 中的自然语言指令
- **Rules** 代替 Hook：3 个 .mdc 规则引导行为

### 3.2 组件与职责

| 组件 | 职责 | 改动 |
|------|------|------|
| simplerig/config.py | 模型与项目配置 | 废弃 performance_degradation_point、optimal_context，仅保留 context_limit |
| simplerig/config.yaml | 配置源 | 同上 |
| simplerig/planner.py | 任务拆分 | 使用 context_limit 作为拆分依据；plan.json 增加 atomic_commit、rollback_strategy、dependencies、decoupled |
| simplerig/git_ops.py | Git 原子操作 | **新增**：原子提交（task_id 标记）、失败回滚（git revert） |
| simplerig/runner.py | 阶段执行 | 集成 git_ops，每任务执行后原子提交 |
| .cursor/skills/simplerig/SKILL.md | 主工作流 | **增强**：融入 OMO Just Do、Boulder 续航、ECC 质量模式、Wisdom 积累 |
| .cursor/skills/code-simplifier/SKILL.md | 代码清理 | **新增**：从 Anthropic 提取，泛化语言栈 |
| .cursor/rules/*.mdc | 行为引导 | **替换**：3 个规则（workflow、quality、context） |
| AGENTS.md | 项目上下文 | **新增**：静态注入 |

### 3.3 工作流

```
plan 阶段
  ├─ simplerig emit stage.started --stage plan
  ├─ 按 context_limit 拆分任务 → plan.json
  └─ simplerig emit stage.completed --stage plan

develop 阶段
  ├─ simplerig emit stage.started --stage develop
  ├─ DAG 并行：task_1, task_2, ... (无依赖可并行)
  │   └─ 每 task: 修改 → lint → code-simplifier → git commit (atomic)
  └─ simplerig emit stage.completed --stage develop

verify 阶段
  ├─ simplerig emit stage.started --stage verify
  ├─ 全量 lint + test
  ├─ 失败 → 诊断 → git revert 失败 task → 重试 (最多 3 轮)
  └─ 通过 → wisdom 记录 → simplerig emit run.completed
```

### 3.4 从参考项目提炼的模式

| 来源 | 模式 | 融入位置 |
|------|------|----------|
| OMO | "Do NOT Ask — Just Do" | SKILL.md develop 阶段 |
| OMO | Boulder 续航（任务未完成不结束 turn） | SKILL.md |
| OMO | Wisdom 积累（learnings → wisdom.jsonl） | SKILL.md verify 阶段 |
| ECC | 编辑后立即 lint | SKILL.md + quality-standards.mdc |
| ECC | Confidence-Based Review（>80% 确信才报） | SKILL.md |
| ECC | Severity 分级（CRITICAL 阻塞） | SKILL.md |
| Anthropic | code-simplifier（Preserve Functionality, Apply Standards, Enhance Clarity） | code-simplifier/SKILL.md |
| OpenSpec | 任务依赖、模块解耦 | plan.json dependencies、decoupled |

### 3.5 明确不做的

| 不做 | 原因 |
|------|------|
| 14 个 Agent 定义 | Skill 已驱动 Agent，Cursor 内置 subagent 够用 |
| 60+ Skill | 过度复杂，逻辑并入 simplerig SKILL |
| ECC Hook 适配层 | Rules 足够 |
| OpenSpec CLI 集成 | simplerig plan.json 已覆盖 |
| 多平台适配 | Cursor only |

---

## 四、目标目录结构

```
CursorCodingEngine/
├── .cursor/
│   ├── rules/
│   │   ├── codingengine-workflow.mdc
│   │   ├── quality-standards.mdc
│   │   └── context-management.mdc
│   └── skills/
│       ├── simplerig/SKILL.md
│       └── code-simplifier/SKILL.md
├── simplerig/                    # 克隆或 submodule
│   ├── simplerig/
│   │   ├── config.py             # 参数化改造
│   │   ├── planner.py            # 上下文空间拆分
│   │   ├── runner.py             # 集成 git_ops
│   │   ├── git_ops.py            # 新增
│   │   └── ...
│   └── config.yaml               # 废弃性能拐点
├── docs/
│   ├── requirements_and_solutions.md   # 本文档
│   ├── plan_fusion_analysis.md
│   ├── wiki_spec.md
│   └── wiki/                     # Wiki 文档集
├── AGENTS.md
├── config.yaml
├── oh-my-opencode/               # 参考（只读）
├── everything-claude-code/       # 参考（只读）
└── OpenSpec/                     # 参考（只读）
```

---

## 五、实施路线

### 5.1 执行顺序

| 步骤 | 任务 | 产出 |
|------|------|------|
| 1 | 克隆 simplerig | simplerig/ 可运行 |
| 2 | 参数化 config | 废弃性能拐点，仅 context_limit |
| 3 | 修改 planner | 按 context_limit 拆分 |
| 4 | 新增 git_ops | 原子提交、回滚 |
| 5 | 修改 runner | 集成 git_ops |
| 6 | 引入 code-simplifier | .cursor/skills/code-simplifier/SKILL.md |
| 7 | 升级 simplerig SKILL | 融入 OMO/ECC 模式 |
| 8 | 替换 Rules | 3 个 .mdc |
| 9 | 创建 AGENTS.md | 项目上下文 |
| 10 | 手工测试 | 3-5 个真实 Issue 验证 |
| 11 | Wiki 文档集 | docs/wiki/ 完整，可传 GitHub |

### 5.2 预期提升（行业研究）

| 能力 | 机制 | 预期贡献 |
|------|------|----------|
| 上下文空间拆分 | planner 按 context_limit 拆任务 | +5-8 pp |
| 原子提交+回滚 | 每任务 git commit，失败 revert | +3-5 pp |
| 迭代修复 | verify 失败 → 诊断 → 重试 | +10-15 pp |
| 执行纪律 | Just Do + Boulder 续航 | +2-3 pp |
| 质量门禁 | 编辑后 lint + 测试覆盖 | +2-3 pp |

### 5.3 评估方式

1. 手工测试：Django/Flask 等 3-5 个已解决 Issue，对比裸模型 vs CodingEngine
2. 确认增量后搭建 SWE-bench 自动化
3. 扩展 HumanEval+/MBPP+ 交叉验证

---

## 六、风险与缓解

| 风险 | 缓解 |
|------|------|
| Agent prompt 质量影响 SWE-bench | 基准驱动迭代优化 prompt |
| 上下文窗口限制 | 压缩恢复 + 静态注入 |
| Cursor 平台限制 | 优先适配，不支持则降级 |
| 评测环境 | 独立 benchmarks/ 目录管理 |

---

## 七、相关文档索引

| 文档 | 用途 |
|------|------|
| `docs/requirements_and_solutions.md` | 本文档，需求与方案总览 |
| `docs/plan_fusion_analysis.md` | 两计划融合分析 |
| `docs/wiki_spec.md` | Wiki 文档集规格 |
| `.cursor/plans/codingengine_revised_plan_*.plan.md` | 实施计划与 todo |

---

## 八、术语表

| 术语 | 说明 |
|------|------|
| 任务工程 | 通过工程手段（拆分、原子化、迭代）让弱模型达到强模型效果 |
| Skill 即胶水 | SKILL.md 为唯一集成点，不引入额外代码依赖 |
| context_limit | 模型上下文窗口大小，任务拆分依据 |
| 原子提交 | 每任务独立 git commit，含 task_id，失败可 revert |
| DAG | 有向无环图，任务依赖与并行调度 |
| Wisdom | 跨任务学习记录，写入 wisdom.jsonl |
| Boulder 续航 | 任务未完成时不结束 turn，注入 continuation |
