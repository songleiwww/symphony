#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一核心调度引擎 - Symphony Core Engine
v1.0.0
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class Task:
    task_id: str
    description: str
    assigned_to: str
    priority: int
    status: str = "pending"
    created_at: str = None
    completed_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class Model:
    model_id: str
    alias: str
    role: str
    emoji: str
    specialty: str
    status: str = "idle"


class SymphonyCoreEngine:
    def __init__(self):
        self.tasks: List[Task] = []
        self.models: List[Model] = []
        self.history: List[Dict] = []
        self.start_time = datetime.now().isoformat()
    
    def register_model(self, model: Model):
        self.models.append(model)
    
    def add_task(self, task: Task):
        self.tasks.append(task)
        self.history.append({
            "type": "task_added",
            "task": task.__dict__,
            "time": datetime.now().isoformat()
        })
    
    def get_pending_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.status == "pending"]
    
    def assign_task(self, task_id: str, model_id: str) -> bool:
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        model = next((m for m in self.models if m.model_id == model_id), None)
        
        if task and model:
            task.assigned_to = model_id
            task.status = "in_progress"
            model.status = "busy"
            self.history.append({
                "type": "task_assigned",
                "task_id": task_id,
                "model_id": model_id,
                "time": datetime.now().isoformat()
            })
            return True
        return False
    
    def complete_task(self, task_id: str) -> bool:
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if task:
            task.status = "completed"
            task.completed_at = datetime.now().isoformat()
            self.history.append({
                "type": "task_completed",
                "task_id": task_id,
                "time": datetime.now().isoformat()
            })
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == "completed")
        pending = sum(1 for t in self.tasks if t.status == "pending")
        in_progress = sum(1 for t in self.tasks if t.status == "in_progress")
        
        return {
            "total_tasks": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "total_models": len(self.models),
            "uptime": (datetime.now() - datetime.fromisoformat(self.start_time)).total_seconds()
        }
    
    def export_report(self) -> str:
        report = {
            "engine_start": self.start_time,
            "generated_at": datetime.now().isoformat(),
            "stats": self.get_stats(),
            "tasks": [t.__dict__ for t in self.tasks],
            "models": [m.__dict__ for m in self.models],
            "history": self.history
        }
        return json.dumps(report, ensure_ascii=False, indent=2)


# 全局实例
symphony_core = SymphonyCoreEngine()
