# config.yaml 完整参考

## models.registry

```yaml
models:
  registry:
    <model_name>:
      provider: "cursor" | "api"
      context_limit: 272000  # 必填，任务拆分依据
      strengths: []
      cost_per_1k: 0.0
      tier: "standard"
```

## models.roles

```yaml
  roles:
    architect: "cursor/opus-4.6-max"
    planner: "cursor/opus-4.6-max"
    dev: "cursor/gpt-5.2-codex-extra-high"
    verifier: "cursor/auto"
```

## paths

```yaml
paths:
  database: "${SIMPLERIG_DB:-./simplerig_data/memory.db}"
  logs: "${SIMPLERIG_LOGS:-./simplerig_data/logs}"
```

## tools

```yaml
tools:
  linter: "ruff"
  formatter: "black"
  test_runner: "pytest"
```
