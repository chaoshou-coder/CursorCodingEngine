# codingengine CLI 参考

> 本页为 codingengine 命令参考。simplerig 为设计参考，实际使用 codingengine。

## init

```bash
codingengine init "Short description"
ce init "Short description"
python -m codingengine.cli init "Short description"
```

创建新 run，返回 run_id。

## emit

```bash
codingengine emit stage.started --stage plan --run-id <run_id>
codingengine emit stage.completed --stage plan --run-id <run_id>
codingengine emit run.completed --run-id <run_id>
```

## list

列出 runs。

## status

查看最近运行状态。

## tail

```bash
codingengine tail --follow
```

实时查看事件流。

## stats

```bash
codingengine stats
```

Token 统计。

## run

```bash
codingengine run "需求" --tdd
codingengine run "需求" --bdd
codingengine run "需求" --resume
```

## bdd

```bash
codingengine bdd generate spec.json -o features/
codingengine bdd run features/demo.feature --report html
```
