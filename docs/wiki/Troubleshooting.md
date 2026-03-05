# 故障排查

## simplerig 命令不可用

- 确认已激活项目 .venv
- 使用 `python -m simplerig.cli`
- `pip install -e ./simplerig`

## config.yaml 未找到

- 检查项目根目录
- 设置 `SIMPLERIG_CONFIG` 环境变量

## plan 阶段卡住

- 检查 plan.json 结构
- 确认 context_limit 已配置

## develop 阶段 lint 失败

- 编辑后立即 lint
- 按 quality-standards 修复

## verify 阶段测试失败

- 诊断失败原因
- 回滚失败任务后重试

## 原子提交冲突

- 检查 git 状态
- 必要时手动 resolve 后重试

## 断点续传失败

- `simplerig status` 查看状态
- 检查 events.jsonl 完整性
