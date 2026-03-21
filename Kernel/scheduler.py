"""
# 序境系统 - Agent任务调度中枢
# 首辅大学士顾至尊 核心框架
# 遵循序境系统总则：数据库优先、多模型协作、并发规则
"""

import sqlite3
import json
import time
import random
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ModelStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"

@dataclass
class ModelConfig:
    model_name: str
    provider: str
    api_url: str
    api_key: str
    model_type: str
    online_status: str
    use_rule: str
    id: str
    
    def is_online(self) -> bool:
        return self.online_status == "online" or self.online_status == "是"

@dataclass
class Task:
    task_id: str
    content: str
    task_type: str = "通用任务"
    priority: int = 3
    status: TaskStatus = TaskStatus.PENDING
    created_by: str = "system"
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    parent_task_id: Optional[str] = None
    features: Optional[Dict] = None
    metadata: Optional[Dict] = None

@dataclass
class TaskResult:
    task_id: str
    role_id: str
    result_content: str
    token_usage: int = 0
    duration: float = 0.0
    success: bool = True
    created_at: float = 0.0

class SchedulerCore:
    """序境统一决策中枢 - 任务调度核心"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._load_models()
        
    def _load_models(self) -> None:
        """从数据库加载最新模型配置（遵循数据库优先原则，不缓存）"""
        self.models: Dict[str, ModelConfig] = {}
        self.provider_models: Dict[str, List[ModelConfig]] = {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, 模型名称, 服务商, API地址, API密钥, 模型类型, 在线状态, 使用规则 FROM "模型配置表"')
        
        for row in cursor.fetchall():
            model_id, model_name, provider, api_url, api_key, model_type, online_status, use_rule = row
            config = ModelConfig(
                id=model_id,
                model_name=model_name,
                provider=provider,
                api_url=api_url,
                api_key=api_key,
                model_type=model_type,
                online_status=online_status,
                use_rule=use_rule
            )
            self.models[model_name] = config
            if provider not in self.provider_models:
                self.provider_models[provider] = []
            self.provider_models[provider].append(config)
        
        conn.close()
    
    def get_online_models(self, provider: Optional[str] = None) -> List[ModelConfig]:
        """获取所有在线模型"""
        self._load_models()  # 每次读取最新配置（遵循禁止固化记忆原则）
        result = []
        if provider:
            if provider in self.provider_models:
                result = [m for m in self.provider_models[provider] if m.is_online()]
        else:
            for provider_models in self.provider_models.values():
                result.extend([m for m in provider_models if m.is_online()])
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取模型健康统计"""
        self._load_models()
        stats = {}
        for provider, models in self.provider_models.items():
            total = len(models)
            online = sum(1 for m in models if m.is_online())
            offline = total - online
            stats[provider] = {
                "total": total,
                "online": online,
                "offline": offline
            }
        
        total_all = sum(s["total"] for s in stats.values())
        online_all = sum(s["online"] for s in stats.values())
        stats["_summary"] = {
            "total": total_all,
            "online": online_all,
            "offline": total_all - online_all
        }
        return stats
    
    def select_models_for_task(self, task_type: str, required_types: Optional[List[str]] = None) -> List[ModelConfig]:
        """根据任务类型选择合适的模型组合（遵循多模型协作原则，必须多模型）"""
        self._load_models()
        online_models = self.get_online_models()
        
        if required_types:
            candidates = [m for m in online_models if m.model_type in required_types]
        else:
            candidates = online_models
        
        if len(candidates) == 0:
            return []
        
        # 遵循多模型协作原则：任何任务优先考虑多模型组合
        if len(candidates) >= 3:
            # 选择不同服务商的模型以支持并发
            selected = []
            providers_seen = set()
            # 先从不同服务商选
            for model in sorted(candidates, key=lambda x: x.provider):
                if model.provider not in providers_seen and len(selected) < 3:
                    selected.append(model)
                    providers_seen.add(model.provider)
            # 如果不够，补充
            if len(selected) < 2:
                remaining = [m for m in candidates if m not in selected]
                selected.extend(remaining[:2 - len(selected)])
            return selected
        elif len(candidates) >= 2:
            return candidates[:2]
        else:
            return candidates
    
    def can_parallel_execute(self, models: List[ModelConfig]) -> bool:
        """检查是否可以并行执行：不同服务商可并发"""
        providers = set(m.provider for m in models)
        return len(providers) == len(models)
    
    def get_execution_order(self, models: List[ModelConfig]) -> List[List[ModelConfig]]:
        """获取执行顺序分组：同服务商顺序排队，不同服务商可以并发（遵循核心调度规则）"""
        by_provider: Dict[str, List[ModelConfig]] = {}
        for model in models:
            if model.provider not in by_provider:
                by_provider[model.provider] = []
            by_provider[model.provider].append(model)
        
        # 每组代表一个并发批次，同组内可以并发（不同服务商），同服务商在不同批次顺序执行
        # 同服务商顺序排队
        max_batches = max(len(models) for models in by_provider.values())
        batches = []
        for i in range(max_batches):
            batch = []
            for provider_models in by_provider.values():
                if i < len(provider_models):
                    batch.append(provider_models[i])
            if batch:
                batches.append(batch)
        return batches
    
    def create_task(self, content: str, task_type: str = "通用任务", priority: int = 3, 
                   created_by: str = "system", parent_task_id: Optional[str] = None,
                   features: Optional[Dict] = None, metadata: Optional[Dict] = None) -> Task:
        """创建新任务"""
        import uuid
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            content=content,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.PENDING,
            created_by=created_by,
            created_at=time.time(),
            parent_task_id=parent_task_id,
            features=features,
            metadata=metadata
        )
        self._save_task_to_db(task)
        return task
    
    def _save_task_to_db(self, task: Task) -> None:
        """保存任务到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        features_json = json.dumps(task.features, ensure_ascii=False) if task.features else None
        metadata_json = json.dumps(task.metadata, ensure_ascii=False) if task.metadata else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO 任务表 
            (task_id, content, task_type, priority, status, created_by, created_at, started_at, completed_at, parent_task_id, features, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.task_id,
            task.content,
            task.task_type,
            task.priority,
            task.status.value,
            task.created_by,
            task.created_at,
            task.started_at,
            task.completed_at,
            task.parent_task_id,
            features_json,
            metadata_json
        ))
        conn.commit()
        conn.close()
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """更新任务状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if status == TaskStatus.RUNNING:
            cursor.execute('UPDATE 任务表 SET status = ?, started_at = ? WHERE task_id = ?',
                         (status.value, time.time(), task_id))
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            cursor.execute('UPDATE 任务表 SET status = ?, completed_at = ? WHERE task_id = ?',
                         (status.value, time.time(), task_id))
        else:
            cursor.execute('UPDATE 任务表 SET status = ? WHERE task_id = ?',
                         (status.value, task_id))
        conn.commit()
        conn.close()
    
    def save_task_result(self, result: TaskResult) -> None:
        """保存任务结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO 任务结果表
            (task_id, role_id, result_content, token_usage, duration, success, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.task_id,
            result.role_id,
            result.result_content,
            result.token_usage,
            result.duration,
            1 if result.success else 0,
            result.created_at
        ))
        conn.commit()
        conn.close()
    
    def get_pending_tasks(self, limit: int = 10) -> List[Task]:
        """获取待执行任务（按优先级排序）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT task_id, content, task_type, priority, status, created_by, created_at, started_at, completed_at, parent_task_id, features, metadata
            FROM 任务表 WHERE status = ? ORDER BY priority ASC, created_at ASC LIMIT ?
        ''', (TaskStatus.PENDING.value, limit))
        
        tasks = []
        for row in cursor.fetchall():
            features = json.loads(row[10]) if row[10] else None
            metadata = json.loads(row[11]) if row[11] else None
            task = Task(
                task_id=row[0],
                content=row[1],
                task_type=row[2],
                priority=row[3],
                status=TaskStatus(row[4]),
                created_by=row[5],
                created_at=row[6],
                started_at=row[7],
                completed_at=row[8],
                parent_task_id=row[9],
                features=features,
                metadata=metadata
            )
            tasks.append(task)
        conn.close()
        return tasks

class MultiModelCollaboration:
    """多模型协作协议实现"""
    
    def __init__(self, scheduler: SchedulerCore):
        self.scheduler = scheduler
    
    def execute_collaborative_task(self, content: str, task_type: str, 
                                   required_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """执行多模型协作任务（遵循多模型协作原则：必须多模型工作）"""
        # 1. 选择模型组合
        models = self.scheduler.select_models_for_task(task_type, required_types)
        if len(models) == 0:
            return {
                "success": False,
                "error": "无可用在线模型",
                "models_selected": []
            }
        
        # 如果只有一个模型，仍然尝试找第二个（遵循多模型原则）
        if len(models) == 1:
            all_online = self.scheduler.get_online_models()
            if len(all_online) > 1:
                for m in all_online:
                    if m.model_name != models[0].model_name:
                        models.append(m)
                        break
        
        # 2. 获取执行批次
        batches = self.scheduler.get_execution_order(models)
        
        # 3. 创建任务
        task = self.scheduler.create_task(content, task_type, metadata={
            "collaborative": True,
            "models": [asdict(m) for m in models],
            "batches": len(batches)
        })
        
        return {
            "success": True,
            "task_id": task.task_id,
            "models_selected": [
                {"provider": m.provider, "model_name": m.model_name, "model_type": m.model_type} 
                for m in models
            ],
            "execution_batches": len(batches),
            "can_parallel": self.scheduler.can_parallel_execute(models),
            "batch_plan": [
                [{"provider": m.provider, "model_name": m.model_name} for m in batch]
                for batch in batches
            ]
        }

# 导出核心模块
__all__ = ["SchedulerCore", "MultiModelCollaboration", "ModelConfig", "Task", "TaskStatus", "ModelStatus"]
