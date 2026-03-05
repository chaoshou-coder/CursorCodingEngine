# simplerig CLI 参考

## init

```bash
simplerig init "Short description"
python -m simplerig.cli init "Short description"
```

创建新 run，返回 run_id。

## emit

```bash
simplerig emit stage.started --stage plan --run-id <run_id>
simplerig emit stage.completed --stage plan --run-id <run_id>
simplerig emit run.completed --run-id <run_id>
```

## list

列出 runs。

## status

查看最近运行状态。

## tail

```bash
simplerig tail --follow
```

实时查看事件流。

## stats

```bash
simplerig stats
```

Token 统计。

## run

```bash
simplerig run "需求" --tdd
simplerig run "需求" --bdd
simplerig run "需求" --resume
```

## bdd

```bash
simplerig bdd generate spec.json -o features/
simplerig bdd run features/demo.feature --report html
```
