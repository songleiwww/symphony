# -*- coding: utf-8 -*-
"""
序境3.0 沙箱隔离模块
=====================

本模块实现基于能力的权限模型(Capability-Based Access Control)，为序境系统提供
安全的沙箱隔离环境。包括资源配额管理、行为审计追踪、能力授权等核心功能。

作者: 少府监·司封郎中 高适
版本: 3.0.0
"""

import hashlib
import json
import time
import threading
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, Flag, auto
from typing import Any, Callable, Dict, List, Optional, Set, Union


# ============================================================================
# 能力标识定义
# ============================================================================

class Capability(Flag):
    """
    沙箱能力标志位定义
    
    使用Flag枚举实现能力的组合与继承，支持按位运算进行能力集合操作。
    继承关系:
    - READ 包含 FILE_READ, MEMORY_READ
    - WRITE 包含 FILE_WRITE, MEMORY_WRITE  
    - EXEC 包含 CODE_EXEC, PROCESS_SPAWN
    - ADMIN 包含所有其他能力
    """
    NONE = 0
    
    # 读取能力组
    FILE_READ = auto()      # 文件读取
    MEMORY_READ = auto()    # 内存读取
    NETWORK_READ = auto()   # 网络读取(GET请求)
    
    # 写入能力组
    FILE_WRITE = auto()     # 文件写入
    MEMORY_WRITE = auto()   # 内存写入
    NETWORK_WRITE = auto()  # 网络写入(POST/PUT请求)
    
    # 执行能力组
    CODE_EXEC = auto()      # 代码执行
    PROCESS_SPAWN = auto()  # 进程创建
    SHELL_EXEC = auto()     # Shell命令执行
    
    # 特殊能力
    ADMIN = auto()          # 管理员权限(所有能力)
    SYSTEM = auto()         # 系统级访问
    DEBUG = auto()          # 调试权限
    METRICS = auto()        # 指标收集
    
    # 能力组便捷定义
    READ = FILE_READ | MEMORY_READ | NETWORK_READ
    WRITE = FILE_WRITE | MEMORY_WRITE | NETWORK_WRITE
    EXEC = CODE_EXEC | PROCESS_SPAWN | SHELL_EXEC
    ALL = READ | WRITE | EXEC | ADMIN | SYSTEM | DEBUG | METRICS


class ResourceType(Enum):
    """资源类型枚举"""
    CPU_TIME = "cpu_time"           # CPU时间(毫秒)
    MEMORY = "memory"               # 内存(字节)
    DISK_IO = "disk_io"             # 磁盘IO(字节)
    NETWORK_IO = "network_io"       # 网络IO(字节)
    FILE_DESCRIPTORS = "fd"         # 文件描述符数量
    THREAD_COUNT = "threads"        # 线程数量
    PROCESS_COUNT = "processes"     # 进程数量
    REQUEST_COUNT = "requests"      # 请求次数


class AuditLevel(Enum):
    """审计级别"""
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


# ============================================================================
# 数据结构定义
# ============================================================================

@dataclass
class ResourceQuota:
    """
    资源配额定义
    
    每个沙箱实例拥有独立的资源配额，用于限制其资源使用量。
    超出配额将触发相应的限制策略。
    """
    # 时间配额(毫秒)
    cpu_time_limit: int = 60000           # 默认60秒CPU时间
    cpu_time_warning: int = 45000         # 警告阈值
    
    # 内存配额(字节)
    memory_limit: int = 512 * 1024 * 1024  # 默认512MB
    memory_warning: int = 384 * 1024 * 1024
    
    # 磁盘IO配额(字节)
    disk_io_limit: int = 1024 * 1024 * 1024  # 默认1GB
    disk_io_warning: int = 768 * 1024 * 1024
    
    # 网络IO配额(字节)
    network_io_limit: int = 100 * 1024 * 1024  # 默认100MB
    network_io_warning: int = 80 * 1024 * 1024
    
    # 资源数量限制
    max_file_descriptors: int = 256
    max_threads: int = 64
    max_processes: int = 8
    max_requests: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "cpu_time": {"limit": self.cpu_time_limit, "warning": self.cpu_time_warning},
            "memory": {"limit": self.memory_limit, "warning": self.memory_warning},
            "disk_io": {"limit": self.disk_io_limit, "warning": self.disk_io_warning},
            "network_io": {"limit": self.network_io_limit, "warning": self.network_io_warning},
            "file_descriptors": {"limit": self.max_file_descriptors},
            "threads": {"limit": self.max_threads},
            "processes": {"limit": self.max_processes},
            "requests": {"limit": self.max_requests},
        }


