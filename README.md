# CodingEngine

编排+执行+迭代的 AI 辅助开发工具。**不污染项目目录**，所有数据在 `~/.codingengine/`。

## 快速开始

```bash
git clone https://github.com/chaoshou-coder/CursorCodingEngine.git
cd CursorCodingEngine
pip install -e .
codingengine init "我的第一个任务"
```

或使用短别名：

```bash
ce init "我的任务"
```

## 前置要求

- Python 3.10+
- Cursor（可选，用于 Skill 驱动）
- Git

## 核心特性

- **不污染项目目录**：runs、events、artifacts 全部在 `~/.codingengine/runs/`，项目内零新增文件
- **编排能力**：按 context_limit 拆分任务，DAG 依赖
- **执行能力**：原子提交、失败回滚
- **迭代能力**：verify 失败 → 诊断 → 重试（最多 3 轮）

## 常用命令

| 命令 | 说明 |
|------|------|
| `codingengine init "需求"` | 初始化新 run |
| `codingengine run "需求"` | 运行工作流 |
| `codingengine run --resume` | 断点续传 |
| `codingengine status` | 查看状态 |
| `codingengine list` | 列出历史运行 |
| `codingengine stats` | 统计 |

## 环境变量

- `CODINGENGINE_DATA`：覆盖数据目录（默认 `~/.codingengine`）
- `CODINGENGINE_CONFIG`：配置文件路径

## 文档

- [快速开始](docs/wiki/Getting-Started.md)
- [安装指南](docs/wiki/Installation.md)
- [配置详解](docs/wiki/Configuration.md)

## 设计参考

simplerig 设计思路，独立实现。
