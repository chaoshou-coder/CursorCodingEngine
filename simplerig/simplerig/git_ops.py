"""
Git 原子操作

提供：
- 原子提交（task_id 标记）
- 失败回滚（git revert）
- 任务开始前 stash 保护现场（可选）
"""
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def find_git_root(start: Path) -> Optional[Path]:
    """从 start 向上查找 git 仓库根目录"""
    current = Path(start).resolve()
    for _ in range(10):  # 最多向上 10 层
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _run_git(cwd: Path, *args: str) -> Tuple[int, str, str]:
    """执行 git 命令"""
    result = subprocess.run(
        ["git"] + list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def stash_save(cwd: Path, message: str = "simplerig-stash") -> bool:
    """
    保护现场：git stash
    返回是否成功
    """
    code, out, err = _run_git(cwd, "stash", "push", "-m", message)
    # 无变更时 stash 可能返回非 0，视为成功
    if code != 0 and "No local changes" in err:
        return True
    return code == 0


def stash_pop(cwd: Path) -> bool:
    """恢复 stash"""
    code, _, _ = _run_git(cwd, "stash", "pop")
    return code == 0


def has_uncommitted_changes(cwd: Path) -> bool:
    """检查是否有未提交变更"""
    code, out, _ = _run_git(cwd, "status", "--porcelain")
    return code == 0 and bool(out.strip())


def atomic_commit(
    cwd: Path,
    task_id: str,
    message: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """
    原子提交：git add -A && git commit

    Args:
        cwd: 仓库根目录
        task_id: 任务 ID，会写入 commit message
        message: 可选自定义 message，默认用 task_id

    Returns:
        (成功与否, 错误信息)
    """
    if not has_uncommitted_changes(cwd):
        return True, None

    code, _, err = _run_git(cwd, "add", "-A")
    if code != 0:
        return False, f"git add failed: {err}"

    commit_msg = message or f"[simplerig] {task_id}"
    code, _, err = _run_git(cwd, "commit", "-m", commit_msg)
    if code != 0:
        return False, f"git commit failed: {err}"

    return True, None


def get_last_commit_hash(cwd: Path) -> Optional[str]:
    """获取最近一次 commit 的 hash"""
    code, out, _ = _run_git(cwd, "rev-parse", "HEAD")
    if code != 0:
        return None
    return out.strip() or None


def revert_last_commit(cwd: Path) -> Tuple[bool, Optional[str]]:
    """
    回滚最近一次 commit：git revert --no-edit HEAD

    使用 revert 而非 reset，以保留历史，便于协作。
    """
    code, _, err = _run_git(cwd, "revert", "--no-edit", "HEAD")
    if code != 0:
        return False, f"git revert failed: {err}"
    return True, None


def rollback_task_commit(cwd: Path, task_id: str) -> Tuple[bool, Optional[str]]:
    """
    回滚指定 task 的 commit

    若最近一次 commit message 包含 task_id，则 revert 该 commit。
    否则尝试查找包含 task_id 的 commit 并 revert。
    """
    code, out, _ = _run_git(cwd, "log", "-1", "--pretty=%B")
    if code != 0:
        return False, "Cannot read last commit message"

    if task_id in (out or ""):
        return revert_last_commit(cwd)

    # 查找包含 task_id 的 commit
    code, out, _ = _run_git(cwd, "log", "--oneline", "-20")
    if code != 0:
        return False, "Cannot read git log"

    for line in (out or "").splitlines():
        if task_id in line:
            # 格式: "abc1234 [simplerig] task_0"
            parts = line.split()
            if parts:
                commit_hash = parts[0]
                code, _, err = _run_git(cwd, "revert", "--no-edit", commit_hash)
                if code != 0:
                    return False, f"git revert {commit_hash} failed: {err}"
                return True, None

    return False, f"No commit found for task_id: {task_id}"
