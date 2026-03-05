"""统计模块"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .events import EventReader, ArtifactStore


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenUsage":
        if not data:
            return cls()
        return cls(
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
        )


@dataclass
class StageStats:
    name: str
    status: str = "unknown"
    duration_ms: int = 0
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "token_usage": self.token_usage.to_dict(),
            "start_time": self.start_time,
            "end_time": self.end_time,
        }


@dataclass
class TaskStats:
    task_id: str
    name: str = ""
    status: str = "unknown"
    duration_ms: int = 0
    token_usage: TokenUsage = field(default_factory=TokenUsage)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RunStats:
    run_id: str
    status: str = "unknown"
    requirement: str = ""
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_duration_ms: int = 0
    total_token_usage: TokenUsage = field(default_factory=TokenUsage)
    token_recorded: bool = False
    stages: Dict[str, StageStats] = field(default_factory=dict)
    tasks: Dict[str, TaskStats] = field(default_factory=dict)
    event_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "requirement": self.requirement,
            "total_duration_ms": self.total_duration_ms,
            "total_token_usage": self.total_token_usage.to_dict(),
            "stages": {k: v.to_dict() for k, v in self.stages.items()},
            "tasks": {k: v.to_dict() for k, v in self.tasks.items()},
        }

    def summary(self) -> str:
        def fmt(ms: int) -> str:
            if ms < 1000:
                return f"{ms}ms"
            elif ms < 60000:
                return f"{ms/1000:.2f}s"
            else:
                return f"{ms//60000}m {(ms%60000)/1000:.1f}s"

        lines = [
            f"Run: {self.run_id}",
            f"状态: {self.status}",
            f"耗时: {fmt(self.total_duration_ms)}",
        ]
        if self.token_recorded:
            lines.append(f"Token: {self.total_token_usage.total_tokens:,}")
        return "\n".join(lines)


def parse_iso_timestamp(ts: str) -> Optional[datetime]:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def calculate_duration(start: str, end: str) -> int:
    s, e = parse_iso_timestamp(start), parse_iso_timestamp(end)
    return int((e - s).total_seconds() * 1000) if s and e else 0


class StatsCollector:
    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.reader = EventReader(run_dir)

    def collect(self) -> RunStats:
        stats = RunStats(run_id=self.run_dir.name)
        stage_starts: Dict[str, str] = {}
        task_starts: Dict[str, str] = {}
        for event in self.reader.iter_events():
            stats.event_count += 1
            if event.type == "run.started":
                stats.status = "running"
                stats.requirement = event.data.get("requirement", "")
                stats.start_time = event.timestamp
            elif event.type == "run.completed":
                stats.status = "completed"
                stats.end_time = event.timestamp
                if "stats" in event.data and "total_token_usage" in event.data["stats"]:
                    stats.total_token_usage = TokenUsage.from_dict(
                        event.data["stats"]["total_token_usage"]
                    )
                    stats.token_recorded = True
            elif event.type == "run.failed":
                stats.status = "failed"
                stats.end_time = event.timestamp
            elif event.type == "stage.started":
                stage_starts[event.data.get("stage", "")] = event.timestamp
                sn = event.data.get("stage", "")
                if sn not in stats.stages:
                    stats.stages[sn] = StageStats(name=sn)
                stats.stages[sn].start_time = event.timestamp
                stats.stages[sn].status = "running"
            elif event.type == "stage.completed":
                sn = event.data.get("stage", "")
                if sn not in stats.stages:
                    stats.stages[sn] = StageStats(name=sn)
                stats.stages[sn].status = "completed"
                stats.stages[sn].end_time = event.timestamp
                stats.stages[sn].duration_ms = event.data.get("duration_ms", 0)
                if "token_usage" in event.data:
                    stats.stages[sn].token_usage = TokenUsage.from_dict(
                        event.data["token_usage"]
                    )
                    stats.total_token_usage = (
                        stats.total_token_usage + stats.stages[sn].token_usage
                    )
                    stats.token_recorded = True
            elif event.type == "stage.failed":
                sn = event.data.get("stage", "")
                if sn not in stats.stages:
                    stats.stages[sn] = StageStats(name=sn)
                stats.stages[sn].status = "failed"
            elif event.type == "llm.called":
                stats.total_token_usage = (
                    stats.total_token_usage
                    + TokenUsage.from_dict(event.data.get("token_usage", {}))
                )
                stats.token_recorded = True
        if stats.start_time and stats.end_time:
            stats.total_duration_ms = calculate_duration(
                stats.start_time, stats.end_time
            )
        return stats


def collect_stats(run_dir: Path) -> RunStats:
    return StatsCollector(run_dir).collect()


def save_stats(run_dir: Path, stats: RunStats):
    ArtifactStore(run_dir).write("stats.json", stats.to_dict())
