# 变更日志

## [Unreleased]

### 新增

- codingengine 独立产品：参考 simplerig 设计，不依赖 simplerig
- 参数化：废弃 performance_degradation_point、optimal_context，仅保留 context_limit
- planner.py：按 context_limit 拆分任务
- git_ops.py：原子提交、失败回滚
- stages.py：集成 git_ops 到 develop 阶段
- code-simplifier Skill：Anthropic 插件 Cursor 适配
- codingengine Skill：OMO Just Do、Boulder 续航、ECC 质量门禁
- 3 个精简规则：codingengine-workflow、quality-standards、context-management
- AGENTS.md

### 文档

- docs/wiki/ 完整文档集
- 文档全面扩展：四项目胶水架构详解、各参考项目贡献与融入方式、安装/配置/工作流/故障排查详尽说明
