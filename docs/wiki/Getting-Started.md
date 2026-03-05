# 快速开始

## 前置要求

- Python 3.10+
- Cursor
- Git

## 5 分钟上手

1. **克隆并安装**
   ```bash
   git clone https://github.com/chaoshou-coder/CursorCodingEngine.git
   cd CursorCodingEngine
   # 创建 venv，建议命名 CCEfor<项目名>（如 CCEforCursorCodingEngine）
   python -m venv CCEforCursorCodingEngine
   # Windows: CCEforCursorCodingEngine\Scripts\Activate.ps1
   # Linux/macOS: source CCEforCursorCodingEngine/bin/activate
   pip install -e .
   ```

2. **第一次运行**
   ```bash
   codingengine init "My first task"
   # 从输出取得 run_id
   codingengine emit stage.started --stage plan --run-id <run_id>
   # 执行规划...
   codingengine emit stage.completed --stage plan --run-id <run_id>
   ```

3. **预期输出**
   - 所有运行时数据在 `~/.codingengine/runs/<run_id>/`
   - `~/.codingengine/runs/<run_id>/artifacts/plan.json`
   - `~/.codingengine/runs/<run_id>/events.jsonl`
   - 项目目录零新增文件

## 在任意项目中使用

在任意项目目录执行 `codingengine init "任务"`，项目内不会创建额外数据目录，所有数据存储在 `~/.codingengine/`（可通过 `CODINGENGINE_DATA` 覆盖）。
