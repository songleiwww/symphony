#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
容错系统 - 故障检测、自动重试、故障转移、熔断保护
"""
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from collections import deque
import sqlite3
import os

class FaultType(Enum):
    """故障类型"""
    TIMEOUT = "timeout"           # 超时
    RATE_LIMIT = "rate_limit"     # 限流
    NETWORK_ERROR = "network"      # 网络错误
    MODEL_ERROR = "model_error"   # 模型错误
    UNKNOWN = "unknown"           # 未知错误

class CircuitState(Enum):
    """熔断状态"""
    CLOSED = "closed"     # 正常
    OPEN = "open"         # 熔断中
    HALF_OPEN = "half_open"  # 半开（尝试恢复）

@dataclass
class FaultRecord:
    """故障记录"""
    fault_id: str
    fault_type: FaultType
    model_name: str
    error_message: str
    timestamp: float
    retry_count: int = 0
    resolved: bool = False

class FaultTolerance:
    """容错系统"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", 
                "symphony.db"
            )
        else:
            self.db_path = db_path
        
        # 熔断器配置
        self.circuit_breakers: Dict[str, Dict] = {}  # model_name -> circuit config
        
        # 故障统计
        self.fault_stats: Dict[str, Dict] = {}  # model_name -> stats
        
        # 重试配置
        self.retry_config = {
            "max_retries": 3,
            "retry_delay": 2,  # 秒
            "backoff_multiplier": 2,  # 指数退避
            "max_retry_delay": 60
        }
        
        # 熔断配置
        self.circuit_config = {
            "failure_threshold": 5,    # 连续失败次数
            "recovery_timeout": 300,   # 恢复超时（秒）
            "half_open_requests": 3    # 半开状态允许的测试请求数
        }
        
        # 初始化
        self._init_fault_tables()
    
    def _init_fault_tables(self):
        """初始化故障相关数据表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 故障记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS 故障记录表 (
            fault_id TEXT PRIMARY KEY,
            fault_type TEXT NOT NULL,
            model_name TEXT NOT NULL,
            error_message TEXT,
            timestamp REAL NOT NULL,
            retry_count INTEGER DEFAULT 0,
            resolved INTEGER DEFAULT 0
        )
        ''')
        
        # 熔断器状态表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS 熔断器状态表 (
            model_name TEXT PRIMARY KEY,
            state TEXT DEFAULT 'closed',
            failure_count INTEGER DEFAULT 0,
            last_failure_time REAL,
            last_success_time REAL,
            updated_at REAL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def should_retry(self, model_name: str, error: Exception) -> bool:
        """判断是否应该重试"""
        error_msg = str(error).lower()
        
        # 可重试的错误类型
        retryable_errors = [
            "timeout", "rate limit", "429", "502", "503", "504",
            "connection", "network", "temporarily unavailable"
        ]
        
        for retryable in retryable_errors:
            if retryable in error_msg:
                return True
        
        # 检查熔断器状态
        if self.is_circuit_open(model_name):
            return False
        
        return True
    
    def get_retry_delay(self, retry_count: int) -> float:
        """计算重试延迟（指数退避）"""
        delay = self.retry_config["retry_delay"] * (self.retry_config["backoff_multiplier"] ** retry_count)
        return min(delay, self.retry_config["max_retry_delay"])
    
    def execute_with_retry(self, func: Callable, model_name: str, 
                          *args, **kwargs) -> tuple:
        """执行函数并自动重试"""
        last_error = None
        retry_count = 0
        
        while retry_count <= self.retry_config["max_retries"]:
            try:
                result = func(*args, **kwargs)
                
                # 成功：更新熔断器状态
                self.record_success(model_name)
                return True, result, None
                
            except Exception as e:
                last_error = e
                
                # 记录失败
                self.record_failure(model_name, str(e))
                
                # 检查是否可重试
                if not self.should_retry(model_name, e):
                    break
                
                # 等待后重试
                if retry_count < self.retry_config["max_retries"]:
                    delay = self.get_retry_delay(retry_count)
                    print(f"[容错] {model_name} 失败，{delay}秒后重试 ({retry_count + 1}/{self.retry_config['max_retries']})")
                    time.sleep(delay)
                
                retry_count += 1
        
        # 重试耗尽，返回失败
        return False, None, str(last_error)
    
    def is_circuit_open(self, model_name: str) -> bool:
        """检查熔断器是否开启"""
        if model_name not in self.circuit_breakers:
            return False
        
        state = self.circuit_breakers[model_name]["state"]
        if state == CircuitState.OPEN.value:
            # 检查是否超过恢复超时
            last_failure = self.circuit_breakers[model_name].get("last_failure_time", 0)
            if time.time() - last_failure > self.circuit_config["recovery_timeout"]:
                # 转换为半开状态
                self.circuit_breakers[model_name]["state"] = CircuitState.HALF_OPEN.value
                self.circuit_breakers[model_name]["half_open_count"] = 0
                return False
            return True
        
        return False
    
    def record_failure(self, model_name: str, error_message: str):
        """记录失败"""
        # 更新内存中的统计
        if model_name not in self.fault_stats:
            self.fault_stats[model_name] = {
                "total_failures": 0,
                "recent_failures": deque(maxlen=10),
                "last_failure_time": None
            }
        
        self.fault_stats[model_name]["total_failures"] += 1
        self.fault_stats[model_name]["recent_failures"].append(time.time())
        self.fault_stats[model_name]["last_failure_time"] = time.time()
        
        # 更新熔断器状态
        if model_name not in self.circuit_breakers:
            self.circuit_breakers[model_name] = {
                "state": CircuitState.CLOSED.value,
                "failure_count": 0,
                "last_failure_time": None,
                "last_success_time": None
            }
        
        circuit = self.circuit_breakers[model_name]
        circuit["failure_count"] += 1
        circuit["last_failure_time"] = time.time()
        
        # 检查是否需要熔断
        if circuit["failure_count"] >= self.circuit_config["failure_threshold"]:
            circuit["state"] = CircuitState.OPEN.value
            print(f"[熔断] {model_name} 触发熔断，连续失败 {circuit['failure_count']} 次")
        
        # 更新数据库
        self._update_circuit_db(model_name)
        
        # 记录故障
        self._log_fault(model_name, error_message)
    
    def record_success(self, model_name: str):
        """记录成功"""
        if model_name not in self.circuit_breakers:
            self.circuit_breakers[model_name] = {
                "state": CircuitState.CLOSED.value,
                "failure_count": 0,
                "last_failure_time": None,
                "last_success_time": None
            }
        
        circuit = self.circuit_breakers[model_name]
        
        if circuit["state"] == CircuitState.HALF_OPEN.value:
            # 半开状态下成功，关闭熔断
            circuit["state"] = CircuitState.CLOSED.value
            circuit["failure_count"] = 0
            print(f"[熔断] {model_name} 熔断恢复")
        elif circuit["state"] == CircuitState.CLOSED.value:
            # 正常状态：重置失败计数
            circuit["failure_count"] = max(0, circuit["failure_count"] - 1)
        
        circuit["last_success_time"] = time.time()
        self._update_circuit_db(model_name)
    
    def _update_circuit_db(self, model_name: str):
        """更新熔断器数据库"""
        if model_name not in self.circuit_breakers:
            return
        
        circuit = self.circuit_breakers[model_name]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO 熔断器状态表 (
            model_name, state, failure_count, last_failure_time, last_success_time, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            model_name, circuit["state"], circuit["failure_count"],
            circuit.get("last_failure_time"), circuit.get("last_success_time"), time.time()
        ))
        
        conn.commit()
        conn.close()
    
    def _log_fault(self, model_name: str, error_message: str):
        """记录故障到数据库"""
        import uuid
        fault_id = f"fault_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO 故障记录表 (
            fault_id, fault_type, model_name, error_message, timestamp
        ) VALUES (?, ?, ?, ?, ?)
        ''', (fault_id, FaultType.UNKNOWN.value, model_name, error_message, time.time()))
        
        conn.commit()
        conn.close()
    
    def get_model_health(self, model_name: str) -> Dict:
        """获取模型健康状态"""
        stats = self.fault_stats.get(model_name, {})
        circuit = self.circuit_breakers.get(model_name, {})
        
        # 计算最近失败率
        recent_failures = stats.get("recent_failures", [])
        recent_fail_count = sum(1 for t in recent_failures if time.time() - t < 300)  # 5分钟内
        
        if recent_fail_count >= 3:
            health = "unhealthy"
        elif recent_fail_count >= 1:
            health = "degraded"
        else:
            health = "healthy"
        
        return {
            "model_name": model_name,
            "health": health,
            "circuit_state": circuit.get("state", CircuitState.CLOSED.value),
            "failure_count": circuit.get("failure_count", 0),
            "recent_failures_5min": recent_fail_count,
            "last_failure_time": stats.get("last_failure_time"),
            "last_success_time": circuit.get("last_success_time")
        }
    
    def get_all_health(self) -> List[Dict]:
        """获取所有模型健康状态"""
        models = list(self.circuit_breakers.keys())
        return [self.get_model_health(m) for m in models]

# 单例实例
_fault_tolerance_instance: Optional[FaultTolerance] = None

def get_fault_tolerance() -> FaultTolerance:
    """获取容错系统单例"""
    global _fault_tolerance_instance
    if _fault_tolerance_instance is None:
        _fault_tolerance_instance = FaultTolerance()
    return _fault_tolerance_instance

if __name__ == "__main__":
    # 测试容错系统
    ft = get_fault_tolerance()
    
    # 模拟失败
    ft.record_failure("test_model", "Rate limit exceeded")
    ft.record_failure("test_model", "Network timeout")
    
    # 获取健康状态
    health = ft.get_model_health("test_model")
    print(f"模型健康状态: {health}")
    
    # 检查熔断
    ft.record_failure("test_model", "Another failure")
    ft.record_failure("test_model", "Yet another failure")
    is_open = ft.is_circuit_open("test_model")
    print(f"熔断开启: {is_open}")
