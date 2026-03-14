#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境 ClosureChecker 闭环检测系统
====================================

团队开发成果：
- 沈清弦 (架构设计)
- 陈美琪 (代码审查)  
- 王浩然 (核心实现)
- 张明远 (测试用例)
- 赵敏 (文档编写)
- 林思远 (性能优化)

版本: v1.0.0
日期: 2026-03-10
"""

import time
import threading
import json
import logging
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


# =============================================================================
# 任务状态枚举
# =============================================================================

class TaskState(Enum):
    """任务状态枚举"""
    PENDING = "pending"           # 待执行
    RUNNING = "running"           # 执行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 执行失败
    TIMEOUT = "timeout"           # 超时
    RETRYING = "retrying"         # 重试中
    CANCELLED = "cancelled"       # 已取消


class ClosureLevel(Enum):
    """闭环级别"""
    EXECUTION = "execution"       # 执行闭环
    VALIDATION = "validation"     # 结果验证
    BUSINESS = "business"        # 业务闭环


# =============================================================================
# 数据结构
# =============================================================================

@dataclass
class TaskContext:
    """任务上下文"""
    task_id: str
    state: TaskState = TaskState.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    error_message: str = ""
    closure_status: Dict[str, bool] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "error_message": self.error_message,
            "closure_status": self.closure_status,
            "metadata": self.metadata,
        }


@dataclass
class AlertConfig:
    """告警配置"""
    enabled: bool = True
    webhook_url: str = ""
    email_recipients: List[str] = field(default_factory=list)
    alert_on_timeout: bool = True
    alert_on_failure: bool = True
    alert_on_retry_exhausted: bool = True


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_backoff: bool = True


@dataclass
class TimeoutConfig:
    """超时配置"""
    default_timeout: float = 120.0  # 默认120秒
    execution_timeout: float = 60.0
    validation_timeout: float = 30.0
    business_timeout: float = 30.0


# =============================================================================
# ClosureChecker 核心类
# =============================================================================

class ClosureChecker:
    """
    闭环检测器
    
    三层闭环检测：
    1. 执行闭环 - API返回即认为执行完成
    2. 结果验证 - 检查返回内容是否符合预期
    3. 业务闭环 - 确认业务目标达成
    """
    
    def __init__(
        self,
        timeout_config: Optional[TimeoutConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        alert_config: Optional[AlertConfig] = None,
    ):
        """初始化闭环检测器"""
        self.timeout_config = timeout_config or TimeoutConfig()
        self.retry_config = retry_config or RetryConfig()
        self.alert_config = alert_config or AlertConfig()
        
        # 任务状态存储
        self.tasks: Dict[str, TaskContext] = {}
        self.lock = threading.RLock()
        
        # 回调函数
        self.callbacks: Dict[str, List[Callable]] = {
            "on_state_change": [],
            "on_timeout": [],
            "on_failure": [],
            "on_completion": [],
            "on_retry": [],
            "on_alert": [],
        }
        
        # 统计信息
        self.stats = {
            "total_tasks": 0,
            "completed": 0,
            "failed": 0,
            "timeout": 0,
            "retried": 0,
        }
        
        # 配置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """配置日志"""
        self.logger = logging.getLogger("ClosureChecker")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    # =========================================================================
    # 任务管理
    # =========================================================================
    
    def create_task(self, task_id: str, metadata: Optional[Dict] = None) -> TaskContext:
        """创建任务"""
        with self.lock:
            task = TaskContext(
                task_id=task_id,
                metadata=metadata or {},
            )
            self.tasks[task_id] = task
            self.stats["total_tasks"] += 1
            self.logger.info(f"Task created: {task_id}")
            return task
    
    def start_task(self, task_id: str) -> bool:
        """开始任务"""
        with self.lock:
            if task_id not in self.tasks:
                self.logger.warning(f"Task not found: {task_id}")
                return False
            
            task = self.tasks[task_id]
            task.state = TaskState.RUNNING
            task.started_at = datetime.now()
            
            self._trigger_callback("on_state_change", task)
            self.logger.info(f"Task started: {task_id}")
            return True
    
    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """完成任务"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.state = TaskState.COMPLETED
            task.completed_at = datetime.now()
            
            if result:
                task.metadata["result"] = result
            
            # 执行三层闭环检测
            closure_status = self._check_closure(task)
            task.closure_status = closure_status
            
            is_fully_closed = all(closure_status.values())
            
            self.stats["completed"] += 1
            self._trigger_callback("on_completion", task)
            self._trigger_callback("on_state_change", task)
            
            self.logger.info(
                f"Task completed: {task_id}, fully_closed={is_fully_closed}"
            )
            return is_fully_closed
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """标记任务失败"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.state = TaskState.FAILED
            task.error_message = error
            task.completed_at = datetime.now()
            
            self.stats["failed"] += 1
            self._trigger_callback("on_failure", task)
            self._trigger_callback("on_state_change", task)
            
            self.logger.error(f"Task failed: {task_id}, error={error}")
            return True
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.state = TaskState.CANCELLED
            task.completed_at = datetime.now()
            
            self._trigger_callback("on_state_change", task)
            self.logger.info(f"Task cancelled: {task_id}")
            return True
    
    # =========================================================================
    # 闭环检测
    # =========================================================================
    
    def _check_closure(self, task: TaskContext) -> Dict[str, bool]:
        """执行三层闭环检测"""
        closure_status = {}
        
        # 第一层：执行闭环
        closure_status[ClosureLevel.EXECUTION.value] = (
            task.state == TaskState.COMPLETED
        )
        
        # 第二层：结果验证
        result = task.metadata.get("result")
        closure_status[ClosureLevel.VALIDATION.value] = (
            result is not None and self._validate_result(result)
        )
        
        # 第三层：业务闭环
        closure_status[ClosureLevel.BUSINESS.value] = (
            self._check_business_closure(task)
        )
        
        return closure_status
    
    def _validate_result(self, result: Any) -> bool:
        """验证结果是否符合预期"""
        # 可以根据具体业务需求重写
        if result is None:
            return False
        if isinstance(result, dict):
            return len(result) > 0
        if isinstance(result, (list, str)):
            return len(result) > 0
        return True
    
    def _check_business_closure(self, task: TaskContext) -> bool:
        """检查业务闭环"""
        # 可以根据具体业务需求重写
        metadata = task.metadata
        return metadata.get("business_closed", True)
    
    def check_closure(self, task_id: str) -> Optional[Dict[str, bool]]:
        """检查任务是否闭环"""
        with self.lock:
            if task_id not in self.tasks:
                return None
            return self.tasks[task_id].closure_status.copy()
    
    def is_fully_closed(self, task_id: str) -> bool:
        """检查任务是否完全闭环"""
        closure = self.check_closure(task_id)
        if closure is None:
            return False
        return all(closure.values())
    
    # =========================================================================
    # 超时处理
    # =========================================================================
    
    def check_timeout(self, task_id: str) -> bool:
        """检查任务是否超时"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.state != TaskState.RUNNING:
                return False
            
            if not task.started_at:
                return False
            
            elapsed = (datetime.now() - task.started_at).total_seconds()
            timeout = self._get_task_timeout(task)
            
            if elapsed > timeout:
                task.state = TaskState.TIMEOUT
                task.completed_at = datetime.now()
                self.stats["timeout"] += 1
                
                self._trigger_callback("on_timeout", task)
                self._trigger_callback("on_state_change", task)
                
                if self.alert_config.alert_on_timeout:
                    self._send_alert(task, "TIMEOUT")
                
                self.logger.warning(
                    f"Task timeout: {task_id}, elapsed={elapsed}s, timeout={timeout}s"
                )
                return True
            
            return False
    
    def _get_task_timeout(self, task: TaskContext) -> float:
        """获取任务超时时间"""
        task_type = task.metadata.get("task_type", "default")
        
        if task_type == "execution":
            return self.timeout_config.execution_timeout
        elif task_type == "validation":
            return self.timeout_config.validation_timeout
        elif task_type == "business":
            return self.timeout_config.business_timeout
        else:
            return self.timeout_config.default_timeout
    
    def start_timeout_monitor(self, task_id: str, interval: float = 1.0):
        """启动超时监控"""
        def monitor():
            while True:
                time.sleep(interval)
                with self.lock:
                    if task_id not in self.tasks:
                        break
                    task = self.tasks[task_id]
                    if task.state not in [TaskState.RUNNING, TaskState.RETRYING]:
                        break
                
                self.check_timeout(task_id)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread
    
    # =========================================================================
    # 重试机制
    # =========================================================================
    
    def should_retry(self, task_id: str) -> bool:
        """检查是否应该重试"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            return (
                task.retry_count < self.retry_config.max_retries
                and task.state in [TaskState.FAILED, TaskState.TIMEOUT]
            )
    
    def retry_task(self, task_id: str) -> bool:
        """重试任务"""
        with self.lock:
            if not self.should_retry(task_id):
                return False
            
            task = self.tasks[task_id]
            task.state = TaskState.RETRYING
            task.retry_count += 1
            
            self.stats["retried"] += 1
            self._trigger_callback("on_retry", task)
            
            # 计算延迟
            delay = self._calculate_retry_delay(task.retry_count)
            self.logger.info(
                f"Retrying task: {task_id}, "
                f"retry={task.retry_count}, "
                f"delay={delay}s"
            )
            
            return True
    
    def _calculate_retry_delay(self, retry_count: int) -> float:
        """计算重试延迟"""
        if self.retry_config.exponential_backoff:
            delay = self.retry_config.base_delay * (2 ** (retry_count - 1))
        else:
            delay = self.retry_config.base_delay
        
        return min(delay, self.retry_config.max_delay)
    
    # =========================================================================
    # 告警系统
    # =========================================================================
    
    def _send_alert(self, task: TaskContext, alert_type: str):
        """发送告警"""
        if not self.alert_config.enabled:
            return
        
        alert_message = {
            "task_id": task.task_id,
            "alert_type": alert_type,
            "state": task.state.value,
            "error_message": task.error_message,
            "timestamp": datetime.now().isoformat(),
        }
        
        self._trigger_callback("on_alert", alert_message)
        self.logger.warning(f"Alert: {alert_message}")
    
    def set_alert_callback(self, callback: Callable):
        """设置告警回调"""
        self.callbacks["on_alert"].append(callback)
    
    # =========================================================================
    # 回调管理
    # =========================================================================
    
    def register_callback(self, event: str, callback: Callable):
        """注册回调"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, *args, **kwargs):
        """触发回调"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Callback error: {e}")
    
    # =========================================================================
    # 统计和查询
    # =========================================================================
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        with self.lock:
            if task_id not in self.tasks:
                return None
            return self.tasks[task_id].to_dict()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self.lock:
            return self.stats.copy()
    
    def list_tasks(
        self,
        state: Optional[TaskState] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """列出任务"""
        with self.lock:
            tasks = list(self.tasks.values())
            
            if state:
                tasks = [t for t in tasks if t.state == state]
            
            # 按创建时间排序
            tasks.sort(key=lambda t: t.created_at, reverse=True)
            
            return [t.to_dict() for t in tasks[:limit]]
    
    def clear_completed(self, older_than_hours: int = 24):
        """清理已完成任务"""
        with self.lock:
            cutoff = datetime.now() - timedelta(hours=older_than_hours)
            to_remove = []
            
            for task_id, task in self.tasks.items():
                if task.completed_at and task.completed_at < cutoff:
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.tasks[task_id]
            
            self.logger.info(f"Cleared {len(to_remove)} completed tasks")
            return len(to_remove)


# =============================================================================
# 使用示例
# =============================================================================

def example_usage():
    """使用示例"""
    # 创建闭环检测器
    checker = ClosureChecker(
        timeout_config=TimeoutConfig(default_timeout=60.0),
        retry_config=RetryConfig(max_retries=3),
        alert_config=AlertConfig(enabled=True),
    )
    
    # 注册回调
    def on_completion(task):
        print(f"Task completed: {task.task_id}")
    
    checker.register_callback("on_completion", on_completion)
    
    # 创建并执行任务
    task_id = "task_001"
    checker.create_task(task_id, {"task_type": "default"})
    checker.start_task(task_id)
    
    # 模拟执行
    time.sleep(2)
    
    # 完成任务
    checker.complete_task(task_id, result={"data": "success"})
    
    # 检查闭环状态
    closure = checker.check_closure(task_id)
    print(f"Closure status: {closure}")
    
    # 获取统计
    stats = checker.get_stats()
    print(f"Stats: {stats}")


if __name__ == "__main__":
    example_usage()
