import json
import tempfile
import unittest
from pathlib import Path

from focusforge import (
    Task, priority_score, recommend_next_task, estimate_daily_load,
    productivity_summary, create_task, complete_task, delete_task, load_tasks, save_tasks,
    export_tasks_csv,
)


def sample(title="Read chapter", due="2026-10-22", minutes=30, importance=3, energy="Medium", completed=False):
    return {
        "id": title.lower().replace(" ", "-"), "title": title, "category": "Study",
        "due_date": due, "estimated_minutes": minutes, "importance": importance,
        "energy": energy, "completed": completed,
    }


class FocusForgeTests(unittest.TestCase):
    def test_task_validation_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            Task(" ", "Study", "2026-10-22", 30)

    def test_task_validation_rejects_invalid_importance(self):
        with self.assertRaises(ValueError):
            Task("Task", "Study", "2026-10-22", 30, importance=7)

    def test_due_today_scores_higher_than_far_deadline(self):
        today = "2026-10-20"
        due_today = sample("Urgent", due=today)
        later = sample("Later", due="2026-11-20")
        self.assertGreater(priority_score(due_today, today), priority_score(later, today))

    def test_recommendation_skips_completed_tasks(self):
        tasks = [sample("Done", due="2026-10-20", completed=True), sample("Open", due="2026-10-25")]
        self.assertEqual(recommend_next_task(tasks, "2026-10-20")["title"], "Open")

    def test_recommendation_returns_none_when_all_complete(self):
        self.assertIsNone(recommend_next_task([sample(completed=True)], "2026-10-20"))

    def test_daily_load_only_counts_due_and_overdue(self):
        tasks = [sample("Today", due="2026-10-20", minutes=60),
                 sample("Later", due="2026-10-24", minutes=45),
                 sample("Overdue", due="2026-10-19", minutes=30)]
        result = estimate_daily_load(tasks, today="2026-10-20")
        self.assertEqual(result["total_minutes"], 90)
        self.assertFalse(result["overloaded"])

    def test_daily_load_flags_overload(self):
        result = estimate_daily_load([sample(due="2026-10-20", minutes=300)], today="2026-10-20", available_minutes=240)
        self.assertTrue(result["overloaded"])

    def test_summary_empty_and_nonempty(self):
        self.assertEqual(productivity_summary([])["completion_rate"], 0)
        summary = productivity_summary([sample(completed=True), sample("Open")])
        self.assertEqual(summary["completion_rate"], 50)

    def test_crud_helpers(self):
        tasks = create_task([], "Build portfolio", "Project", "2026-10-30", 60, 5, "High")
        task_id = tasks[0]["id"]
        self.assertTrue(complete_task(tasks, task_id)[0]["completed"])
        self.assertEqual(delete_task(tasks, task_id), [])

    def test_json_roundtrip_and_csv_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tasks.json"
            tasks = [sample()]
            save_tasks(path, tasks)
            self.assertEqual(load_tasks(path), tasks)
            self.assertIn("Read chapter", export_tasks_csv(tasks))
            self.assertTrue(json.loads(path.read_text()))


if __name__ == "__main__":
    unittest.main()