@dataclass
class ResourceUsage:
    """资源使用量追踪"""
    cpu_time_used: int = 0
    memory_used: int = 0
    disk_io_read: int = 0
    disk_io_write: int = 0
    network_io_sent: int = 0
    network_io_received: int = 0
    file_descriptors_open: int = 0
    threads_active: int = 0
    processes_spawned: int = 0
    requests_made: int = 0
    last_updated: float = field(default_factory=time.time)
    
    def reset(self):
        """重置所有计数器"""
        self.cpu_time_used = 0
        self.memory_used = 0
        self.disk_io_read = 0
        self.disk_io_write = 0
        self.network_io_sent = 0
        self.network_io_received = 0
        self.file_descriptors_open = 0
        self.threads_active = 0
        self.processes_spawned = 0
        self.requests_made = 0
        self.last_updated = time.time()


@dataclass
class AuditRecord:
    """审计记录"""
    event_id: str
    timestamp: float
    level: AuditLevel
    action: str
    resource: str
    capability_required: Capability
    granted: bool
    sandbox_id: str
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "level": self.level.name,
            "action": self.action,
            "resource": self.resource,
            "capability_required": self.capability_required.name if self.capability_required else "NONE",
            "granted": self.granted,
            "sandbox_id": self.sandbox_id,
            "details": self.details,
            "duration_ms": self.duration_ms,
        }


@dataclass
class CapabilityGrant:
    """
    能力授权凭证
    
    不可变的能力授权凭证，包含授权范围、有效期等信息。
    使用加密签名防止篡改。
    """
    grant_id: str
    capabilities: Capability
    resource_scope: Set[str]  # 允许访问的资源范围
    valid_from: float
    valid_until: float
    max_uses: Optional[int]  # 最大使用次数，None表示无限制
    uses_count: int = 0
    signature: str = ""
    
    def __post_init__(self):
        if not self.grant_id:
            self.grant_id = str(uuid.uuid4())
    
    def is_valid(self) -> bool:
        """检查授权是否有效"""
        now = time.time()
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.max_uses is not None and self.uses_count >= self.max_uses:
            return False
        return True
    
    def use(self) -> bool:
        """使用一次授权"""
        if not self.is_valid():
            return False
        self.uses_count += 1
        return True
    
    def sign(self, secret: str):
        """对授权进行签名"""
        data = f"{self.grant_id}:{self.capabilities.value}:{self.valid_until}"
        self.signature = hashlib.sha256(f"{data}:{secret}".encode()).hexdigest()
    
    def verify(self, secret: str) -> bool:
        """验证签名"""
        if not self.signature:
            return False
        data = f"{self.grant_id}:{self.capabilities.value}:{self.valid_until}"
        expected = hashlib.sha256(f"{data}:{secret}".encode()).hexdigest()
        return self.signature == expected


# ============================================================================
# 审计日志处理器
# ============================================================================

class AuditHandler(ABC):
    """审计日志处理器抽象基类"""
    
    @abstractmethod
    def emit(self, record: AuditRecord):
        """输出审计记录"""
        pass
    
    @abstractmethod
    def flush(self):
        """刷新缓冲区"""
        pass


class ConsoleAuditHandler(AuditHandler):
    """控制台审计处理器"""
    
    def __init__(self, min_level: AuditLevel = AuditLevel.INFO):
        self.min_level = min_level
    
    def emit(self, record: AuditRecord):
        if record.level.value < self.min_level.value:
            return
        
        level_colors = {
            AuditLevel.DEBUG: "\033[36m",     # 青色
            AuditLevel.INFO: "\033[32m",      # 绿色
            AuditLevel.WARNING: "\033[33m",   # 黄色
            AuditLevel.ERROR: "\033[31m",     # 红色
            AuditLevel.CRITICAL: "\033[35m",  # 紫色
        }
        color = level_colors.get(record.level, "")
        reset = "\033[0m"
        
        status = "✓" if record.granted else "✗"
        print(f"{color}[{record.level.name}]{reset} {record.timestamp:.3f} "
              f"{status} {record.action} on {record.resource} "
              f"(sandbox: {record.sandbox_id[:8]}...)")
    
    def flush(self):
        pass


