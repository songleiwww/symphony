from typing import List, Optional, Dict, Any
from datetime import datetime
from .task import Task
from .storage import Storage


class TaskManager:
    """任务管理器，处理所有任务的核心业务逻辑"""

    def __init__(self, storage: Storage = None):
        self.storage = storage or Storage()
        self.tasks: List[Task] = []
        self.next_id = 1
        self.load()

    def load(self) -> None:
        """从存储加载任务"""
        data = self.storage.load()
        self.next_id = data.get("next_id", 1)
        task_dicts = data.get("tasks", [])
        self.tasks = [Task.from_dict(td) for td in task_dicts]

    def save(self) -> None:
        """保存任务到存储"""
        task_dicts = [task.to_dict() for task in self.tasks]
        self.storage.save_tasks(task_dicts, self.next_id)

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: str = Task.PRIORITY_MEDIUM,
        due_date_str: Optional[str] = None,
    ) -> Task:
        """添加新任务"""
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                # 设置为当天的23:59:59
                due_date = due_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise ValueError(f"无效的日期格式: {due_date_str}，请使用 YYYY-MM-DD")

        task = Task(
            task_id=self.next_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        self.tasks.append(task)
        self.next_id += 1
        self.save()
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: int, **kwargs) -> bool:
        """更新任务属性"""
        task = self.get_task(task_id)
        if not task:
            return False

        # 更新允许的字段
        allowed_fields = ["title", "description", "priority", "status"]
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(task, field, value)

        # 处理截止日期
        if "due_date_str" in kwargs:
            due_date_str = kwargs["due_date_str"]
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                    due_date = due_date.replace(hour=23, minute=59, second=59)
                    task.due_date = due_date
                except ValueError:
                    raise ValueError(f"无效的日期格式: {due_date_str}，请使用 YYYY-MM-DD")
            else:
                task.due_date = None

        self.save()
        return True

    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        task = self.get_task(task_id)
        if not task:
            return False
        self.tasks.remove(task)
        self.save()
        return True

    def mark_done(self, task_id: int) -> bool:
        """标记任务为已完成"""
        task = self.get_task(task_id)
        if not task:
            return False
        task.mark_done()
        self.save()
        return True

    def list_tasks(self, filter_str: Optional[str] = None) -> List[Task]:
        """列出任务，支持筛选"""
        tasks = self.tasks.copy()

        if filter_str:
            filter_str = filter_str.lower()
            if filter_str == "pending":
                tasks = [t for t in tasks if t.status == Task.STATUS_PENDING]
            elif filter_str == "in_progress":
                tasks = [t for t in tasks if t.status == Task.STATUS_IN_PROGRESS]
            elif filter_str == "done":
                tasks = [t for t in tasks if t.status == Task.STATUS_DONE]
            elif filter_str == "overdue":
                tasks = [t for t in tasks if t.is_overdue()]
            elif filter_str == "high":
                tasks = [t for t in tasks if t.priority == Task.PRIORITY_HIGH]

        # 按创建时间排序
        tasks.sort(key=lambda x: x.created_at)
        return tasks

    def get_stats(self) -> Dict[str, int]:
        """获取任务统计"""
        stats = {
            "total": len(self.tasks),
            "pending": 0,
            "in_progress": 0,
            "done": 0,
            "overdue": 0,
        }

        for task in self.tasks:
            if task.status == Task.STATUS_PENDING:
                stats["pending"] += 1
            elif task.status == Task.STATUS_IN_PROGRESS:
                stats["in_progress"] += 1
            elif task.status == Task.STATUS_DONE:
                stats["done"] += 1

            if task.is_overdue():
                stats["overdue"] += 1

        return stats
