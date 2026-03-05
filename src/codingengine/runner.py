"""Runner - 阶段机与断点续传"""

import enum
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from .events import (
    EventWriter,
    EventReader,
    ArtifactStore,
    ArtifactRef,
    create_run_context,
)
from .config import get_config
from .stats import TokenUsage, collect_stats, save_stats


class StageStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    status: StageStatus
    outputs: List[ArtifactRef] = field(default_factory=list)
    error: Optional[str] = None
    duration_ms: int = 0
    token_usage: TokenUsage = field(default_factory=TokenUsage)


@dataclass
class Stage:
    name: str
    handler: Callable = None
    depends_on: List[str] = field(default_factory=list)
    required_inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


@dataclass
class RunState:
    run_id: str
    requirement: str = ""
    status: str = "unknown"
    current_stage: str = ""
    completed_stages: Set[str] = field(default_factory=set)
    failed_stages: Set[str] = field(default_factory=set)
    skipped_stages: Set[str] = field(default_factory=set)
    artifacts: Dict[str, ArtifactRef] = field(default_factory=dict)
    tasks: Dict[str, dict] = field(default_factory=dict)
    last_event_seq: int = 0
    start_time: str = ""
    end_time: str = ""

    def is_stage_done(self, stage_name: str) -> bool:
        return stage_name in self.completed_stages or stage_name in self.skipped_stages

    def can_skip(self, stage: Stage, store: ArtifactStore) -> bool:
        if stage.name not in self.completed_stages:
            return False
        for out in stage.outputs:
            if out not in self.artifacts or not store.verify(self.artifacts[out]):
                return False
        return True


class StateReconstructor:
    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.reader = EventReader(run_dir)

    def reconstruct(self) -> RunState:
        state = RunState(run_id=self.run_dir.name)
        for event in self.reader.iter_events():
            state.last_event_seq = event.seq
            if event.type == "run.started":
                state.status = "running"
                state.requirement = event.data.get("requirement", "")
                state.start_time = event.timestamp
            elif event.type == "run.completed":
                state.status = "completed"
                state.end_time = event.timestamp
            elif event.type == "run.failed":
                state.status = "failed"
                state.end_time = event.timestamp
            elif event.type == "stage.completed":
                state.completed_stages.add(event.data.get("stage", ""))
            elif event.type == "stage.failed":
                state.failed_stages.add(event.data.get("stage", ""))
            elif event.type == "stage.skipped":
                state.skipped_stages.add(event.data.get("stage", ""))
            elif event.type == "artifact.written":
                a = event.data.get("artifact", {})
                if "ref" in a:
                    name = a["ref"].replace("artifacts/", "")
                    state.artifacts[name] = ArtifactRef(
                        ref=a.get("ref", ""),
                        sha256=a.get("sha256", ""),
                        size=a.get("size", 0),
                        mime=a.get("mime", "application/octet-stream"),
                    )
        return state


@dataclass
class StageContext:
    run_id: str
    run_dir: Path
    project_root: Path
    writer: EventWriter
    store: ArtifactStore
    state: RunState
    config: Any
    requirement: str = ""
    options: Dict[str, Any] = field(default_factory=dict)
    stage_name: str = ""
    inputs: Dict[str, ArtifactRef] = field(default_factory=dict)


