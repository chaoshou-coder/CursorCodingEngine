"""CodingEngine CLI"""

import argparse
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def get_runs_dir() -> Path:
    """数据目录 ~/.codingengine/runs，不污染项目"""
    base = (
        Path(os.environ.get("CODINGENGINE_DATA", "~/.codingengine"))
        .expanduser()
        .resolve()
    )
    return base / "runs"


def generate_run_id() -> str:
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def get_latest_run_id() -> Optional[str]:
    runs_dir = get_runs_dir()
    if not runs_dir.exists():
        return None
    runs = sorted(
        [d for d in runs_dir.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )
    return runs[0].name if runs else None


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codingengine",
        description="CodingEngine - 编排+执行+迭代，不污染项目目录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", "-V", action="version", version="%(prog)s 0.1.0")
    sub = parser.add_subparsers(dest="command")
    init_p = sub.add_parser("init", help="初始化新 run")
    init_p.add_argument("requirement", nargs="?", help="需求描述")
    emit_p = sub.add_parser("emit", help="记录事件")
    emit_p.add_argument("event", help="事件类型")
    emit_p.add_argument("--run-id", required=True, help="Run ID")
    emit_p.add_argument("--stage", help="阶段名")
    emit_p.add_argument("--data", help="JSON 数据")
    emit_p.add_argument("--prompt-tokens", type=int)
    emit_p.add_argument("--completion-tokens", type=int)
    run_p = sub.add_parser("run", help="运行工作流")
    run_p.add_argument("requirement", nargs="?", help="需求描述")
    run_p.add_argument("--resume", nargs="?", const="latest", help="恢复执行")
    run_p.add_argument(
        "--from-stage", choices=["plan", "develop", "verify", "integrate"]
    )
    run_p.add_argument("--fail-fast", action="store_true")
    run_p.add_argument("--tdd", action="store_true")
    run_p.add_argument("--bdd", action="store_true")
    status_p = sub.add_parser("status", help="查看状态")
    status_p.add_argument("--run-id", help="Run ID")
    status_p.add_argument("--json", action="store_true")
    tail_p = sub.add_parser("tail", help="查看事件流")
    tail_p.add_argument("--run-id", help="Run ID")
    tail_p.add_argument("--lines", "-n", type=int, default=20)
    list_p = sub.add_parser("list", help="列出历史")
    list_p.add_argument("--limit", type=int, default=10)
    stats_p = sub.add_parser("stats", help="统计")
    stats_p.add_argument("--run-id", help="Run ID")
    return parser


def cmd_init(args) -> int:
    if not args.requirement:
        print("错误：请提供需求描述", file=sys.stderr)
        return 1
    run_id = generate_run_id()
    run_dir = get_runs_dir() / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "artifacts").mkdir(exist_ok=True)
    (run_dir / "locks").mkdir(exist_ok=True)
    from .events import EventWriter

    EventWriter(run_dir).emit("run.started", run_id, requirement=args.requirement)
    print(f"run_id={run_id}")
    return 0


def cmd_emit(args) -> int:
    run_dir = get_runs_dir() / args.run_id
    if not run_dir.exists():
        print(f"错误：run_id '{args.run_id}' 不存在", file=sys.stderr)
        return 1
    data = {}
    if args.data:
        import json

        data = json.loads(args.data)
    if args.stage:
        data["stage"] = args.stage
    if args.prompt_tokens is not None or args.completion_tokens is not None:
        data["token_usage"] = {
            "prompt_tokens": args.prompt_tokens or 0,
            "completion_tokens": args.completion_tokens or 0,
        }
    from .events import EventWriter

    EventWriter(run_dir).emit(args.event, args.run_id, **data)
    print(f"Event recorded: {args.event}")
    return 0


def cmd_run(args) -> int:
    from .runner import StageMachine
    from .stages import get_default_stages, get_enhanced_stages
    from .config import get_config
    from .stats import collect_stats

    config = get_config()
    if args.resume:
        run_id = get_latest_run_id() if args.resume == "latest" else args.resume
        if not run_id:
            print("错误：没有可恢复的 run", file=sys.stderr)
            return 1
    else:
        if not args.requirement:
            print("错误：请提供需求描述或 --resume", file=sys.stderr)
            return 1
        run_id = generate_run_id()
    run_dir = get_runs_dir() / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "artifacts").mkdir(exist_ok=True)
    (run_dir / "locks").mkdir(exist_ok=True)
    print(f"run_id={run_id}")
    print(f"数据目录: {run_dir} (项目目录无新增文件)")
    stages = get_enhanced_stages() if (args.tdd or args.bdd) else get_default_stages()
    try:
        machine = StageMachine(
            run_dir, stages=stages, fail_fast=args.fail_fast, project_root=Path.cwd()
        )
        state = machine.run(
            requirement=args.requirement or "",
            resume=bool(args.resume),
            from_stage=args.from_stage,
            tdd=args.tdd,
            bdd=args.bdd,
        )
        print(f"\n状态: {state.status}")
        print(collect_stats(run_dir).summary())
        return 0 if state.status == "completed" else 1
    except Exception as e:
        print(f"执行失败: {e}", file=sys.stderr)
        return 1


def cmd_status(args) -> int:
    run_id = args.run_id or get_latest_run_id()
    if not run_id:
        print("未找到运行记录", file=sys.stderr)
        return 1
    run_dir = get_runs_dir() / run_id
    if not run_dir.exists():
        print("运行不存在", file=sys.stderr)
        return 1
    info = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "events_exists": (run_dir / "events.jsonl").exists(),
    }
    if args.json:
        import json

        print(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        print(f"Run ID: {info['run_id']}")
        print(f"目录: {info['run_dir']}")
    return 0


def cmd_tail(args) -> int:
    run_id = args.run_id or get_latest_run_id()
    if not run_id:
        print("未找到运行记录", file=sys.stderr)
        return 1
    events_file = get_runs_dir() / run_id / "events.jsonl"
    if not events_file.exists():
        print("事件日志不存在", file=sys.stderr)
        return 1
    lines = events_file.read_text(encoding="utf-8").strip().split("\n")
    for line in lines[-args.lines :]:
        print(line)
    return 0


def cmd_list(args) -> int:
    runs_dir = get_runs_dir()
    if not runs_dir.exists():
        print("没有历史运行")
        return 0
    runs = sorted(
        [d for d in runs_dir.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )[: args.limit]
    for d in runs:
        mtime = datetime.fromtimestamp(d.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {d.name}  {mtime}")
    return 0


def cmd_stats(args) -> int:
    run_id = args.run_id or get_latest_run_id()
    if not run_id:
        print("未找到运行记录", file=sys.stderr)
        return 1
    run_dir = get_runs_dir() / run_id
    if not run_dir.exists():
        print("运行不存在", file=sys.stderr)
        return 1
    from .stats import collect_stats

    print(collect_stats(run_dir).summary())
    return 0


def main(argv: list = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    cmds = {
        "init": cmd_init,
        "emit": cmd_emit,
        "run": cmd_run,
        "status": cmd_status,
        "tail": cmd_tail,
        "list": cmd_list,
        "stats": cmd_stats,
    }
    handler = cmds.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            print("\n中断")
            return 130
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            return 1
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
