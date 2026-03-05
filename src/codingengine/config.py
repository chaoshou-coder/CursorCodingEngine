"""
Config - 统一配置加载器
所有配置从 config.yaml 读取，默认路径 ~/.codingengine
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


def _data_dir() -> Path:
    """数据目录，默认 ~/.codingengine"""
    return Path(os.environ.get("CODINGENGINE_DATA", "~/.codingengine")).expanduser().resolve()


@dataclass
class ModelConfig:
    """模型配置"""
    context_limit: int
    strengths: list
    cost_per_1k: float = 0.0
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    provider: str = "cursor"
    tier: str = "standard"
    max_output: int = 0

    @property
    def safe_limit(self) -> int:
        """安全上下文上限"""
        return self.context_limit


@dataclass
class Config:
    """CodingEngine 配置"""
    models: Dict[str, ModelConfig] = field(default_factory=dict)
    roles: Dict[str, str] = field(default_factory=dict)
    api: Dict[str, Any] = field(default_factory=dict)
    paths: Dict[str, Path] = field(default_factory=dict)
    project: Dict[str, list] = field(default_factory=dict)
    tools: Dict[str, Any] = field(default_factory=dict)
    timeouts: Dict[str, int] = field(default_factory=dict)
    parallel: Dict[str, int] = field(default_factory=dict)
    budget: Dict[str, float] = field(default_factory=dict)
    logging: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, config_path: str = "config.yaml") -> "Config":
        """加载配置"""
        path = cls._find_config(config_path)
        if not path:
            return cls._default()
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls._parse(data)

    @classmethod
    def _find_config(cls, config_path: str) -> Optional[Path]:
        """查找配置文件"""
        path = Path(config_path)
        if path.exists():
            return path
        if env_path := os.getenv("CODINGENGINE_CONFIG"):
            p = Path(env_path)
            if p.exists():
                return p
        for location in [
            "./config.yaml",
            os.path.expanduser("~/.config/codingengine/config.yaml"),
            _data_dir() / "config.yaml",
        ]:
            p = Path(location)
            if p.exists():
                return p
        return None

    @classmethod
    def _parse(cls, data: Dict) -> "Config":
        """解析配置数据"""
        import warnings
        models = {}
        for name, info in data.get("models", {}).get("registry", {}).items():
            info = dict(info)
            if "performance_degradation_point" in info or "optimal_context" in info:
                warnings.warn(
                    "performance_degradation_point and optimal_context are deprecated",
                    DeprecationWarning,
                    stacklevel=2,
                )
            info.pop("performance_degradation_point", None)
            info.pop("optimal_context", None)
            if "strengths" not in info:
                info["strengths"] = []
            models[name] = ModelConfig(**info)

        base = _data_dir()
        default_paths = {"database": base / "memory.db", "logs": base / "logs", "temp": base / "temp"}
        paths = {}
        for key, value in data.get("paths", {}).items():
            if isinstance(value, str):
                value = os.path.expandvars(value)
                value = os.path.expanduser(value)
                value = value.replace("./simplerig_data/", str(base) + "/")
                p = Path(value)
                if not p.is_absolute():
                    p = (base / value.lstrip("./")).resolve()
                paths[key] = p
            else:
                paths[key] = value
        for k, v in default_paths.items():
            paths.setdefault(k, v)

        return cls(
            models=models,
            roles=data.get("models", {}).get("roles", {}),
            api=data.get("api", {}),
            paths=paths,
            project=data.get("project", {}),
            tools=data.get("tools", {}),
            timeouts=data.get("timeouts", {}),
            parallel=data.get("parallel", {}),
            budget=data.get("budget", {}),
            logging=data.get("logging", {}),
        )

    @classmethod
    def _default(cls) -> "Config":
        """默认配置"""
        base = _data_dir()
        return cls(
            models={
                "opencode/kimi-k2.5-free": ModelConfig(
                    context_limit=8000,
                    cost_per_1k=0.0,
                    strengths=["code_gen", "text_analysis"],
                ),
                "openai/gpt-5.2-codex": ModelConfig(
                    context_limit=128000,
                    cost_per_1k=0.002,
                    strengths=["complex_reasoning", "reliable"],
                ),
            },
            roles={
                "architect": "openai/gpt-5.2-codex",
                "planner": "openai/gpt-5.2-codex",
                "dev": "opencode/kimi-k2.5-free",
            },
            paths={
                "database": base / "memory.db",
                "logs": base / "logs",
                "temp": base / "temp",
            },
            project={"source_dirs": ["src"], "test_dirs": ["tests"]},
            tools={
                "linter": "ruff",
                "formatter": "black",
                "test_runner": "pytest",
                "linter_args": ["check", "--fix"],
                "formatter_args": [],
                "test_runner_args": ["-v"],
            },
            timeouts={"tdd_max_retries": 3, "monitor_stall": 60, "run_lock": 30, "tool": 300},
            parallel={"default_agents": 3, "task_groups": 3},
        )

    def get_model(self, role: str) -> tuple[str, ModelConfig]:
        """获取角色对应的模型"""
        model_name = self.roles.get(role, "opencode/kimi-k2.5-free")
        config = self.models.get(model_name)
        if not config:
            config = ModelConfig(context_limit=8000, cost_per_1k=0.002, strengths=[])
        return model_name, config

    def get_timeout(self, key: str, default: int = 60) -> int:
        """获取超时配置"""
        return self.timeouts.get(key, default)


_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置"""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config():
    """重新加载配置"""
    global _config
    _config = Config.load()
