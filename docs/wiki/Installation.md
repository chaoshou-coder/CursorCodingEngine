# 安装指南

## 克隆 CursorCodingEngine

```bash
git clone https://github.com/chaoshou-coder/CursorCodingEngine.git
cd CursorCodingEngine
pip install -e .
```

CodingEngine 为独立产品，clone 一次即获得完整工具。

## 验证安装

```bash
codingengine --help
# 或
ce --help
# 或
python -m codingengine.cli --help
pip show codingengine
```

## 虚拟环境

建议在项目虚拟环境中安装。**命名建议**：使用 `CCEfor<项目名>` 格式（如 `CCEforMyApp`、`CCEforEagle`），便于区分多项目环境。

```bash
# 创建 venv（推荐命名：CCEfor<项目名>）
python -m venv CCEforMyApp
# Windows: CCEforMyApp\Scripts\Activate.ps1
# Linux/macOS: source CCEforMyApp/bin/activate
pip install -e .
```

若使用默认 `.venv` 亦可：

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -e .
```

## 平台差异

- **Windows**：PowerShell 不支持 `&&`，用 `;` 分隔命令
- **macOS/Linux**：标准 bash 即可
