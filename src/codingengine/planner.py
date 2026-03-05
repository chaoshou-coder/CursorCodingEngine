"""Planner - 任务规划"""
import re
from dataclasses import dataclass
from typing import List, Dict

from .config import get_config


@dataclass
class AtomicTask:
    id: str
    description: str
    estimated_context: int
    dependencies: List[str]
    parallel_group: int
    assigned_model: str


class Planner:
    def __init__(self, config=None):
        self.config = config or get_config()
        _, self.planner_config = self.config.get_model("planner")
        self.dev_model_name, self.dev_config = self.config.get_model("dev")
        self.safe_limit = self.dev_config.context_limit
        self.task_groups = self.config.parallel.get("task_groups", 3)

    def plan_from_architecture(self, architecture_doc: str) -> List[AtomicTask]:
        modules = [l.strip() for l in architecture_doc.split("\n") if l.strip() and not l.strip().startswith("#")]
        tasks = []
        for i, module in enumerate(modules):
            estimated = min(len(module) // 4, self.dev_config.context_limit)
            deps = []
            for t in tasks:
                kw = re.split(r"[^a-zA-Z0-9_]+", t.description.lower())
                if any(k in module.lower() for k in kw if len(k) > 2):
                    deps.append(t.id)
            group = max((t.parallel_group for t in tasks if t.id in deps), default=0) + 1 if deps else 0
            if estimated > self.safe_limit:
                lines = module.split("\n")
                lines_per = max(1, self.safe_limit // (len(module) // 4 // len(lines)) if lines else 1)
                for j in range(0, len(lines), lines_per):
                    chunk = "\n".join(lines[j:j + lines_per])
                    tasks.append(AtomicTask(
                        id=f"task_{i}_{j//lines_per}",
                        description=chunk,
                        estimated_context=self.safe_limit // 2,
                        dependencies=[tasks[-1].id] if tasks else [],
                        parallel_group=(j // lines_per) % self.task_groups,
                        assigned_model=self.dev_model_name,
                    ))
            else:
                tasks.append(AtomicTask(
                    id=f"task_{i}",
                    description=module,
                    estimated_context=estimated,
                    dependencies=deps,
                    parallel_group=group,
                    assigned_model=self.dev_model_name,
                ))
        return tasks

    def export_plan(self, tasks: List[AtomicTask]) -> Dict:
        groups = sorted(set(t.parallel_group for t in tasks))
        return {
            "dev_model": self.dev_model_name,
            "context_limit": self.safe_limit,
            "atomic_commit": True,
            "rollback_strategy": "git_revert",
            "decoupled": True,
            "total_tasks": len(tasks),
            "parallel_groups": [[t.id for t in tasks if t.parallel_group == g] for g in groups],
            "dag_edges": {t.id: t.dependencies for t in tasks if t.dependencies},
            "tasks": [{"id": t.id, "description": t.description[:100]+"..." if len(t.description) > 100 else t.description, "dependencies": t.dependencies, "parallel_group": t.parallel_group, "assigned_model": t.assigned_model} for t in tasks],
        }
