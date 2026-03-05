# 快速开始

## 一、前置要求

- Python 3.10+
- Cursor（用于 Skill 驱动；CLI 可独立使用）
- Git

## 二、5 分钟上手

### 步骤 1：克隆并安装

```bash
git clone https://github.com/chaoshou-coder/CursorCodingEngine.git
cd CursorCodingEngine

# 创建虚拟环境，建议命名 CCEfor<项目名>
python -m venv CCEforCursorCodingEngine

# 激活（Windows PowerShell）
CCEforCursorCodingEngine\Scripts\Activate.ps1
# 激活（Linux/macOS）
# source CCEforCursorCodingEngine/bin/activate

# 安装
pip install -e .
```

### 步骤 2：验证安装

```bash
codingengine --help
pip show codingengine
```

### 步骤 3：第一次运行

```bash
# 初始化新 run，返回 run_id
codingengine init "My first task"

# 从输出取得 run_id，例如 20250305_120000_abcd1234

# 开始 plan 阶段
codingengine emit stage.started --stage plan --run-id <run_id>

# （在 Cursor 中或手动）分析需求，制定 plan.json，保存到
# ~/.codingengine/runs/<run_id>/artifacts/plan.json

# 完成 plan 阶段
codingengine emit stage.completed --stage plan --run-id <run_id>

# 后续 develop、verify 同理...
```

### 步骤 4：预期输出

- **数据目录**：`~/.codingengine/runs/<run_id>/`
- **产物**：`artifacts/plan.json`、`artifacts/code_changes.json`、`artifacts/verify_result.json`
- **事件流**：`events.jsonl`
- **项目目录**：零新增文件，不污染项目

## 三、在任意项目中使用

在任意项目目录执行 `codingengine init "任务"`，项目内不会创建 `simplerig_data/` 等额外目录。所有数据存储在 `~/.codingengine/`，可通过 `CODINGENGINE_DATA` 环境变量覆盖。

### 典型流程

1. 进入目标项目根目录
2. 激活该项目的 venv（建议 `CCEfor<项目名>`）
3. 确保已安装 codingengine：`pip show codingengine`
4. 执行 `codingengine init "简短英文描述"`
5. 按主工作流 Skill 执行 plan → develop → verify

## 四、与 Cursor Skill 配合

若在 Cursor 中使用，需将 `.cursor/skills/` 复制到目标项目，或确保项目能引用本仓库的 skills。主工作流 Skill 会引导 Agent 按阶段调用 `codingengine emit`，并融入 OMO Just Do、Boulder 续航、ECC 质量门禁。

详见 [Skill 系统](Skills.md)。

## 五、下一步

- [安装指南](Installation.md) — 更多安装方式与平台说明
- [配置详解](Configuration.md) — config.yaml 与环境变量
- [工作流详解](Workflow.md) — plan/develop/verify 各阶段细节
- [架构设计](Architecture.md) — 整体架构与数据流
