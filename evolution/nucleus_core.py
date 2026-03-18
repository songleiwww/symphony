# -*- coding: utf-8 -*-
"""
序境3.0 内核核心模块
==================

序境内核最小边界定义：
1. 消息路由 - 负责消息的分发、过滤、路由
2. 生命周期管理 - 组件的创建、初始化、运行、销毁
3. 接口契约 - 组件间交互的标准化接口

作者：少府监·工部尚书 李太白
版本：3.0.0-alpha
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid


# ============================================================
# 消息路由模块
# ============================================================

class MessagePriority(Enum):
    """消息优先级枚举"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class Message:
    """
    消息结构体
    
    属性:
        id: 唯一标识符
        type: 消息类型
        payload: 消息内容
        priority: 优先级
        source: 来源组件
        target: 目标组件
        timestamp: 时间戳
        metadata: 元数据
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    payload: Any = None
    priority: MessagePriority = MessagePriority.NORMAL
    source: str = ""
    target: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MessageRouter:
    """
    消息路由器
    
    负责消息的分发、过滤、路由功能
    """
    
    def __init__(self):
        self._routes: Dict[str, List[Callable]] = {}
        self._filters: List[Callable[[Message], bool]] = []
        self._message_queue: List[Message] = []
    
    def register_route(self, message_type: str, handler: Callable[[Message], None]) -> None:
        """
        注册消息路由
        
        Args:
            message_type: 消息类型
            handler: 处理函数
        """
        if message_type not in self._routes:
            self._routes[message_type] = []
        self._routes[message_type].append(handler)
    
    def add_filter(self, filter_func: Callable[[Message], bool]) -> None:
        """
        添加消息过滤器
        
        Args:
            filter_func: 过滤函数，返回True表示通过
        """
        self._filters.append(filter_func)
    
    def route(self, message: Message) -> bool:
        """
        路由消息
        
        Args:
            message: 待路由的消息
            
        Returns:
            是否成功路由
        """
        # 先经过过滤器
        for f in self._filters:
            if not f(message):
                return False
        
        # 查找对应的处理器
        handlers = self._routes.get(message.type, [])
        
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                # 记录错误但继续处理其他处理器
                print(f"消息处理错误: {e}")
        
        return len(handlers) > 0
    
    def broadcast(self, message: Message) -> None:
        """
        广播消息到所有已注册的类型处理器
        
        Args:
            message: 待广播的消息
        """
        for handlers in self._routes.values():
            for handler in handlers:
                try:
                    handler(message)
                except Exception as e:
                    print(f"广播处理错误: {e}")


# ============================================================
# 生命周期管理模块
# ============================================================

class ComponentState(Enum):
    """组件状态枚举"""
    CREATED = "created"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class LifecycleManager:
    """
    生命周期管理器
    
    负责组件的创建、初始化、运行、销毁
    """
    
    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._states: Dict[str, ComponentState] = {}
        self._hooks: Dict[str, List[Callable]] = {
            "on_create": [],
            "on_init": [],
            "on_start": [],
            "on_stop": [],
            "on_destroy": []
        }
    
    def register_component(self, name: str, component: Any) -> None:
        """
        注册组件
        
        Args:
            name: 组件名称
            component: 组件实例
        """
        self._components[name] = component
        self._states[name] = ComponentState.CREATED
        self._trigger_hook("on_create", name, component)
    
    def initialize(self, name: str) -> bool:
        """
        初始化组件
        
        Args:
            name: 组件名称
            
        Returns:
            是否成功初始化
        """
        if name not in self._components:
            return False
        
        self._states[name] = ComponentState.INITIALIZING
        
        try:
            component = self._components[name]
            if hasattr(component, 'initialize'):
                component.initialize()
            self._states[name] = ComponentState.RUNNING
            self._trigger_hook("on_init", name, component)
            return True
        except Exception as e:
            self._states[name] = ComponentState.ERROR
            print(f"组件初始化失败 {name}: {e}")
            return False
    
    def start(self, name: str) -> bool:
        """
        启动组件
        
        Args:
            name: 组件名称
            
        Returns:
            是否成功启动
        """
        if name not in self._components:
            return False
        
        try:
            component = self._components[name]
            if hasattr(component, 'start'):
                component.start()
            self._states[name] = ComponentState.RUNNING
            self._trigger_hook("on_start", name, component)
            return True
        except Exception as e:
            self._states[name] = ComponentState.ERROR
            print(f"组件启动失败 {name}: {e}")
            return False
    
    def stop(self, name: str) -> bool:
        """
        停止组件
        
        Args:
            name: 组件名称
            
        Returns:
            是否成功停止
        """
        if name not in self._components:
            return False
        
        self._states[name] = ComponentState.STOPPING
        
        try:
            component = self._components[name]
            if hasattr(component, 'stop'):
                component.stop()
            self._states[name] = ComponentState.STOPPED
            self._trigger_hook("on_stop", name, component)
            return True
        except Exception as e:
            self._states[name] = ComponentState.ERROR
            print(f"组件停止失败 {name}: {e}")
            return False
    
    def destroy(self, name: str) -> bool:
        """
        销毁组件
        
        Args:
            name: 组件名称
            
        Returns:
            是否成功销毁
        """
        if name not in self._components:
            return False
        
        try:
            component = self._components[name]
            if hasattr(component, 'destroy'):
                component.destroy()
            self._trigger_hook("on_destroy", name, component)
            del self._components[name]
            del self._states[name]
            return True
        except Exception as e:
            print(f"组件销毁失败 {name}: {e}")
            return False
    
    def get_state(self, name: str) -> Optional[ComponentState]:
        """获取组件状态"""
        return self._states.get(name)
    
    def register_hook(self, event: str, callback: Callable) -> None:
        """注册生命周期钩子"""
        if event in self._hooks:
            self._hooks[event].append(callback)
    
    def _trigger_hook(self, event: str, *args, **kwargs) -> None:
        """触发钩子"""
        for callback in self._hooks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"钩子执行错误 {event}: {e}")


# ============================================================
# 接口契约模块
# ============================================================

class IComponent(ABC):
    """
    组件接口契约
    
    所有组件必须实现此接口
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """初始化组件"""
        pass
    
    @abstractmethod
    def start(self) -> None:
        """启动组件"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止组件"""
        pass
    
    @abstractmethod
    def destroy(self) -> None:
        """销毁组件"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """组件名称"""
        pass
    
    @property
    @abstractmethod
    def state(self) -> ComponentState:
        """组件状态"""
        pass


class IMessageHandler(ABC):
    """
    消息处理器接口契约
    """
    
    @abstractmethod
    def handle(self, message: Message) -> Any:
        """
        处理消息
        
        Args:
            message: 消息对象
            
        Returns:
            处理结果
        """
        pass
    
    @abstractmethod
    def can_handle(self, message: Message) -> bool:
        """
        判断是否能处理此消息
        
        Args:
            message: 消息对象
            
        Returns:
            是否能处理
        """
        pass


class IPlugin(ABC):
    """
    插件接口契约
    
    序境扩展插件的标准接口
    """
    
    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """插件唯一标识"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """依赖插件列表"""
        pass
    
    @abstractmethod
    def install(self, core: 'NucleusCore') -> bool:
        """
        安装插件
        
        Args:
            core: 内核核心实例
            
        Returns:
            是否安装成功
        """
        pass
    
    @abstractmethod
    def uninstall(self, core: 'NucleusCore') -> bool:
        """
        卸载插件
        
        Args:
            core: 内核核心实例
            
        Returns:
            是否卸载成功
        """
        pass


# ============================================================
# 内核核心类
# ============================================================

class NucleusCore:
    """
    序境内核核心类
    
    这是序境3.0的核心引擎，负责：
    - 消息路由协调
    - 组件生命周期管理
    - 插件系统
    - 配置管理
    - 事件系统
    
    使用示例:
        core = NucleusCore()
        core.initialize()
        core.start()
        # ... 运行序境
        core.stop()
        core.destroy()
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化内核核心
        
        Args:
            config: 配置字典
        """
        self._config = config or {}
        self._core_id = str(uuid.uuid4())
        self._name = self._config.get("name", "序境3.0内核")
        self._version = "3.0.0-alpha"
        
        # 核心子系统
        self._router = MessageRouter()
        self._lifecycle = LifecycleManager()
        self._plugins: Dict[str, IPlugin] = {}
        self._services: Dict[str, Any] = {}
        
        # 状态
        self._state = ComponentState.CREATED
        self._start_time: Optional[datetime] = None
    
    @property
    def core_id(self) -> str:
        """内核唯一标识"""
        return self._core_id
    
    @property
    def name(self) -> str:
        """内核名称"""
        return self._name
    
    @property
    def version(self) -> str:
        """内核版本"""
        return self._version
    
    @property
    def state(self) -> ComponentState:
        """内核状态"""
        return self._state
    
    @property
    def router(self) -> MessageRouter:
        """获取消息路由器"""
        return self._router
    
    @property
    def lifecycle(self) -> LifecycleManager:
        """获取生命周期管理器"""
        return self._lifecycle
    
    # -------------------- 生命周期方法 --------------------
    
    def initialize(self) -> bool:
        """
        初始化内核
        
        Returns:
            是否成功初始化
        """
        if self._state != ComponentState.CREATED:
            print(f"内核已在运行状态: {self._state}")
            return False
        
        self._state = ComponentState.INITIALIZING
        
        try:
            # 初始化核心服务
            self._init_services()
            
            # 注册内置消息路由
            self._register_builtin_routes()
            
            self._state = ComponentState.RUNNING
            print(f"序境内核初始化完成: {self._name} v{self._version}")
            return True
            
        except Exception as e:
            self._state = ComponentState.ERROR
            print(f"内核初始化失败: {e}")
            return False
    
    def start(self) -> bool:
        """
        启动内核
        
        Returns:
            是否成功启动
        """
        if self._state != ComponentState.RUNNING:
            print(f"内核未就绪: {self._state}")
            return False
        
        self._start_time = datetime.now()
        
        # 启动所有已注册的服务
        for name in self._services:
            self._lifecycle.start(name)
        
        print(f"序境内核已启动")
        return True
    
    def stop(self) -> bool:
        """
        停止内核
        
        Returns:
            是否成功停止
        """
        if self._state != ComponentState.RUNNING:
            return False
        
        self._state = ComponentState.STOPPING
        
        # 停止所有服务
        for name in list(self._services.keys()):
            self._lifecycle.stop(name)
        
        self._state = ComponentState.STOPPED
        print(f"序境内核已停止")
        return True
    
    def destroy(self) -> bool:
        """
        销毁内核
        
        Returns:
            是否成功销毁
        """
        # 卸载所有插件
        for plugin_id in list(self._plugins.keys()):
            self.uninstall_plugin(plugin_id)
        
        # 销毁所有服务
        for name in list(self._services.keys()):
            self._lifecycle.destroy(name)
        
        self._services.clear()
        self._plugins.clear()
        
        self._state = ComponentState.STOPPED
        print(f"序境内核已销毁")
        return True
    
    # -------------------- 服务管理 --------------------
    
    def register_service(self, name: str, service: Any) -> bool:
        """
        注册服务
        
        Args:
            name: 服务名称
            service: 服务实例
            
        Returns:
            是否成功注册
        """
        if name in self._services:
            print(f"服务已存在: {name}")
            return False
        
        self._services[name] = service
        self._lifecycle.register_component(name, service)
        
        # 如果内核已在运行状态，自动初始化并启动
        if self._state == ComponentState.RUNNING:
            self._lifecycle.initialize(name)
            self._lifecycle.start(name)
        
        return True
    
    def get_service(self, name: str) -> Optional[Any]:
        """
        获取服务
        
        Args:
            name: 服务名称
            
        Returns:
            服务实例，不存在返回None
        """
        return self._services.get(name)
    
    def unregister_service(self, name: str) -> bool:
        """
        注销服务
        
        Args:
            name: 服务名称
            
        Returns:
            是否成功注销
        """
        if name not in self._services:
            return False
        
        self._lifecycle.destroy(name)
        del self._services[name]
        return True
    
    # -------------------- 插件系统 --------------------
    
    def install_plugin(self, plugin: IPlugin) -> bool:
        """
        安装插件
        
        Args:
            plugin: 插件实例
            
        Returns:
            是否成功安装
        """
        plugin_id = plugin.plugin_id
        
        if plugin_id in self._plugins:
            print(f"插件已安装: {plugin_id}")
            return False
        
        # 检查依赖
        for dep in plugin.dependencies:
            if dep not in self._plugins:
                print(f"缺少依赖插件: {dep}")
                return False
        
        # 安装插件
        if plugin.install(self):
            self._plugins[plugin_id] = plugin
            print(f"插件已安装: {plugin_id} v{plugin.version}")
            return True
        
        return False
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_id: 插件标识
            
        Returns:
            是否成功卸载
        """
        if plugin_id not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_id]
        
        if plugin.uninstall(self):
            del self._plugins[plugin_id]
            print(f"插件已卸载: {plugin_id}")
            return True
        
        return False
    
    def get_plugin(self, plugin_id: str) -> Optional[IPlugin]:
        """
        获取插件
        
        Args:
            plugin_id: 插件标识
            
        Returns:
            插件实例，不存在返回None
        """
        return self._plugins.get(plugin_id)
    
    # -------------------- 消息系统 --------------------
    
    def send_message(self, message: Message) -> bool:
        """
        发送消息
        
        Args:
            message: 消息对象
            
        Returns:
            是否成功发送
        """
        return self._router.route(message)
    
    def broadcast_message(self, message: Message) -> None:
        """
        广播消息
        
        Args:
            message: 消息对象
        """
        self._router.broadcast(message)
    
    def register_message_handler(self, message_type: str, handler: Callable[[Message], None]) -> None:
        """
        注册消息处理器
        
        Args:
            message_type: 消息类型
            handler: 处理函数
        """
        self._router.register_route(message_type, handler)
    
    # -------------------- 私有方法 --------------------
    
    def _init_services(self) -> None:
        """初始化内置服务"""
        # TODO: 根据配置初始化内置服务
        pass
    
    def _register_builtin_routes(self) -> None:
        """注册内置消息路由"""
        # 系统消息
        self._router.register_route("system", self._handle_system_message)
        # 组件消息
        self._router.register_route("component", self._handle_component_message)
        # 插件消息
        self._router.register_route("plugin", self._handle_plugin_message)
    
    def _handle_system_message(self, message: Message) -> None:
        """处理系统消息"""
        print(f"系统消息: {message.payload}")
    
    def _handle_component_message(self, message: Message) -> None:
        """处理组件消息"""
        print(f"组件消息: {message.source} -> {message.target}")
    
    def _handle_plugin_message(self, message: Message) -> None:
        """处理插件消息"""
        print(f"插件消息: {message.payload}")
    
    # -------------------- 工具方法 --------------------
    
    def get_uptime(self) -> Optional[float]:
        """
        获取运行时间（秒）
        
        Returns:
            运行时间，不在运行状态返回None
        """
        if self._start_time is None:
            return None
        return (datetime.now() - self._start_time).total_seconds()
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取内核状态
        
        Returns:
            状态字典
        """
        return {
            "core_id": self._core_id,
            "name": self._name,
            "version": self._version,
            "state": self._state.value,
            "uptime": self.get_uptime(),
            "services_count": len(self._services),
            "plugins_count": len(self._plugins)
        }
    
    def __repr__(self) -> str:
        return f"NucleusCore(name={self._name}, state={self._state.value})"


# ============================================================
# 导出
# ============================================================

__all__ = [
    # 枚举
    'MessagePriority',
    'ComponentState',
    
    # 接口
    'IComponent',
    'IMessageHandler',
    'IPlugin',
    
    # 核心类
    'Message',
    'MessageRouter',
    'LifecycleManager',
    'NucleusCore',
]