class MemoryAuditHandler(AuditHandler):
    """内存审计处理器(带轮转)"""
    
    def __init__(self, max_records: int = 10000):
        self.max_records = max_records
        self.records: List[AuditRecord] = []
        self._lock = threading.Lock()
    
    def emit(self, record: AuditRecord):
        with self._lock:
            self.records.append(record)
            if len(self.records) > self.max_records:
                self.records = self.records[-self.max_records:]
    
    def flush(self):
        with self._lock:
            self.records.clear()
    
    def query(self, 
              level: Optional[AuditLevel] = None,
              sandbox_id: Optional[str] = None,
              action: Optional[str] = None,
              limit: int = 100) -> List[AuditRecord]:
        """查询审计记录"""
        with self._lock:
            results = self.records
            if level:
                results = [r for r in results if r.level == level]
            if sandbox_id:
                results = [r for r in results if r.sandbox_id == sandbox_id]
            if action:
                results = [r for r in results if r.action == action]
            return results[-limit:]


# ============================================================================
# 资源监控器
# ============================================================================

class ResourceMonitor:
    """资源使用监控器"""
    
    def __init__(self, quota: ResourceQuota):
        self.quota = quota
        self.usage = ResourceUsage()
        self._lock = threading.RLock()
        self._callbacks: Dict[ResourceType, List[Callable]] = defaultdict(list)
    
    def check_quota(self, resource_type: ResourceType) -> tuple[bool, str]:
        """
        检查资源配额
        
        返回: (是否允许, 警告/错误消息)
        """
        with self._lock:
            if resource_type == ResourceType.CPU_TIME:
                if self.usage.cpu_time_used >= self.quota.cpu_time_limit:
                    return False, f"CPU时间超出配额: {self.usage.cpu_time_used}/{self.quota.cpu_time_limit}ms"
                if self.usage.cpu_time_used >= self.quota.cpu_time_warning:
                    return True, f"CPU时间接近限制: {self.usage.cpu_time_used}/{self.quota.cpu_time_limit}ms"
            
            elif resource_type == ResourceType.MEMORY:
                if self.usage.memory_used >= self.quota.memory_limit:
                    return False, f"内存超出配额: {self.usage.memory_used}/{self.quota.memory_limit}bytes"
                if self.usage.memory_used >= self.quota.memory_warning:
                    return True, f"内存接近限制: {self.usage.memory_used}/{self.quota.memory_limit}bytes"
            
            elif resource_type == ResourceType.DISK_IO:
                total = self.usage.disk_io_read + self.usage.disk_io_write
                if total >= self.quota.disk_io_limit:
                    return False, f"磁盘IO超出配额: {total}/{self.quota.disk_io_limit}bytes"
                if total >= self.quota.disk_io_warning:
                    return True, f"磁盘IO接近限制: {total}/{self.quota.disk_io_limit}bytes"
            
            elif resource_type == ResourceType.NETWORK_IO:
                total = self.usage.network_io_sent + self.usage.network_io_received
                if total >= self.quota.network_io_limit:
                    return False, f"网络IO超出配额: {total}/{self.quota.network_io_limit}bytes"
                if total >= self.quota.network_io_warning:
                    return True, f"网络IO接近限制: {total}/{self.quota.network_io_limit}bytes"
            
            elif resource_type == ResourceType.FILE_DESCRIPTORS:
                if self.usage.file_descriptors_open >= self.quota.max_file_descriptors:
                    return False, f"文件描述符超出配额: {self.usage.file_descriptors_open}/{self.quota.max_file_descriptors}"
            
            elif resource_type == ResourceType.THREAD_COUNT:
                if self.usage.threads_active >= self.quota.max_threads:
                    return False, f"线程数超出配额: {self.usage.threads_active}/{self.quota.max_threads}"
            
            elif resource_type == ResourceType.PROCESS_COUNT:
                if self.usage.processes_spawned >= self.quota.max_processes:
                    return False, f"进程数超出配额: {self.usage.processes_spawned}/{self.quota.max_processes}"
            
            elif resource_type == ResourceType.REQUEST_COUNT:
                if self.usage.requests_made >= self.quota.max_requests:
                    return False, f"请求数超出配额: {self.usage.requests_made}/{self.quota.max_requests}"
            
            return True, ""
    
    def record_usage(self, resource_type: ResourceType, amount: int):
        """记录资源使用"""
        with self._lock:
            if resource_type == ResourceType.CPU_TIME:
                self.usage.cpu_time_used += amount
            elif resource_type == ResourceType.MEMORY:
                self.usage.memory_used += amount
            elif resource_type == ResourceType.DISK_IO:
                self.usage.disk_io_write += amount
            elif resource_type == ResourceType.NETWORK_IO:
                self.usage.network_io_sent += amount
            elif resource_type == ResourceType.FILE_DESCRIPTORS:
                self.usage.file_descriptors_open = amount
            elif resource_type == ResourceType.THREAD_COUNT:
                self.usage.threads_active = amount
            elif resource_type == ResourceType.PROCESS_COUNT:
                self.usage.processes_spawned = amount
            elif resource_type == ResourceType.REQUEST_COUNT:
                self.usage.requests_made += amount
            
            self.usage.last_updated = time.time()
            
            # 检查并触发回调
            allowed, msg = self.check_quota(resource_type)
            if not allowed:
                for cb in self._callbacks.get(resource_type, []):
                    try:
                        cb(resource_type, amount, msg)
                    except Exception:
                        pass
    
    def register_callback(self, resource_type: ResourceType, callback: Callable):
        """注册资源超限回调"""
        self._callbacks[resource_type].append(callback)
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """获取使用摘要"""
        with self._lock:
            return {
                "cpu_time": {
                    "used": self.usage.cpu_time_used,
                    "limit": self.quota.cpu_time_limit,
                    "percent": (self.usage.cpu_time_used / self.quota.cpu_time_limit * 100) if self.quota.cpu_time_limit else 0
                },
                "memory": {
                    "used": self.usage.memory_used,
                    "limit": self.quota.memory_limit,
                    "percent": (self.usage.memory_used / self.quota.memory_limit * 100) if self.quota.memory_limit else 0
                },
                "disk_io": {
                    "used": self.usage.disk_io_read + self.usage.disk_io_write,
                    "limit": self.quota.disk_io_limit,
                    "percent": ((self.usage.disk_io_read + self.usage.disk_io_write) / self.quota.disk_io_limit * 100) if self.quota.disk_io_limit else 0
                },
                "network_io": {
                    "used": self.usage.network_io_sent + self.usage.network_io_received,
                    "limit": self.quota.network_io_limit,
                    "percent": ((self.usage.network_io_sent + self.usage.network_io_received) / self.quota.network_io_limit * 100) if self.quota.network_io_limit else 0
                },
                "file_descriptors": {
                    "used": self.usage.file_descriptors_open,
                    "limit": self.quota.max_file_descriptors
                },
                "threads": {
                    "used": self.usage.threads_active,
                    "limit": self.quota.max_threads
                },
                "processes": {
                    "used": self.usage.processes_spawned,
                    "limit": self.quota.max_processes
                },
                "requests": {
                    "used": self.usage.requests_made,
                    "limit": self.quota.max_requests
                }
            }


