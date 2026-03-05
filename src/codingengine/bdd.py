"""BDD - Gherkin 解析与执行"""
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .events import ArtifactStore, EventWriter


@dataclass
class Step:
    keyword: str
    text: str
    line_number: int = 0


@dataclass
class Scenario:
    name: str
    steps: List[Step] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class Feature:
    name: str
    description: str = ""
    scenarios: List[Scenario] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class StepResult:
    step: Step
    passed: bool
    error: Optional[str] = None


@dataclass
class ScenarioResult:
    scenario: Scenario
    steps: List[StepResult]
    passed: bool


@dataclass
class TestResult:
    feature_path: str
    feature_name: str
    scenarios: List[ScenarioResult]
    passed: bool
    duration_ms: int = 0


def _parse_gherkin(content: str) -> Feature:
    lines = content.split("\n")
    feature = Feature(name="")
    current_scenario = None
    for i, raw in enumerate(lines):
        ln, line = i + 1, raw.strip()
        if not line:
            continue
        if line.lower().startswith("feature:"):
            feature.name = line[8:].strip()
        elif line.lower().startswith("scenario:"):
            if current_scenario:
                feature.scenarios.append(current_scenario)
            current_scenario = Scenario(name=line[9:].strip())
        elif re.match(r"^(given|when|then|and|but)\s", line, re.I):
            if current_scenario is None:
                current_scenario = Scenario(name="(no name)")
            m = re.match(r"^(given|when|then|and|but)\s+(.*)$", line, re.I)
            if m:
                current_scenario.steps.append(Step(keyword=m.group(1).capitalize(), text=m.group(2).strip(), line_number=ln))
    if current_scenario:
        feature.scenarios.append(current_scenario)
    return feature


class BDDRunner:
    def __init__(self, config, writer: EventWriter, run_id: str, store: Optional[ArtifactStore] = None):
        self.config = config
        self.writer = writer
        self.run_id = run_id
        self.store = store
        self._steps: Dict[str, Callable] = {}

    def register_step(self, pattern: str, func: Callable):
        self._steps[pattern] = func

    def _match_step(self, text: str) -> tuple[Optional[Callable], Optional[dict]]:
        for pattern, func in self._steps.items():
            if pattern.strip() == text.strip():
                return func, {}
        return None, None

    def run_feature(self, feature_path: Path) -> TestResult:
        start = time.perf_counter()
        path = Path(feature_path)
        feature = _parse_gherkin(path.read_text(encoding="utf-8"))
        self.writer.emit("bdd.feature_started", self.run_id, path=str(path), feature=feature.name)
        scenario_results = []
        all_passed = True
        for sc in feature.scenarios:
            step_results = []
            sc_passed = True
            for step in sc.steps:
                func, params = self._match_step(step.text)
                try:
                    if func:
                        func(**params) if params else func()
                    step_results.append(StepResult(step=step, passed=True))
                except Exception as e:
                    step_results.append(StepResult(step=step, passed=False, error=str(e)))
                    sc_passed = False
            scenario_results.append(ScenarioResult(scenario=sc, steps=step_results, passed=sc_passed))
            if not sc_passed:
                all_passed = False
        duration_ms = int((time.perf_counter() - start) * 1000)
        self.writer.emit("bdd.feature_completed", self.run_id, path=str(path), feature=feature.name, passed=all_passed, duration_ms=duration_ms)
        return TestResult(feature_path=str(path), feature_name=feature.name, scenarios=scenario_results, passed=all_passed, duration_ms=duration_ms)

    def generate_report(self, result: TestResult, format: str = "text", store: Optional[ArtifactStore] = None) -> str:
        store = store or self.store
        if format == "json":
            data = {"feature_path": result.feature_path, "feature_name": result.feature_name, "passed": result.passed, "duration_ms": result.duration_ms, "scenarios": [{"name": sr.scenario.name, "passed": sr.passed} for sr in result.scenarios]}
            out = json.dumps(data, ensure_ascii=False, indent=2)
            if store:
                store.write("bdd_report.json", data)
            return out
        lines = [f"Feature: {result.feature_name}", f"Passed: {result.passed}", f"Duration: {result.duration_ms} ms"]
        for sr in result.scenarios:
            lines.append(f"  Scenario: {sr.scenario.name} ({'PASS' if sr.passed else 'FAIL'})")
        return "\n".join(lines)


class BDDGenerator:
    def __init__(self, writer: EventWriter, run_id: str):
        self.writer = writer
        self.run_id = run_id

    def generate_from_spec(self, spec: Dict[str, Any], output_dir: Path) -> Path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        name = spec.get("name", "Unnamed")
        lines = [f"Feature: {name}", ""]
        for sc in spec.get("scenarios", []):
            lines.append(f"  Scenario: {sc.get('name', 'Unnamed')}")
            for st in sc.get("steps", []):
                lines.append(f"    {st.get('keyword', 'Given')} {st.get('text', '')}")
            lines.append("")
        safe_name = re.sub(r"[^\w\-]", "_", name).strip("_") or "feature"
        path = output_dir / f"{safe_name}.feature"
        path.write_text("\n".join(lines), encoding="utf-8")
        self.writer.emit("bdd.feature_generated", self.run_id, path=str(path), feature=name)
        return path
