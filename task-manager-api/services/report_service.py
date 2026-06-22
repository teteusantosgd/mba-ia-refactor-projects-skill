from datetime import timedelta

from shared.clock import utc_now
from shared.constants import HIGH_PRIORITY_THRESHOLD, RECENT_ACTIVITY_DAYS
from shared.errors import ServiceError


class ReportService:
    """Agregações e relatórios. Calcula tudo a partir de uma única leitura, evitando N+1."""

    def __init__(self, task_repository, user_repository, category_repository):
        self.tasks = task_repository
        self.users = user_repository
        self.categories = category_repository

    def summary(self):
        all_tasks = self.tasks.get_all_with_relations()
        users = self.users.get_all()

        status_counts = {"pending": 0, "in_progress": 0, "done": 0, "cancelled": 0}
        priority_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        overdue_list = []
        recent_threshold = utc_now() - timedelta(days=RECENT_ACTIVITY_DAYS)
        recent_created = 0
        recent_done = 0
        tasks_by_user = {}

        for task in all_tasks:
            if task.status in status_counts:
                status_counts[task.status] += 1
            if task.priority in priority_counts:
                priority_counts[task.priority] += 1
            if task.is_overdue():
                overdue_list.append(
                    {
                        "id": task.id,
                        "title": task.title,
                        "due_date": str(task.due_date),
                        "days_overdue": (utc_now() - task.due_date).days,
                    }
                )
            if task.created_at and task.created_at >= recent_threshold:
                recent_created += 1
            if task.status == "done" and task.updated_at and task.updated_at >= recent_threshold:
                recent_done += 1
            tasks_by_user.setdefault(task.user_id, []).append(task)

        user_stats = []
        for user in users:
            user_tasks = tasks_by_user.get(user.id, [])
            total = len(user_tasks)
            completed = sum(1 for task in user_tasks if task.status == "done")
            user_stats.append(
                {
                    "user_id": user.id,
                    "user_name": user.name,
                    "total_tasks": total,
                    "completed_tasks": completed,
                    "completion_rate": round((completed / total) * 100, 2) if total > 0 else 0,
                }
            )

        return {
            "generated_at": str(utc_now()),
            "overview": {
                "total_tasks": len(all_tasks),
                "total_users": len(users),
                "total_categories": self.categories.count(),
            },
            "tasks_by_status": {
                "pending": status_counts["pending"],
                "in_progress": status_counts["in_progress"],
                "done": status_counts["done"],
                "cancelled": status_counts["cancelled"],
            },
            "tasks_by_priority": {
                "critical": priority_counts[1],
                "high": priority_counts[2],
                "medium": priority_counts[3],
                "low": priority_counts[4],
                "minimal": priority_counts[5],
            },
            "overdue": {
                "count": len(overdue_list),
                "tasks": overdue_list,
            },
            "recent_activity": {
                "tasks_created_last_7_days": recent_created,
                "tasks_completed_last_7_days": recent_done,
            },
            "user_productivity": user_stats,
        }

    def user_report(self, user_id):
        user = self.users.get_by_id(user_id)
        if not user:
            raise ServiceError("Usuário não encontrado", 404)

        tasks = self.tasks.get_by_user(user_id)
        counters = {"done": 0, "pending": 0, "in_progress": 0, "cancelled": 0}
        overdue = 0
        high_priority = 0

        for task in tasks:
            if task.status in counters:
                counters[task.status] += 1
            if task.priority <= HIGH_PRIORITY_THRESHOLD:
                high_priority += 1
            if task.is_overdue():
                overdue += 1

        total = len(tasks)
        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            },
            "statistics": {
                "total_tasks": total,
                "done": counters["done"],
                "pending": counters["pending"],
                "in_progress": counters["in_progress"],
                "cancelled": counters["cancelled"],
                "overdue": overdue,
                "high_priority": high_priority,
                "completion_rate": round((counters["done"] / total) * 100, 2) if total > 0 else 0,
            },
        }
