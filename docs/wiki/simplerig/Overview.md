# simplerig 概览

## 简介

simplerig 是 CodingEngine 的编排骨架，提供：
- **事件溯源**：events.jsonl 记录所有阶段事件
- **阶段机**：plan → develop → verify → integrate
- **DAG 调度**：任务依赖、并行执行
- **断点续传**：--resume、--from-stage

## 与 CodingEngine 的关系

CodingEngine 在 simplerig 基础上：
- 参数化改造（仅 context_limit）
- 集成 git_ops 原子提交/回滚
- 通过 Skill 融入 OMO/ECC 最佳实践
