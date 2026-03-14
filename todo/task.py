from datetime import datetime
from typing import Optional, Dict, Any


class Task:
    """任务数据模型"""

    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"
    PRIORITIES = [PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW]

    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"
    STATUSES = [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_DONE]

    def __init__(
        self,
        task_id: int,
        title: str,
        description: str = "",
        priority: str = PRIORITY_MEDIUM,
        status: str = STATUS_PENDING,
        created_at: Optional[datetime] = None,
        due_date: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ):
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority if priority in self.PRIORITIES else self.PRIORITY_MEDIUM
        self.status = status if status in self.STATUSES else self.STATUS_PENDING
        self.created_at = created_at or datetime.now()
        self.due_date = due_date
        self.completed_at = completed_at

    def to_dict(self) -> Dict[str, Any]:
        """将任务转换为字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建任务对象"""
        return cls(
            task_id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", cls.PRIORITY_MEDIUM),
            status=data.get("status", cls.STATUS_PENDING),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
        )

    def mark_done(self) -> None:
        """标记任务为已完成"""
        self.status = self.STATUS_DONE
        self.completed_at = datetime.now()

    def is_overdue(self) -> bool:
        """检查任务是否过期"""
        if self.due_date is None:
            return False
        return self.due_date < datetime.now() and self.status != self.STATUS_DONE

    def get_priority_emoji(self) -> str:
        """获取优先级emoji"""
        emoji_map = {
            self.PRIORITY_HIGH: "🔴",
            self.PRIORITY_MEDIUM: "🟡",
            self.PRIORITY_LOW: "🟢",
        }
        return emoji_map.get(self.priority, "⚪")

    def get_status_emoji(self) -> str:
        """获取状态emoji"""
        emoji_map = {
            self.STATUS_PENDING: "📋",
            self.STATUS_IN_PROGRESS: "🔄",
            self.STATUS_DONE: "✅",
        }
        return emoji_map.get(self.status, "❓")

    def __str__(self) -> str:
        """任务的字符串表示"""
        status_str = f"{self.get_status_emoji()} {self.status.upper()}"
        priority_str = f"{self.get_priority_emoji()} {self.priority.upper()}"
        overdue_str = " ⚠️ OVERDUE" if self.is_overdue() else ""

        result = f"[{self.id}] {self.title}\n"
        result += f"    状态: {status_str} | 优先级: {priority_str}{overdue_str}\n"

        if self.description:
            result += f"    描述: {self.description}\n"

        if self.due_date:
            result += f"    截止: {self.due_date.strftime('%Y-%m-%d %H:%M')}\n"

        result += f"    创建: {self.created_at.strftime('%Y-%m-%d %H:%M')}"

        if self.completed_at:
            result += f"\n    完成: {self.completed_at.strftime('%Y-%m-%d %H:%M')}"

        return result
