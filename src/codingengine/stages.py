"""内置阶段处理器"""
from pathlib import Path
from typing import List

from .runner import Stage, StageStatus, StageResult, StageContext
from .lint_guard import LintGuard
from .git_ops import atomic_commit, has_uncommitted_changes, rollback_task_commit


def plan_handler(ctx: StageContext) -> StageResult:
    plan = {
        "requirement": ctx.requirement,
        "stages": ["plan", "develop", "verify", "integrate"],
        "atomic_commit": True,
        "rollback_strategy": "git_revert",
        "decoupled": True,
        "tasks": [
            {"id": "task_analyze", "name": "需求分析", "description": f"分析需求: {ctx.requirement}", "parallel_group": 0},
            {"id": "task_design", "name": "设计方案", "description": "设计实现方案", "dependencies": ["task_analyze"], "parallel_group": 1},
            {"id": "task_implement", "name": "代码实现", "description": "实现代码", "dependencies": ["task_design"], "parallel_group": 2},
        ],
        "stub": True,
    }
    ref = ctx.store.write("plan.json", plan)
    ctx.writer.emit("artifact.written", ctx.run_id, artifact=ref.to_dict())
    ctx.state.artifacts["plan.json"] = ref
    return StageResult(status=StageStatus.COMPLETED, outputs=[ref])


def develop_handler(ctx: StageContext) -> StageResult:
    plan = None
    if "plan.json" in ctx.inputs:
        try:
            plan = ctx.store.read_json("plan.json")
        except Exception:
            pass
    tdd_mode = ctx.options.get("tdd", False)
    project_root = ctx.project_root
    tdd_ran = False
    tdd_success = True
    if tdd_mode and plan:
        tdd_test = plan.get("tdd_test_file") or (plan.get("tasks") and next((t.get("test_file") for t in plan["tasks"] if t.get("test_file")), None))
        tdd_impl = plan.get("tdd_impl_file") or (plan.get("tasks") and next((t.get("impl_file") for t in plan["tasks"] if t.get("impl_file")), None))
        if tdd_test and tdd_impl:
            try:
                from .tdd import TDDRunner
                test_path = project_root / tdd_test if not Path(tdd_test).is_absolute() else Path(tdd_test)
                impl_path = project_root / tdd_impl if not Path(tdd_impl).is_absolute() else Path(tdd_impl)
                runner = TDDRunner(ctx.config, ctx.writer, ctx.run_id)
                result = runner.run_cycle(test_path, impl_path, lambda: None, project_root=project_root)
                tdd_ran, tdd_success = True, result.success
            except ImportError:
                pass
    changes = {"requirement": ctx.requirement, "plan": plan, "tdd_mode": tdd_mode, "tdd_ran": tdd_ran, "tdd_success": tdd_success if tdd_ran else None, "changes": [{"file": "stub_file.py", "action": "create", "content": "# Stub\n"}], "stub": not tdd_ran}
    ref = ctx.store.write("code_changes.json", changes)
    ctx.writer.emit("artifact.written", ctx.run_id, artifact=ref.to_dict())
    ctx.state.artifacts["code_changes.json"] = ref
    if tdd_ran and not tdd_success:
        if plan and plan.get("rollback_strategy") == "git_revert":
            rollback_task_commit(project_root, f"develop_{ctx.run_id}")
        return StageResult(status=StageStatus.FAILED, outputs=[ref], error="TDD cycle failed")
    if plan and plan.get("atomic_commit") and has_uncommitted_changes(project_root):
        atomic_commit(project_root, f"develop_{ctx.run_id}")
    return StageResult(status=StageStatus.COMPLETED, outputs=[ref])


def verify_handler(ctx: StageContext) -> StageResult:
    guard = LintGuard(project_root=str(ctx.project_root), config=ctx.config, writer=ctx.writer, run_id=ctx.run_id)
    check = guard.full_check()
    lint_result, test_result = check["lint"], check["tests"]
    lint_success = lint_result.success
    lint_report = lint_result.stdout or lint_result.stderr or "Lint done"
    tests_success = test_result.success
    tests_report = test_result.stdout or test_result.stderr or "Tests done"
    bdd_result = None
    feature_files = list(Path(ctx.store.artifacts_dir).glob("*.feature")) if hasattr(ctx.store, "artifacts_dir") and ctx.store.artifacts_dir.exists() else []
    if (ctx.options.get("bdd") or feature_files) and feature_files:
        try:
            from .bdd import BDDRunner
            runner = BDDRunner(ctx.config, ctx.writer, ctx.run_id, store=ctx.store)
            for fp in feature_files:
                r = runner.run_feature(fp)
                bdd_result = {"feature": r.feature_name, "passed": r.passed, "duration_ms": r.duration_ms}
                if not r.passed:
                    tests_success = False
        except ImportError:
            pass
    verify_result = {"requirement": ctx.requirement, "lint": {"success": lint_success, "report": lint_report}, "tests": {"success": tests_success, "report": tests_report}, "bdd": bdd_result, "overall_success": lint_success and tests_success}
    ref = ctx.store.write("verify_result.json", verify_result)
    ctx.writer.emit("artifact.written", ctx.run_id, artifact=ref.to_dict())
    ctx.state.artifacts["verify_result.json"] = ref
    if not verify_result["overall_success"]:
        return StageResult(status=StageStatus.FAILED, outputs=[ref], error=f"Verify failed: lint={lint_success}, tests={tests_success}")
    return StageResult(status=StageStatus.COMPLETED, outputs=[ref])


def integrate_handler(ctx: StageContext) -> StageResult:
    verify_result = None
    if "verify_result.json" in ctx.inputs:
        try:
            verify_result = ctx.store.read_json("verify_result.json")
        except Exception:
            pass
    if verify_result and not verify_result.get("overall_success", False):
        return StageResult(status=StageStatus.FAILED, error="Cannot integrate: verification failed")
    ref = ctx.store.write("integration_result.json", {"requirement": ctx.requirement, "verify_result": verify_result, "integration": {"applied_changes": [], "commit_hash": None}, "stub": True})
    ctx.writer.emit("artifact.written", ctx.run_id, artifact=ref.to_dict())
    ctx.state.artifacts["integration_result.json"] = ref
    return StageResult(status=StageStatus.COMPLETED, outputs=[ref])


def get_default_stages() -> List[Stage]:
    return [
        Stage("plan", handler=plan_handler, outputs=["plan.json"]),
        Stage("develop", handler=develop_handler, depends_on=["plan"], required_inputs=["plan.json"], outputs=["code_changes.json"]),
        Stage("verify", handler=verify_handler, depends_on=["develop"], required_inputs=["code_changes.json"], outputs=["verify_result.json"]),
        Stage("integrate", handler=integrate_handler, depends_on=["verify"], required_inputs=["verify_result.json"], outputs=["integration_result.json"]),
    ]


def get_enhanced_stages() -> List[Stage]:
    return get_default_stages()
