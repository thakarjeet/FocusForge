"""Core logic for FocusForge: a local-first, explainable productivity planner."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Iterable
import csv
import io
import json
import uuid


@dataclass
class Task:
    title: str
    category: str
    due_date: str
    estimated_minutes: int
    importance: int = 3
    energy: str = "Medium"
    completed: bool = False
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = uuid.uuid4().hex[:10]
        if not self.title.strip():
            raise ValueError("Task title cannot be empty.")
        if self.estimated_minutes <= 0:
            raise ValueError("Estimated minutes must be positive.")
        if not 1 <= self.importance <= 5:
            raise ValueError("Importance must be between 1 and 5.")
        if self.energy not in {"Low", "Medium", "High"}:
            raise ValueError("Energy must be Low, Medium, or High.")
        date.fromisoformat(self.due_date)


def _normalise(task) -> dict:
    if isinstance(task, Task):
        return asdict(task)
    return dict(task)


def priority_score(task, today: str | None = None) -> float:
    """Return an explainable 0–100 score using urgency, importance, effort and energy."""
    t = _normalise(task)
    today_date = date.fromisoformat(today) if today else date.today()
    due = date.fromisoformat(t["due_date"])
    days_left = (due - today_date).days

    # Urgency rises sharply as the deadline approaches and remains high when overdue.
    if days_left < 0:
        urgency = 40
    elif days_left == 0:
        urgency = 38
    elif days_left == 1:
        urgency = 32
    elif days_left <= 3:
        urgency = 25
    elif days_left <= 7:
        urgency = 17
    else:
        urgency = max(5, 14 - min(days_left, 30) * 0.3)

    importance = (int(t.get("importance", 3)) / 5) * 30
    # Short tasks receive a modest boost to make quick wins visible, without dominating urgency.
    minutes = max(1, int(t.get("estimated_minutes", 30)))
    quick_win = max(0, 12 - min(minutes, 120) / 10)
    energy_adjustment = {"Low": 5, "Medium": 2, "High": 0}.get(t.get("energy", "Medium"), 0)
    score = urgency + importance + quick_win + energy_adjustment
    return round(max(0, min(100, score)), 1)


def recommend_next_task(tasks: Iterable[dict | Task], today: str | None = None):
    """Choose the highest-priority incomplete task, or None if all are complete."""
    candidates = [_normalise(t) for t in tasks if not _normalise(t).get("completed", False)]
    if not candidates:
        return None
    return max(candidates, key=lambda t: (priority_score(t, today), -int(t.get("estimated_minutes", 30))))


def estimate_daily_load(tasks: Iterable[dict | Task], today: str | None = None,
                        available_minutes: int = 240) -> dict:
    """Estimate today's actionable workload and flag likely overload."""
    today_date = date.fromisoformat(today) if today else date.today()
    actionable = []
    for item in tasks:
        t = _normalise(item)
        if t.get("completed", False):
            continue
        due = date.fromisoformat(t["due_date"])
        if due <= today_date:
            actionable.append(t)
    total = sum(int(t["estimated_minutes"]) for t in actionable)
    blocks = (total + 49) // 50
    overloaded = total > available_minutes
    if total == 0:
        message = "No tasks are due or overdue today. Use the time for a small step toward a longer-term goal."
    elif overloaded:
        message = f"{total} minutes of work are due or overdue; consider moving some tasks or splitting them into smaller steps."
    else:
        message = f"{total} minutes of work are due or overdue. Leave a little buffer for breaks and surprises."
    return {"total_minutes": total, "focus_blocks": blocks, "overloaded": overloaded, "message": message}


def productivity_summary(tasks: Iterable[dict | Task]) -> dict:
    items = [_normalise(t) for t in tasks]
    total = len(items)
    completed = sum(bool(t.get("completed", False)) for t in items)
    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "completion_rate": (completed / total * 100) if total else 0.0,
    }


def create_task(tasks: list[dict], title: str, category: str, due_date: str,
                estimated_minutes: int, importance: int, energy: str) -> list[dict]:
    task = Task(title, category, due_date, int(estimated_minutes), int(importance), energy)
    return [*tasks, asdict(task)]


def complete_task(tasks: list[dict], task_id: str) -> list[dict]:
    return [dict(t, completed=True) if t["id"] == task_id else t for t in tasks]


def delete_task(tasks: list[dict], task_id: str) -> list[dict]:
    return [t for t in tasks if t["id"] != task_id]


def load_tasks(path: str | Path = "data/tasks.json") -> list[dict]:
    file = Path(path)
    if not file.exists():
        return []
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(path: str | Path, tasks: list[dict]) -> None:
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")


def export_tasks_csv(tasks: Iterable[dict | Task]) -> str:
    rows = [_normalise(t) for t in tasks]
    output = io.StringIO()
    fields = ["id", "title", "category", "due_date", "estimated_minutes", "importance", "energy", "completed"]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
