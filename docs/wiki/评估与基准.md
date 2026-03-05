# 评估与基准

## 一、目标

将 SWE-bench 上 ~50% 水平的模型推到 **70-80%+**。增量来自四个参考项目的协同与三个能力的叠加。

## 二、能力分解与预期贡献

| 能力 | 机制 | 来源 | 预期贡献 |
|------|------|------|----------|
| 上下文空间拆分 | planner 按 context_limit 拆任务 | simplerig + OpenSpec | +5-8 pp |
| 原子提交+回滚 | 每任务 git commit，失败 revert | simplerig + git_ops | +3-5 pp |
| 迭代修复 | verify 失败 → 诊断 → 重试（最多 3 轮） | simplerig 阶段机 | +10-15 pp |
| 执行纪律 | Just Do + Boulder 续航 | OMO | +2-3 pp |
| 质量门禁 | 编辑后 lint + 测试覆盖 | ECC | +2-3 pp |

## 三、评估方式

1. **手工测试**：3-5 个真实 Issue（Django/Flask 等已解决），对比裸模型 vs CodingEngine 增强后
2. **确认增量后**：搭建 SWE-bench 自动化评测
3. **交叉验证**：HumanEval+、MBPP+ 代码生成基准

## 四、相关基准

- **SWE-bench** — 主评测基准
- **HumanEval**、**MBPP** — 代码生成基准
- **RULER benchmark** (NVIDIA 2024) — 长上下文性能研究
