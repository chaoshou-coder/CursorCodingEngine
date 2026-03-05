# 架构设计

## 整体架构

```mermaid
flowchart TB
    subgraph 编排
        A[需求] --> B[plan]
        B --> C[plan.json]
        C --> D[develop]
    end
    subgraph 执行
        D --> E[task_1]
        D --> F[task_2]
        E --> G[lint]
        F --> G
        G --> H[code-simplifier]
        H --> I[原子提交]
    end
    subgraph 迭代
        I --> J[verify]
        J -->|失败| K[回滚]
        K --> D
        J -->|通过| L[完成]
    end
```

## 三层能力

1. **编排** — codingengine planner 按 context_limit 拆分，DAG 调度
2. **执行** — 每 task 原子提交，失败可回滚
3. **迭代** — verify 失败 → 诊断 → 重试（最多 3 轮）

## 数据流

```
用户需求 → init → plan → plan.json
         → develop → 修改 → lint → code-simplifier → commit
         → verify → 通过/失败
         → 完成
```

## 目录结构

见 [AGENTS.md](../../AGENTS.md)。