class StageMachine:
    DEFAULT_STAGES = [
        Stage("plan", outputs=["plan.json"]),
        Stage(
            "develop",
            depends_on=["plan"],
            required_inputs=["plan.json"],
            outputs=["code_changes.json"],
        ),
        Stage(
            "verify",
            depends_on=["develop"],
            required_inputs=["code_changes.json"],
            outputs=["verify_result.json"],
        ),
        Stage(
            "integrate",
            depends_on=["verify"],
            required_inputs=["verify_result.json"],
            outputs=["integration_result.json"],
        ),
    ]

    def __init__(
        self,
        run_dir: Path,
        stages: List[Stage] = None,
        fail_fast: bool = False,
        project_root: Path = None,
    ):
        self.run_dir = Path(run_dir)
        self.stages = stages or self.DEFAULT_STAGES
        self.fail_fast = fail_fast
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.writer, self.store, self.lock = create_run_context(run_dir)
        self._stage_map = {s.name: s for s in self.stages}

    def run(
        self,
        requirement: str = "",
        resume: bool = False,
        from_stage: str = None,
        tdd: bool = False,
        bdd: bool = False,
    ) -> RunState:
        config = get_config()
        lock_timeout = config.timeouts.get("run_lock", 30)
        if not self.lock.acquire(timeout=lock_timeout if lock_timeout else None):
            raise TimeoutError("获取运行锁超时")
        try:
            state = StateReconstructor(self.run_dir).reconstruct()
            if resume:
                if state.status == "completed":
                    return state
                requirement = state.requirement or requirement
            else:
                if not requirement:
                    raise ValueError("缺少需求描述")
                self.writer.emit(
                    "run.started", self.run_dir.name, requirement=requirement
                )
                state.requirement = requirement
                state.status = "running"
            start_idx = 0
            if from_stage:
                start_idx = next(
                    i for i, s in enumerate(self.stages) if s.name == from_stage
                )
                for i in range(start_idx):
                    s = self.stages[i]
                    if not state.is_stage_done(s.name):
                        self.writer.emit(
                            "stage.skipped",
                            self.run_dir.name,
                            stage=s.name,
                            reason="from_stage",
                        )
                        state.skipped_stages.add(s.name)
            ctx = StageContext(
                run_id=self.run_dir.name,
                run_dir=self.run_dir,
                project_root=self.project_root,
                writer=self.writer,
                store=self.store,
                state=state,
                config=config,
                requirement=requirement,
                options={"tdd": tdd, "bdd": bdd},
            )
            for i in range(start_idx, len(self.stages)):
                stage = self.stages[i]
                if state.can_skip(stage, self.store):
                    self.writer.emit(
                        "stage.skipped",
                        self.run_dir.name,
                        stage=stage.name,
                        reason="skip",
                    )
                    state.skipped_stages.add(stage.name)
                    continue
                if stage.name in state.completed_stages:
                    state.completed_stages.discard(stage.name)
                if stage.name in state.failed_stages and resume:
                    state.failed_stages.discard(stage.name)
                result = self._execute_stage(ctx, stage)
                if result.status == StageStatus.FAILED and self.fail_fast:
                    self.writer.emit(
                        "run.failed",
                        self.run_dir.name,
                        error=result.error,
                        stage=stage.name,
                    )
                    state.status = "failed"
                    return state
            if all(state.is_stage_done(s.name) for s in self.stages):
                run_stats = collect_stats(self.run_dir)
                self.writer.emit(
                    "run.completed",
                    self.run_dir.name,
                    stats={
                        "total_duration_ms": run_stats.total_duration_ms,
                        "total_token_usage": run_stats.total_token_usage.to_dict(),
                        "stages": {k: v.to_dict() for k, v in run_stats.stages.items()},
                    },
                )
                save_stats(self.run_dir, run_stats)
                state.status = "completed"
            return state
        finally:
            self.lock.release()

    def _execute_stage(self, ctx: StageContext, stage: Stage) -> StageResult:
        start = time.time()
        ctx.stage_name = stage.name
        ctx.inputs = {
            n: ctx.state.artifacts[n]
            for n in stage.required_inputs
            if n in ctx.state.artifacts
        }
        _role = {
            "plan": "planner",
            "develop": "dev",
            "verify": "verifier",
            "integrate": "verifier",
        }.get(stage.name, "dev")
        self.writer.emit(
            "stage.started",
            self.run_dir.name,
            stage=stage.name,
            model=ctx.config.roles.get(_role, "unknown"),
            inputs=list(ctx.inputs.keys()),
        )
        try:
            result = (
                stage.handler(ctx) if stage.handler else self._stub_handler(ctx, stage)
            )
            result.duration_ms = int((time.time() - start) * 1000)
            if result.status == StageStatus.COMPLETED:
                self.writer.emit(
                    "stage.completed",
                    self.run_dir.name,
                    stage=stage.name,
                    outputs=[r.to_dict() for r in result.outputs],
                    duration_ms=result.duration_ms,
                    token_usage=result.token_usage.to_dict(),
                )
                ctx.state.completed_stages.add(stage.name)
            elif result.status == StageStatus.FAILED:
                self.writer.emit(
                    "stage.failed",
                    self.run_dir.name,
                    stage=stage.name,
                    error=result.error,
                    duration_ms=result.duration_ms,
                )
                ctx.state.failed_stages.add(stage.name)
            return result
        except Exception as e:
            self.writer.emit(
                "stage.failed",
                self.run_dir.name,
                stage=stage.name,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
            )
            ctx.state.failed_stages.add(stage.name)
            return StageResult(
                status=StageStatus.FAILED,
                error=str(e),
                duration_ms=int((time.time() - start) * 1000),
            )

    def _stub_handler(self, ctx: StageContext, stage: Stage) -> StageResult:
        outputs = []
        for out in stage.outputs:
            content = {
                "stage": stage.name,
                "run_id": ctx.run_id,
                "requirement": ctx.requirement,
                "inputs": list(ctx.inputs.keys()),
                "stub": True,
            }
            ref = ctx.store.write(out, content)
            outputs.append(ref)
            ctx.writer.emit("artifact.written", ctx.run_id, artifact=ref.to_dict())
            ctx.state.artifacts[out] = ref
        return StageResult(status=StageStatus.COMPLETED, outputs=outputs)
