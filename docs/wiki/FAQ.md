# 常见问题

## 为什么用 simplerig 而不是自己写？

simplerig 已提供事件溯源、DAG、断点续传。CodingEngine 在其上做胶水即可，无需从零开发。

## 为什么不需要 14 个 Agent？

Cursor 内置 subagent 够用。Skill 驱动行为，不建额外 Agent 层。

## 为什么废弃性能拐点？

用户要求仅保留 context_limit。性能拐点增加复杂性，收益不明确。

## code-simplifier 会增加 token 消耗吗？

会，但通常可减少 20-30% 后续维护的 token。在 task 提交前调用，可控。

## 支持非 Python 项目吗？

支持。配置可指定 linter、formatter、test_runner。code-simplifier 已泛化。

## 如何扩展 Skill？

在 `.cursor/skills/` 下新建目录，含 SKILL.md。参考 simplerig、code-simplifier 格式。
