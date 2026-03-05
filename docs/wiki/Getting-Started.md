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
   python -m venv .venv
   # Windows: .venv\Scripts\Activate.ps1
   # Linux/macOS: source .venv/bin/activate
   pip install -e ./simplerig
   ```

2. **第一次运行**
   ```bash
   simplerig init "My first task"
   # 从输出取得 run_id
   simplerig emit stage.started --stage plan --run-id <run_id>
   # 执行规划...
   simplerig emit stage.completed --stage plan --run-id <run_id>
   ```

3. **预期输出**
   - 所有运行时数据在 `~/.codingengine/runs/<run_id>/`
   - `~/.codingengine/runs/<run_id>/artifacts/plan.json`
   - `~/.codingengine/runs/<run_id>/events.jsonl`
   - 项目目录零新增文件

## 在任意项目中使用

在任意项目目录执行 `simplerig init "任务"`，项目内不会创建 `simplerig_data/` 等文件，所有数据存储在 `~/.codingengine/`。
