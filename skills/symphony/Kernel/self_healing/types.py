# -*- coding: utf-8 -*-
"""自愈系统类型定义"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class AnomalyType(Enum):
    # 进程级异�?    CRASH = "crash"
    DEADLOCK = "deadlock"
    MEMORY_OVERFLOW = "memory_overflow"
    CPU_OVERLOAD = "cpu_overload"
    THREAD_LEAK = "thread_leak"
    
    # 数据级异�?    DB_CORRUPTION = "db_corruption"
    CONFIG_CORRUPTION = "config_corruption"
    CACHE_CORRUPTION = "cache_corruption"
    DATA_MISSING = "data_missing"
    
    # 依赖级异�?    MODEL_SERVICE_DOWN = "model_service_down"
    API_TIMEOUT = "api_timeout"
    SUBAGENT_SESSION_FAILED = "subagent_session_failed"
    DEPENDENCY_MISSING = "dependency_missing"

class HealingAction(Enum):
    NO_ACTION = "no_action"
    RESTART_COMPONENT = "restart_component"
    RESTORE_FROM_BACKUP = "restore_from_backup"
    RETRY_REQUEST = "retry_request"
    SWITCH_TO_BACKUP = "switch_to_backup"
    DEGRADE_SERVICE = "degrade_service"
    ALERT_ADMIN = "alert_admin"

@dataclass
class AnomalyEvent:
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: HealthStatus
    component: str
    description: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealingResult:
    event_id: str
    action: HealingAction
    success: bool
    description: str
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthReport:
    timestamp: float = field(default_factory=time.time)
    overall_status: HealthStatus = HealthStatus.HEALTHY
    component_status: Dict[str, HealthStatus] = field(default_factory=dict)
    anomalies: List[AnomalyEvent] = field(default_factory=list)
    resource_usage: Dict[str, float] = field(default_factory=dict)

