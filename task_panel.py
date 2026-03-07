# Symphony Task Panel
# 开发者: MiniMax-M2.5
# 生成时间: 2026-03-08T01:35:48.115257
# 版本: 1.4.1

# Symphony系统可视化任务面板实现

以下是完整的Python代码实现，包含任务面板、模型选择器和进度追踪器：

```python
"""
Symphony系统可视化任务面板
Symphony System Visualization Task Panel
"""

import time
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelType(Enum):
    """模型类型枚举"""
    TRANSFORMER = "transformer"
    CNN = "cnn"
    RNN = "rnn"
    GAN = "gan"
    REINFORCEMENT = "reinforcement"


@dataclass
class Task:
    """任务数据类"""
    task_id: str
    name: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    model_type: Optional[ModelType] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._listeners: List[callable] = []
    
    def add_task(self, task: Task) -> None:
        """添加任务"""
        self._tasks[task.task_id] = task
        self._notify_listeners("task_added", task)
    
    def update_progress(self, task_id: str, progress: float, 
                       status: Optional[TaskStatus] = None) -> None:
        """更新任务进度"""
        if task_id not in self._tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self._tasks[task_id]
        task.progress = min(100.0, max(0.0, progress))
        
        if status:
            task.status = status
            if status == TaskStatus.RUNNING and not task.started_at:
               