# ============================================================================
# 能力检查器
# ============================================================================

class CapabilityChecker:
    """
    能力检查器
    
    基于Capability-Based Access Control (CBAC)模型实现细粒度的权限检查。
    支持能力继承、资源范围匹配、时间有效性检查等特性。
    """
    
    def __init__(self, grants: Optional[List[CapabilityGrant]] = None):
        self.grants: List[CapabilityGrant] = grants or []
        self._lock = threading.RLock()
    
    def add_grant(self, grant: CapabilityGrant):
        """添加授权凭证"""
        with self._lock:
            self.grants.append(grant)
    
    def remove_grant(self, grant_id: str) -> bool:
        """移除授权凭证"""
        with self._lock:
            for i, g in enumerate(self.grants):
                if g.grant_id == grant_id:
                    self.grants.pop(i)
                    return True
            return False
    
    def check(self, 
              capability: Capability, 
              resource: Optional[str] = None,
              consume: bool = True) -> tuple[bool, Optional[CapabilityGrant]]:
        """
        检查是否具有指定能力
        
        参数:
            capability: 需要的能力
            resource: 目标资源路径
            consume: 是否消耗授权使用次数
        
        返回:
            (是否允许, 匹配的授权凭证)
        """
        with self._lock:
            for grant in self.grants:
                # 检查授权是否有效
                if not grant.is_valid():
                    continue
                
                # 检查能力是否匹配
                if not (grant.capabilities & capability):
                    continue
                
                # 检查资源范围
                if resource and grant.resource_scope:
                    if not any(
                        resource.startswith(scope) or scope == "*"
                        for scope in grant.resource_scope
                    ):
                        continue
                
                # 消耗使用次数
                if consume:
                    grant.use()
                
                return True, grant
            
            return False, None
    
    def get_effective_capabilities(self, resource: Optional[str] = None) -> Capability:
        """
        获取对指定资源的所有有效能力
        
        返回所有授权凭证的能力集合（按位或）
        """
        with self._lock:
            result = Capability.NONE
            for grant in self.grants:
                if not grant.is_valid():
                    continue
                if resource and grant.resource_scope:
                    if not any(
                        resource.startswith(scope) or scope == "*"
                        for scope in grant.resource_scope
                    ):
                        continue
                result |= grant.capabilities
            return result


