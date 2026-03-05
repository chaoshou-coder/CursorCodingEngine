# 故障排查

## codingengine 命令不可用

**可能原因**：未激活虚拟环境、装到错误环境、PATH 未包含 Scripts/bin。

**排查步骤**：
1. 确认已激活项目 venv（建议命名 `CCEfor<项目名>`，便于区分）
2. 使用 `python -m codingengine.cli` 替代 `codingengine`
3. 执行 `pip install -e .` 确保已安装
4. 检查 `pip show codingengine` 的 Location 是否指向当前项目

## config.yaml 未找到

**可能原因**：项目根目录无 config.yaml，且未设置 `CODINGENGINE_CONFIG`。

**解决**：codingengine 有内置默认值，可直接运行。若需自定义，在项目根创建 `config.yaml`，或设置 `CODINGENGINE_CONFIG` 指向配置文件路径。

## plan 阶段卡住

**可能原因**：plan.json 结构不符合预期、context_limit 未配置、Agent 未正确执行规划逻辑。

**排查步骤**：
1. 检查 `~/.codingengine/runs/<run_id>/artifacts/plan.json` 是否存在且结构正确
2. 确认 config.yaml 中 models.registry 已配置 context_limit
3. 确认主工作流 Skill 已启用，Agent 按阶段执行

## develop 阶段 lint 失败

**可能原因**：代码引入 lint 错误、linter 配置与项目不符。

**解决**：按 quality-standards 修复。编辑后立即 lint，不攒到最后。可调整 config.yaml 中的 tools.linter、linter_args。

## verify 阶段测试失败

**可能原因**：单元测试失败、集成问题、环境依赖缺失。

**解决**：诊断失败原因 → 回滚失败任务（`git revert`）→ 重试（最多 3 轮）。检查 test_runner 配置与测试环境。

## 原子提交冲突

**可能原因**：多个 task 修改同一文件、git 状态异常。

**解决**：检查 `git status`，必要时手动 resolve 冲突后重试。确保每个 task 修改范围清晰，减少跨 task 重叠。

## 断点续传失败

**可能原因**：events.jsonl 不完整、run_id 错误、状态不一致。

**排查步骤**：
1. `codingengine status` 查看最近运行状态
2. `codingengine tail` 查看事件流
3. 检查 `~/.codingengine/runs/<run_id>/events.jsonl` 完整性
4. 使用 `--from-stage` 从指定阶段重新开始

## 虚拟环境装错项目

**现象**：`pip show codingengine` 的 Location 指向其他项目。

**解决**：先激活目标项目的 venv，再执行 `pip install -e .`。使用 `CCEfor<项目名>` 命名 venv，便于区分。
