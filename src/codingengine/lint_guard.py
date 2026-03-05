"""Lint Guard - 代码风格检查"""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .config import get_config
from .events import EventWriter


@dataclass
class LintIssue:
    file: str
    line: int
    code: str
    message: str
    fixable: bool


@dataclass
class LintResult:
    success: bool
    issues: List[LintIssue]
    fixed_count: int
    command: str
    stdout: str
    stderr: str


@dataclass
class TestRunResult:
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    skipped: bool
    test_count: int
    passed_count: int
    failed_count: int


class LintGuard:
    def __init__(
        self,
        project_root: str = ".",
        config=None,
        writer: Optional[EventWriter] = None,
        run_id: str = "",
    ):
        self.project_root = Path(project_root)
        self.config = config or get_config()
        self.writer = writer
        self.run_id = run_id
        self.linter = self.config.tools.get("linter", "ruff")
        self.formatter = self.config.tools.get("formatter", "black")
        self.test_runner = self.config.tools.get("test_runner", "pytest")
        self.linter_args = self.config.tools.get("linter_args", ["check", "--fix"])
        self.formatter_args = self.config.tools.get("formatter_args", [])
        self.test_runner_args = self.config.tools.get("test_runner_args", ["-v"])
        self.source_dirs = self.config.project.get("source_dirs", ["src"])
        self.test_dirs = self.config.project.get("test_dirs", ["tests"])

    def _emit(self, event_type: str, **data):
        if self.writer:
            self.writer.emit(event_type, self.run_id, **data)

    def _get_targets(self) -> List[str]:
        targets = []
        for d in self.source_dirs + self.test_dirs:
            if (self.project_root / d).exists():
                targets.append(d)
        return targets or ["."]

    def _run_tool(self, tool: str, args: List[str]) -> Dict:
        cmd = [tool] + args
        timeout = self.config.timeouts.get("tool", 300)
        try:
            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            issues = (
                self._parse_ruff(r.stdout + r.stderr) if tool == self.linter else []
            )
            fixed = 0
            if "Fixed" in (r.stderr or ""):
                for line in (r.stderr or "").split("\n"):
                    if "Fixed" in line:
                        try:
                            fixed = int(line.split()[1])
                        except Exception:
                            pass
                        break
            return {
                "issues": issues,
                "fixed": fixed,
                "stdout": r.stdout or "",
                "stderr": r.stderr or "",
            }
        except FileNotFoundError:
            return {
                "issues": [
                    LintIssue("N/A", 0, "NOT_FOUND", f"{tool} not found", False)
                ],
                "fixed": 0,
                "stdout": "",
                "stderr": f"{tool} not found",
            }
        except subprocess.TimeoutExpired:
            return {
                "issues": [LintIssue("N/A", 0, "TIMEOUT", f"{tool} timed out", False)],
                "fixed": 0,
                "stdout": "",
                "stderr": "Timeout",
            }

    def _parse_ruff(self, output: str) -> List[LintIssue]:
        issues = []
        for line in output.split("\n"):
            if ":" not in line:
                continue
            parts = line.split(":", 3)
            if len(parts) < 4:
                continue
            try:
                issues.append(
                    LintIssue(
                        file=parts[0],
                        line=int(parts[1]),
                        code=parts[3].strip().split()[0] if parts[3].strip() else "",
                        message=(
                            " ".join(parts[3].strip().split()[1:])
                            if parts[3].strip()
                            else ""
                        ),
                        fixable=(
                            parts[3]
                            .strip()
                            .split()[0]
                            .startswith(("F4", "F5", "I", "UP"))
                            if parts[3].strip()
                            else False
                        ),
                    )
                )
            except Exception:
                pass
        return issues

    def check_and_fix(self, files: List[str] = None) -> LintResult:
        target = files or self._get_targets()
        r1 = self._run_tool(self.linter, self.linter_args + target)
        r2 = self._run_tool(self.formatter, self.formatter_args + target)
        r3 = self._run_tool(self.linter, ["check"] + target)
        success = len(r3["issues"]) == 0
        self._emit(
            "lint.passed" if success else "lint.failed",
            fixed_count=r1["fixed"] + r2.get("fixed", 0),
            issues_count=len(r3["issues"]),
        )
        return LintResult(
            success=success,
            issues=r3["issues"],
            fixed_count=r1["fixed"],
            command=f"{self.linter}+{self.formatter}",
            stdout=r1["stdout"] + r2["stdout"],
            stderr=r1["stderr"] + r2["stderr"],
        )

    def run_tests(self) -> TestRunResult:
        targets = []
        for d in self.test_dirs:
            if (self.project_root / d).exists():
                targets.append(d)
        targets = targets or ["."]
        cmd = [self.test_runner] + self.test_runner_args + targets
        timeout = self.config.get_timeout("tool", 300)
        try:
            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return TestRunResult(
                success=False,
                exit_code=1,
                stdout="",
                stderr=str(e),
                skipped=False,
                test_count=0,
                passed_count=0,
                failed_count=0,
            )
        out = (r.stdout or "") + (r.stderr or "")
        passed = failed = 0
        for line in out.splitlines():
            if "passed" in line:
                m = re.search(r"(\d+)\s+passed", line)
                if m:
                    passed = int(m.group(1))
            if "failed" in line:
                m = re.search(r"(\d+)\s+failed", line)
                if m:
                    failed = int(m.group(1))
        skipped = r.returncode == 5
        success = r.returncode in (0, 5)
        return TestRunResult(
            success=success,
            exit_code=r.returncode,
            stdout=r.stdout or "",
            stderr=r.stderr or "",
            skipped=skipped,
            test_count=passed + failed,
            passed_count=passed,
            failed_count=failed,
        )

    def full_check(self) -> Dict:
        lint_result = self.check_and_fix()
        test_result = self.run_tests()
        return {
            "lint": lint_result,
            "tests": test_result,
            "overall_success": lint_result.success and test_result.success,
        }
