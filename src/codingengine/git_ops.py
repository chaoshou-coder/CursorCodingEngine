"""Git 原子操作"""
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def find_git_root(start: Path) -> Optional[Path]:
    current = Path(start).resolve()
    for _ in range(10):
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _run_git(cwd: Path, *args: str) -> Tuple[int, str, str]:
    result = subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def has_uncommitted_changes(cwd: Path) -> bool:
    code, out, _ = _run_git(cwd, "status", "--porcelain")
    return code == 0 and bool(out.strip())


def atomic_commit(cwd: Path, task_id: str, message: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    if not has_uncommitted_changes(cwd):
        return True, None
    code, _, err = _run_git(cwd, "add", "-A")
    if code != 0:
        return False, f"git add failed: {err}"
    commit_msg = message or f"[codingengine] {task_id}"
    code, _, err = _run_git(cwd, "commit", "-m", commit_msg)
    if code != 0:
        return False, f"git commit failed: {err}"
    return True, None


def revert_last_commit(cwd: Path) -> Tuple[bool, Optional[str]]:
    code, _, err = _run_git(cwd, "revert", "--no-edit", "HEAD")
    return (True, None) if code == 0 else (False, f"git revert failed: {err}")


def rollback_task_commit(cwd: Path, task_id: str) -> Tuple[bool, Optional[str]]:
    code, out, _ = _run_git(cwd, "log", "-1", "--pretty=%B")
    if code != 0:
        return False, "Cannot read last commit message"
    if task_id in (out or ""):
        return revert_last_commit(cwd)
    code, out, _ = _run_git(cwd, "log", "--oneline", "-20")
    if code != 0:
        return False, "Cannot read git log"
    for line in (out or "").splitlines():
        if task_id in line:
            parts = line.split()
            if parts:
                code, _, err = _run_git(cwd, "revert", "--no-edit", parts[0])
                return (True, None) if code == 0 else (False, f"git revert failed: {err}")
    return False, f"No commit found for task_id: {task_id}"
