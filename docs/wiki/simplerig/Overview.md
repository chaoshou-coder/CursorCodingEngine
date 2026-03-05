# simplerig 概览（设计参考）

## 简介

simplerig 是 CodingEngine 的设计参考，提供：
- **事件溯源**：events.jsonl 记录所有阶段事件
- **阶段机**：plan → develop → verify → integrate
- **DAG 调度**：任务依赖、并行执行
- **断点续传**：--resume、--from-stage

## 与 CodingEngine 的关系

CodingEngine 参考 simplerig 设计，作为**独立产品**实现：
- 不依赖 simplerig，无需安装 simplerig
- 参数化改造（仅 context_limit）
- 集成 git_ops 原子提交/回滚
- 通过 Skill 融入 OMO/ECC 最佳实践

> 本仓库中的 `simplerig/` 目录为参考代码，不参与安装与运行。
