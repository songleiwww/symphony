#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境3.0 集成入口模块
===================

序境（Xujing）3.0 核心集成入口，提供统一的API访问所有子系统。

模块架构：
- ipc_protocol: 标准化IPC通信协议
- lifecycle_manager: 单元生命周期状态机
- memory_system_v2: 三层记忆系统
- nucleus_core: 内核核心（消息路由、生命周期、接口契约）
- unit_registry: 单元注册中心

作者：少府监·工部尚书 李太白
版本：3.0.0
"""

# ============================================================
# 模块导入
# ============================================================

from . import ipc_protocol
from . import lifecycle_manager
from . import memory_system_v2
from . import nucleus_core
from . import unit_registry

# 从各模块导入核心类和枚举
from .ipc_protocol import (
    MessageType,
    MessagePriority,
    IPCMessage,
    create_request,
    create_response,
    create_event,
    create_error,
    ErrorCode,
    SystemAction
)

from .lifecycle_manager import (
    UnitState,
    LifecycleEvent,
    UnitMetadata,
    LifecycleResult,
    LifecycleManager,
    create_manager
)

from .memory_system_v2 import (
    MemoryType,
    MemoryPriority,
    MemoryBlock,
    WorkingMemory,
    LongTermMemory,
    IndexMemory,
    MemorySystemV2,
    create_memory_system
)

from .nucleus_core import (
    MessagePriority as NucleusMessagePriority,
    ComponentState,
    Message,
    MessageRouter,
    LifecycleManager as NucleusLifecycleManager,
    IComponent,
    IMessageHandler,
    IPlugin,
    NucleusCore
)

from .unit_registry import (
    UnitState as RegistryUnitState,
    UnitType,
    UnitManifest,
    UnitMetadata as RegistryUnitMetadata,
    UnitRegistry
)

# ============================================================
# 统一入口类
# ============================================================

class XujingEvolution:
    """
    序境3.0 统一入口类
    =================
    
    整合所有核心模块，提供统一的初始化、运行和管理接口。
    
    使用示例:
        # 创建序境实例
        xujing = XujingEvolution()
        
        # 初始化所有子系统
        xujing.initialize()
        
        # 启动
        xujing.start()
        
        # ... 运行任务
        
        # 停止
        xujing.stop()
        
        # 销毁
        xujing.destroy()
    
    属性:
        core: 内核核心实例
        lifecycle: 生命周期管理器
        memory: 记忆系统
        registry: 单元注册中心
        ipc: IPC协议模块
    """
    
    def __init__(self, config: dict = None):
        """
        初始化序境3.0
        
        Args:
            config: 配置字典，可包含:
                - name: 序境实例名称
                - version: 版本号
                - memory_capacity: 工作记忆容量
                - memory_storage_path: 记忆存储路径
                - registry_base_path: 单元注册基础路径
        """
        self._config = config or {}
        self._name = self._config.get("name", "序境3.0")
        self._version = self._config.get("version", "3.0.0")
        
        # 核心子系统实例
        self._core: NucleusCore = None
        self._lifecycle: LifecycleManager = None
        self._memory: MemorySystemV2 = None
        self._registry: UnitRegistry = None
        
        # 状态标志
        self._initialized = False
        self._running = False
        
        # 初始化子系统
        self._init_subsystems()
        
        print(f"[Xujing3.0] Init complete: {self._name} v{self._version}")
    
    def _init_subsystems(self):
        """初始化所有子系统"""
        # 1. 初始化内核核心
        self._core = NucleusCore(self._config)
        
        # 2. 初始化生命周期管理器
        self._lifecycle = LifecycleManager(
            max_retries=self._config.get("max_retries", 3)
        )
        
        # 3. 初始化记忆系统
        memory_capacity = self._config.get("memory_capacity", 100)
        memory_storage = self._config.get("memory_storage_path", "./xujing_memory")
        self._memory = MemorySystemV2(
            working_capacity=memory_capacity,
            storage_path=memory_storage
        )
        
        # 4. 初始化单元注册中心
        registry_path = self._config.get("registry_base_path", "./units")
        self._registry = UnitRegistry(base_path=registry_path)
    
    # -------------------- 属性访问器 --------------------
    
    @property
    def name(self) -> str:
        """序境实例名称"""
        return self._name
    
    @property
    def version(self) -> str:
        """版本号"""
        return self._version
    
    @property
    def core(self) -> NucleusCore:
        """获取内核核心实例"""
        return self._core
    
    @property
    def lifecycle(self) -> LifecycleManager:
        """获取生命周期管理器实例"""
        return self._lifecycle
    
    @property
    def memory(self) -> MemorySystemV2:
        """获取记忆系统实例"""
        return self._memory
    
    @property
    def registry(self) -> UnitRegistry:
        """获取单元注册中心实例"""
        return self._registry
    
    @property
    def ipc(self):
        """获取IPC协议模块"""
        return ipc_protocol
    
    @property
    def is_initialized(self) -> bool:
        """是否已初始化"""
        return self._initialized
    
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running
    
    # -------------------- 生命周期方法 --------------------
    
    def initialize(self) -> bool:
        """
        初始化序境
        
        初始化所有子系统，建立内部连接和事件通道。
        
        Returns:
            是否成功初始化
        """
        if self._initialized:
            print("⚠️ 序境已经初始化")
            return True
        
        try:
            # 初始化内核核心
            if self._core:
                self._core.initialize()
            
            self._initialized = True
            print(f"✅ 序境初始化成功: {self._name}")
            return True
            
        except Exception as e:
            print(f"❌ 序境初始化失败: {e}")
            return False
    
    def start(self) -> bool:
        """
        启动序境
        
        开始处理消息、事件和任务。
        
        Returns:
            是否成功启动
        """
        if not self._initialized:
            print("❌ 序境未初始化，请先调用 initialize()")
            return False
        
        if self._running:
            print("⚠️ 序境已经在运行")
            return True
        
        try:
            # 启动内核核心
            if self._core:
                self._core.start()
            
            self._running = True
            print(f"🚀 序境已启动: {self._name}")
            return True
            
        except Exception as e:
            print(f"❌ 序境启动失败: {e}")
            return False
    
    def stop(self) -> bool:
        """
        停止序境
        
        暂停所有活动，保存状态。
        
        Returns:
            是否成功停止
        """
        if not self._running:
            return True
        
        try:
            # 停止内核核心
            if self._core:
                self._core.stop()
            
            self._running = False
            print(f"🛑 序境已停止: {self._name}")
            return True
            
        except Exception as e:
            print(f"❌ 序境停止失败: {e}")
            return False
    
    def destroy(self) -> bool:
        """
        销毁序境
        
        清理所有资源，完全关闭序境。
        
        Returns:
            是否成功销毁
        """
        try:
            # 先停止
            if self._running:
                self.stop()
            
            # 销毁内核核心
            if self._core:
                self._core.destroy()
            
            # 清理记忆系统
            if self._memory:
                self._memory.consolidate()
            
            self._initialized = False
            print(f"🗑️ 序境已销毁: {self._name}")
            return True
            
        except Exception as e:
            print(f"❌ 序境销毁失败: {e}")
            return False
    
    # -------------------- 便捷方法 --------------------
    
    def create_unit(self, unit_id: str, unit_name: str, version: str = "1.0.0") -> LifecycleResult:
        """
        创建并激活一个单元
        
        Args:
            unit_id: 单元唯一标识
            unit_name: 单元名称
            version: 版本号
            
        Returns:
            LifecycleResult: 操作结果
        """
        return self._lifecycle.full_lifecycle(unit_id, unit_name, version)
    
    def store_memory(self, content: str, memory_type: str = "episodic", 
                   priority: str = "normal", tags: list = None) -> str:
        """
        存储记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型 (episodic/semantic/procedural/emotional)
            priority: 优先级 (critical/high/normal/low)
            tags: 标签列表
            
        Returns:
            记忆ID
        """
        # 转换字符串到枚举
        mem_type = MemoryType[memory_type.upper()] if isinstance(memory_type, str) else memory_type
        mem_priority = MemoryPriority[priority.upper()] if isinstance(priority, str) else priority
        
        return self._memory.store(
            content=content,
            memory_type=mem_type,
            priority=mem_priority,
            tags=tags or []
        )
    
    def search_memory(self, query: str, top_k: int = 10) -> list:
        """
        搜索记忆
        
        Args:
            query: 查询内容
            top_k: 返回结果数量
            
        Returns:
            (相关性分数, 记忆块)列表
        """
        return self._memory.search(query, top_k=top_k)
    
    def send_message(self, sender: str, receiver: str, action: str, 
                    payload: dict = None) -> bool:
        """
        发送消息
        
        Args:
            sender: 发送方
            receiver: 接收方
            action: 操作名称
            payload: 消息载荷
            
        Returns:
            是否成功发送
        """
        message = create_request(
            sender=sender,
            receiver=receiver,
            action=action,
            payload=payload or {}
        )
        
        if self._core:
            return self._core.send_message(
                Message(
                    type=action,
                    payload=payload or {},
                    source=sender,
                    target=receiver
                )
            )
        return False
    
    def register_unit(self, manifest: UnitManifest, base_path: str = "") -> bool:
        """
        注册单元
        
        Args:
            manifest: 单元清单
            base_path: 单元基础路径
            
        Returns:
            是否注册成功
        """
        return self._registry.register(manifest, base_path)
    
    def load_unit(self, unit_id: str) -> bool:
        """
        加载单元
        
        Args:
            unit_id: 单元标识符
            
        Returns:
            是否加载成功
        """
        return self._registry.load(unit_id)
    
    def activate_unit(self, unit_id: str) -> bool:
        """
        激活单元
        
        Args:
            unit_id: 单元标识符
            
        Returns:
            是否激活成功
        """
        return self._registry.activate(unit_id)
    
    def get_status(self) -> dict:
        """
        获取序境状态
        
        Returns:
            状态字典
        """
        status = {
            "name": self._name,
            "version": self._version,
            "initialized": self._initialized,
            "running": self._running
        }
        
        if self._core:
            status["core"] = self._core.get_status()
        
        if self._memory:
            status["memory"] = self._memory.get_stats()
        
        if self._registry:
            status["registry"] = self._registry.get_stats()
        
        return status
    
    def __repr__(self) -> str:
        return f"XujingEvolution(name={self._name}, version={self._version}, running={self._running})"


# ============================================================
# 便捷函数
# ============================================================

def create_xujing(config: dict = None) -> XujingEvolution:
    """
    创建序境实例的便捷函数
    
    Args:
        config: 配置字典
        
    Returns:
        XujingEvolution 实例
    """
    return XujingEvolution(config)


def quick_start(name: str = "序境3.0") -> XujingEvolution:
    """
    快速启动序境
    
    创建实例、初始化、启动一步完成。
    
    Args:
        name: 序境名称
        
    Returns:
        已启动的 XujingEvolution 实例
    """
    xujing = XujingEvolution({"name": name})
    xujing.initialize()
    xujing.start()
    return xujing


# ============================================================
# 导出清单
# ============================================================

__all__ = [
    # 版本信息
    '__version__',
    '__author__',
    
    # 模块引用
    'ipc_protocol',
    'lifecycle_manager', 
    'memory_system_v2',
    'nucleus_core',
    'unit_registry',
    
    # IPC协议
    'MessageType',
    'MessagePriority',
    'IPCMessage',
    'create_request',
    'create_response',
    'create_event',
    'create_error',
    'ErrorCode',
    'SystemAction',
    
    # 生命周期管理
    'UnitState',
    'LifecycleEvent',
    'UnitMetadata',
    'LifecycleResult',
    'LifecycleManager',
    'create_manager',
    
    # 记忆系统
    'MemoryType',
    'MemoryPriority',
    'MemoryBlock',
    'WorkingMemory',
    'LongTermMemory',
    'IndexMemory',
    'MemorySystemV2',
    'create_memory_system',
    
    # 内核核心
    'ComponentState',
    'Message',
    'MessageRouter',
    'IComponent',
    'IMessageHandler',
    'IPlugin',
    'NucleusCore',
    
    # 单元注册
    'UnitType',
    'UnitManifest',
    'UnitMetadata as RegistryUnitMetadata',
    'UnitRegistry',
    
    # 统一入口
    'XujingEvolution',
    'create_xujing',
    'quick_start',
]

# 版本信息
__version__ = "3.0.0"
__author__ = "少府监·工部尚书 李太白"
