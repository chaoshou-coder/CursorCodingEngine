# 安装指南

## 克隆 CursorCodingEngine

```bash
git clone https://github.com/chaoshou-coder/CursorCodingEngine.git
cd CursorCodingEngine
pip install -e ./simplerig
```

simplerig 已纳入主仓库，clone 一次即获得完整产品。

## 验证安装

```bash
simplerig --help
# 或
python -m simplerig.cli --help
pip show simplerig
```

## 虚拟环境

建议在项目 `.venv` 中安装：

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -e ./simplerig
```

## 平台差异

- **Windows**：PowerShell 不支持 `&&`，用 `;` 分隔命令
- **macOS/Linux**：标准 bash 即可