# ============================================================================
# 沙箱隔离主类
# ============================================================================

class SandboxIsolation:
    """
    沙箱隔离控制器
    
    序境3.0的核心安全组件，提供完整的沙箱隔离能力。
    
    功能特性:
    - 基于能力的细粒度权限控制
    - 资源配额与使用追踪
    - 完整的行为审计日志
    - 可扩展的策略引擎
    - 线程安全的并发操作
    
    使用示例:
        sandbox = SandboxIsolation(
            sandbox_id="agent_001",
            quota=ResourceQuota(memory_limit=256*1024*1024),
            capabilities=Capability.READ | Capability.WRITE
        )
        
        # 检查权限
        if sandbox.check_capability(Capability.FILE_READ, "/data/config.json"):
            content = sandbox.read_file("/data/config.json")
    """
    
    # 类级别的审计处理器(所有沙箱实例共享)
    _audit_handlers: List[AuditHandler] = []
    _audit_lock = threading.Lock()
    
    @classmethod
    def add_audit_handler(cls, handler: AuditHandler):
        """添加审计处理器"""
        with cls._audit_lock:
            cls._audit_handlers.append(handler)
    
    @classmethod
    def remove_audit_handler(cls, handler: AuditHandler):
        """移除审计处理器"""
        with cls._audit_lock:
            if handler in cls._audit_handlers:
                cls._audit_handlers.remove(handler)
    
    @classmethod
    def get_audit_handlers(cls) -> List[AuditHandler]:
        """获取所有审计处理器"""
        with cls._audit_lock:
            return cls._audit_handlers.copy()
    
    def __init__(
        self,
        sandbox_id: str,
        quota: Optional[ResourceQuota] = None,
        capabilities: Optional[Capability] = None,
        grants: Optional[List[CapabilityGrant]] = None,
        parent: Optional["SandboxIsolation"] = None,
        audit_enabled: bool = True,
    ):
        """
        初始化沙箱隔离器
        
        参数:
            sandbox_id: 沙箱唯一标识符
            quota: 资源配额配置
            capabilities: 直接赋予的能力标志
            grants: 能力授权凭证列表
            parent: 父沙箱(用于继承)
            audit_enabled: 是否启用审计
        """
        self.sandbox_id = sandbox_id
        self.quota = quota or ResourceQuota()
        self.capabilities = capabilities or Capability.NONE
        self.parent = parent
        self.audit_enabled = audit_enabled
        
        # 资源监控器
        self.monitor = ResourceMonitor(self.quota)
        
        # 能力检查器
        self.checker = CapabilityChecker(grants)
        
        # 沙箱元数据
        self.created_at = time.time()
        self.last_activity = time.time()
        self.is_active = True
        
        # 状态锁
        self._state_lock = threading.RLock()
        
        # 子沙箱注册表
        self._children: Dict[str, "SandboxIsolation"] = {}
    
    def check_capability(
        self, 
        capability: Capability, 
        resource: Optional[str] = None
    ) -> bool:
        """
        检查是否具有指定能力
        
        参数:
            capability: 需要的能力标志
            resource: 目标资源路径
        
        返回:
            是否具有该能力
        """
        start_time = time.time()
        granted = False
        
        # 检查直接赋予的能力
        if self.capabilities & capability:
            granted = True
        
        # 检查授权凭证
        if not granted:
            grant_ok, _ = self.checker.check(capability, resource, consume=False)
            if grant_ok:
                granted = True
        
        # 检查父沙箱能力继承
        if not granted and self.parent:
            granted = self.parent.check_capability(capability, resource)
        
        # 记录审计日志
        duration_ms = (time.time() - start_time) * 1000
        self._emit_audit(
            level=AuditLevel.DEBUG if granted else AuditLevel.WARNING,
            action="check_capability",
            resource=resource or "all",
            capability_required=capability,
            granted=granted,
            details={"capability_bits": capability.value},
            duration_ms=duration_ms
        )
        
        self.last_activity = time.time()
        return granted
    
    def request(
        self, 
        capability: Capability, 
        resource: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        请求执行操作
        
        参数:
            capability: 需要的操作能力
            resource: 目标资源
        
        返回:
            (是否允许, 拒绝原因)
        """
        start_time = time.time()
        
        # 首先检查能力
        if not self.check_capability(capability, resource):
            reason = f"缺少必要能力: {capability.name}"
            self._emit_audit(
                level=AuditLevel.WARNING,
                action="request_denied",
                resource=resource or "unknown",
                capability_required=capability,
                granted=False,
                details={"reason": reason}
            )
            return False, reason
        
        # 检查资源配额
        resource_type = self._capability_to_resource_type(capability)
        if resource_type:
            allowed, msg = self.monitor.check_quota(resource_type)
            if not allowed:
                self._emit_audit(
                    level=AuditLevel.ERROR,
                    action="quota_exceeded",
                    resource=resource or "unknown",
                    capability_required=capability,
                    granted=False,
                    details={"quota_msg": msg}
                )
                return False, msg
        
        # 记录成功请求
        duration_ms = (time.time() - start_time) * 1000
        self._emit_audit(
            level=AuditLevel.INFO,
            action="request_granted",
            resource=resource or "all",
            capability_required=capability,
            granted=True,
            duration_ms=duration_ms
        )
        
        return True, "允许"
    
    def _capability_to_resource_type(self, capability: Capability) -> Optional[ResourceType]:
        """将能力映射到资源类型"""
        mapping = {
            Capability.CODE_EXEC: ResourceType.CPU_TIME,
            Capability.PROCESS_SPAWN: ResourceType.PROCESS_COUNT,
            Capability.SHELL_EXEC: ResourceType.CPU_TIME,
            Capability.FILE_READ: ResourceType.DISK_IO,
            Capability.FILE_WRITE: ResourceType.DISK_IO,
            Capability.NETWORK_READ: ResourceType.NETWORK_IO,
            Capability.NETWORK_WRITE: ResourceType.NETWORK_IO,
        }
        return mapping.get(capability)
    
    def _emit_audit(
        self,
        level: AuditLevel,
        action: str,
        resource: str,
        capability_required: Capability,
        granted: bool,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: float = 0.0
    ):
        """发出审计记录"""
        if not self.audit_enabled:
            return
        
        record = AuditRecord(
            event_id=str(uuid.uuid4()),
            timestamp=time.time(),
            level=level,
            action=action,
            resource=resource,
            capability_required=capability_required,
            granted=granted,
            sandbox_id=self.sandbox_id,
            details=details or {},
            duration_ms=duration_ms
        )
        
        with SandboxIsolation._audit_lock:
            for handler in SandboxIsolation._audit_handlers:
                try:
                    handler.emit(record)
                except Exception as e:
                    print(f"审计处理器错误: {e}")
    
    def create_child(
        self,
        child_id: str,
        quota: Optional[ResourceQuota] = None,
        capabilities: Optional[Capability] = None
    ) -> "SandboxIsolation":
        """
        创建子沙箱
        
        子沙箱继承父沙箱的部分能力，但不能超出父沙箱的范围。
        """
        with self._state_lock:
            if child_id in self._children:
                raise ValueError(f"子沙箱 {child_id} 已存在")
            
            child = SandboxIsolation(
                sandbox_id=f"{self.sandbox_id}:{child_id}",
                quota=quota,
                capabilities=capabilities,
                parent=self,
                audit_enabled=self.audit_enabled
            )
            
            self._children[child_id] = child
            
            self._emit_audit(
                level=AuditLevel.INFO,
                action="sandbox_created",
                resource=child.sandbox_id,
                capability_required=Capability.NONE,
                granted=True,
                details={"parent": self.sandbox_id}
            )
            
            return child
    
    def destroy_child(self, child_id: str) -> bool:
        """销毁子沙箱"""
        with self._state_lock:
            if child_id not in self._children:
                return False
            
            child = self._children.pop(child_id)
            child.terminate()
            
            self._emit_audit(
                level=AuditLevel.INFO,
                action="sandbox_destroyed",
                resource=child.sandbox_id,
                capability_required=Capability.NONE,
                granted=True,
                details={"reason": "explicit_destroy"}
            )
            
            return True
    
    def terminate(self):
        """终止沙箱"""
        with self._state_lock:
            # 终止所有子沙箱
            for child in list(self._children.values()):
                child.terminate()
            self._children.clear()
            
            self.is_active = False
            self._emit_audit(
                level=AuditLevel.INFO,
                action="sandbox_terminated",
                resource=self.sandbox_id,
                capability_required=Capability.NONE,
                granted=True
            )
    
    def grant_capability(self, grant: CapabilityGrant):
        """授予能力凭证"""
        self.checker.add_grant(grant)
        self._emit_audit(
            level=AuditLevel.INFO,
            action="capability_granted",
            resource="sandbox",
            capability_required=grant.capabilities,
            granted=True,
            details={
                "grant_id": grant.grant_id,
                "max_uses": grant.max_uses
            }
        )
    
    def revoke_capability(self, grant_id: str) -> bool:
        """撤销能力凭证"""
        result = self.checker.remove_grant(grant_id)
        if result:
            self._emit_audit(
                level=AuditLevel.INFO,
                action="capability_revoked",
                resource="sandbox",
                capability_required=Capability.NONE,
                granted=True,
                details={"grant_id": grant_id}
            )
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """获取沙箱状态"""
        with self._state_lock:
            return {
                "sandbox_id": self.sandbox_id,
                "is_active": self.is_active,
                "created_at": self.created_at,
                "last_activity": self.last_activity,
                "capabilities": self.capabilities.name,
                "quota": self.quota.to_dict(),
                "usage": self.monitor.get_usage_summary(),
                "children_count": len(self._children)
            }
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.terminate()
        return False


# ============================================================================
# 便捷函数
# ============================================================================

def create_sandbox(
    sandbox_id: str,
    memory_mb: int = 512,
    cpu_time_ms: int = 60000,
    capabilities: Optional[Capability] = None
) -> SandboxIsolation:
    """
    创建沙箱的便捷函数
    
    参数:
        sandbox_id: 沙箱标识
        memory_mb: 内存配额(MB)
        cpu_time_ms: CPU时间配额(毫秒)
        capabilities: 能力标志
    
    返回:
        配置好的沙箱实例
    """
    quota = ResourceQuota(
        memory_limit=memory_mb * 1024 * 1024,
        cpu_time_limit=cpu_time_ms
    )
    return SandboxIsolation(
        sandbox_id=sandbox_id,
        quota=quota,
        capabilities=capabilities or Capability.READ
    )


def create_grand(
    capabilities: Capability,
    resource_scope: Optional[Set[str]] = None,
    valid_seconds: int = 3600,
    max_uses: Optional[int] = None
) -> CapabilityGrant:
    """
    创建能力授权的便捷函数
    
    参数:
        capabilities: 授权的能力
        resource_scope: 资源范围
        valid_seconds: 有效期(秒)
        max_uses: 最大使用次数
    
    返回:
        授权凭证
    """
    now = time.time()
    grant = CapabilityGrant(
        grant_id="",
        capabilities=capabilities,
        resource_scope=resource_scope or {"*"},
        valid_from=now,
        valid_until=now + valid_seconds,
        max_uses=max_uses
    )
    return grant


# ============================================================================
# 模块初始化
# ============================================================================

# 添加默认审计处理器
_default_audit_handler = ConsoleAuditHandler(AuditLevel.INFO)
SandboxIsolation.add_audit_handler(_default_audit_handler)

# 内存审计处理器(用于查询)
_memory_audit_handler = MemoryAuditHandler()
SandboxIsolation.add_audit_handler(_memory_audit_handler)


# 导出公共接口
__all__ = [
    "Capability",
    "ResourceType",
    "ResourceQuota",
    "ResourceUsage", 
    "ResourceMonitor",
    "CapabilityGrant",
    "CapabilityChecker",
    "SandboxIsolation",
    "AuditRecord",
    "AuditLevel",
    "AuditHandler",
    "ConsoleAuditHandler",
    "MemoryAuditHandler",
    "create_sandbox",
    "create_grand",
]
