"""TDD Runner - 红绿循环"""
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from .config import get_config
from .events import EventWriter


@dataclass
class TDDResult:
    success: bool
    red_passed: bool
    green_passed: bool
    retries: int = 0
    red_output: str = ""
    green_output: str = ""
    error: Optional[str] = None


class TDDRunner:
    def __init__(self, config, writer: EventWriter, run_id: str):
        self.config = config
        self.writer = writer
        self.run_id = run_id
        self.red_timeout = config.get_timeout("tdd_red_phase", 30)
        self.green_timeout = config.get_timeout("tdd_green_phase", 30)
        self.max_retries = config.get_timeout("tdd_max_retries", 3)
        self.test_runner = config.tools.get("test_runner", "pytest")
        self.test_args = config.tools.get("test_runner_args", ["-v"])
        if isinstance(self.test_args, str):
            self.test_args = [self.test_args]

    def run_cycle(self, test_file: Path, impl_file: Path, dev_func: Callable[[], None], project_root: Optional[Path] = None) -> TDDResult:
        cwd = Path(project_root) if project_root else test_file.parent
        self.writer.emit("tdd.red_started", self.run_id, test_file=str(test_file))
        red_ok, red_output = self._run(test_file, cwd)
        if not red_ok:
            self.writer.emit("tdd.red_failed", self.run_id, test_file=str(test_file), output=red_output[:2000])
            return TDDResult(success=False, red_passed=False, green_passed=False, red_output=red_output, error="Red phase failed")
        self.writer.emit("tdd.red_passed", self.run_id, test_file=str(test_file))
        retries = 0
        green_output = ""
        while retries <= self.max_retries:
            dev_func()
            self.writer.emit("tdd.green_started", self.run_id, test_file=str(test_file), retry=retries)
            green_ok, green_output = self._run(test_file, cwd, expect_pass=True)
            if green_ok:
                self.writer.emit("tdd.green_passed", self.run_id, test_file=str(test_file), retries=retries)
                return TDDResult(success=True, red_passed=True, green_passed=True, retries=retries, red_output=red_output, green_output=green_output)
            self.writer.emit("tdd.green_failed", self.run_id, test_file=str(test_file), retry=retries, output=green_output[:2000])
            retries += 1
        self.writer.emit("tdd.cycle_failed", self.run_id, test_file=str(test_file), retries=retries, output=green_output[:2000])
        return TDDResult(success=False, red_passed=True, green_passed=False, retries=retries, red_output=red_output, green_output=green_output, error=f"Green failed after {retries} retries")

    def _run(self, test_file: Path, cwd: Path, expect_pass: bool = False) -> tuple[bool, str]:
        cmd = [self.test_runner] + self.test_args + [str(test_file)]
        timeout = self.green_timeout if expect_pass else self.red_timeout
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout)
            out = (r.stdout or "") + (r.stderr or "")
            return (r.returncode == 0 if expect_pass else r.returncode != 0, out)
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return (False, str(e))
