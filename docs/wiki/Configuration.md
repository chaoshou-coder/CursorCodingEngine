# 配置详解

## 配置文件位置

- 项目根 `config.yaml`
- 或环境变量 `CODINGENGINE_CONFIG` 指向的路径

## 模型配置

仅保留 `context_limit` 作为任务拆分依据。已废弃：
- `performance_degradation_point`
- `optimal_context`

示例：
```yaml
models:
  registry:
    cursor/gpt-5.2-codex:
      provider: "cursor"
      context_limit: 272000
      strengths: ["code_gen", "bug_fixing"]
```

## 项目结构

```yaml
project:
  source_dirs: ["src", "lib"]
  test_dirs: ["tests", "test"]
```

## 工具链

```yaml
tools:
  linter: "ruff"
  formatter: "black"
  test_runner: "pytest"
```

## 环境变量

- `CODINGENGINE_CONFIG` — 配置文件路径
- `CODINGENGINE_DATA` — 数据目录（默认 `~/.codingengine`）
- `CODINGENGINE_LOGS` — 日志路径
