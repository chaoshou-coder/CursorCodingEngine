# 评估与基准

## 目标

SWE-bench ~50% → 70-80%+

## 能力分解与预期贡献

| 能力 | 机制 | 预期贡献 |
|------|------|----------|
| 上下文空间拆分 | planner 按 context_limit 拆任务 | +5-8 pp |
| 原子提交+回滚 | 每任务 git commit，失败 revert | +3-5 pp |
| 迭代修复 | verify 失败 → 重试（最多 3 轮） | +10-15 pp |
| 执行纪律 | Just Do + Boulder 续航 | +2-3 pp |
| 质量门禁 | 编辑后 lint + 测试覆盖 | +2-3 pp |

## 评估方式

1. **手工测试**：3-5 个真实 Issue（Django/Flask 已解决），对比裸模型 vs CodingEngine
2. **确认增量后**：搭 SWE-bench 自动化评测
3. **交叉验证**：HumanEval+、MBPP+
