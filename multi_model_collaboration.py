"""
Symphony 多模型协作系统
- 智能任务分配
- 模型负载均衡
- 故障自动转移
"""
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable
import requests


class MultiModelCollaboration:
    """多模型协作系统"""
    
    def __init__(self):
        self.models = {}           # model_id -> model_info
        self.task_queue = []       # 任务队列
        self.results = {}          # task_id -> result
        self.load_balancer = "round_robin"  # 负载均衡策略
        self.current_index = 0
    
    def register_model(self, model_id: str, model_info: dict):
        """注册模型"""
        self.models[model_id] = {
            **model_info,
            "status": "available",
            "tasks_completed": 0,
            "avg_response_time": 0,
            "registered_at": datetime.now().isoformat()
        }
    
    def get_available_models(self) -> List[str]:
        """获取可用模型"""
        return [mid for mid, m in self.models.items() if m["status"] == "available"]
    
    def select_model(self, strategy: str = "least_loaded") -> Optional[str]:
        """选择最优模型"""
        available = self.get_available_models()
        if not available:
            return None
        
        if strategy == "round_robin":
            model_id = available[self.current_index % len(available)]
            self.current_index += 1
            return model_id
        
        elif strategy == "least_loaded":
            return min(available, key=lambda m: self.models[m]["tasks_completed"])
        
        elif strategy == "fastest":
            return min(available, key=lambda m: self.models[m]["avg_response_time"])
        
        return available[0]
    
    def assign_task(self, task: dict, model_id: str = None) -> str:
        """分配任务"""
        if not model_id:
            model_id = self.select_model()
        
        if not model_id:
            return None
        
        task_id = f"task_{len(self.task_queue)}_{int(time.time())}"
        
        self.task_queue.append({
            "task_id": task_id,
            "task": task,
            "model_id": model_id,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        })
        
        return task_id
    
    def execute_task(self, task_id: str, executor: Callable) -> dict:
        """执行任务"""
        task_info = next((t for t in self.task_queue if t["task_id"] == task_id), None)
        if not task_info:
            return {"status": "error", "message": "任务不存在"}
        
        model_id = task_info["model_id"]
        task = task_info["task"]
        
        try:
            # 执行任务
            result = executor(task)
            
            # 更新模型统计
            if model_id in self.models:
                self.models[model_id]["tasks_completed"] += 1
            
            self.results[task_id] = {
                "status": "success",
                "result": result,
                "model_id": model_id,
                "completed_at": datetime.now().isoformat()
            }
            
            # 更新任务状态
            task_info["status"] = "completed"
            
            return self.results[task_id]
            
        except Exception as e:
            # 故障转移
            task_info["status"] = "failed"
            self.results[task_id] = {
                "status": "failed",
                "error": str(e),
                "model_id": model_id
            }
            
            # 尝试故障转移
            new_model = self.select_model()
            if new_model and new_model != model_id:
                new_task_id = self.assign_task(task, new_model)
                return {"status": "failed_and_redirected", "new_task_id": new_task_id}
            
            return self.results[task_id]
    
    def get_collaboration_status(self) -> dict:
        """获取协作状态"""
        return {
            "total_models": len(self.models),
            "available_models": len(self.get_available_models()),
            "pending_tasks": len([t for t in self.task_queue if t["status"] == "pending"]),
            "completed_tasks": len([t for t in self.task_queue if t["status"] == "completed"]),
            "models": {mid: {"status": m["status"], "tasks": m["tasks_completed"]} 
                      for mid, m in self.models.items()}
        }


# 全局实例
multi_model = MultiModelCollaboration()
