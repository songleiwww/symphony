# -*- coding: utf-8 -*-
"""
序境内核 - 插件系统
标准化插件接口，支持动态加载、生命周期管理
"""

import os
import logging
import importlib
from typing import Dict, Optional, Any, List, Type
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class PluginLifecycle(Enum):
    """插件生命周期"""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    STOPPED = "stopped"
    FAILED = "failed"
    UNLOADED = "unloaded"


class PluginPriority(Enum):
    """插件优先级"""
    CRITICAL = 0    # 关键插件
    HIGH = 10       # 高优先级
    NORMAL = 50     # 普通优先级
    LOW = 90        # 低优先级
    DISABLED = 100  # 已禁用


@dataclass
class PluginMetadata:
    """插件元数据"""
    name: str
    version: str
    author: str = ""
    description: str = ""
    dependencies: List[str] = None
    priority: PluginPriority = PluginPriority.NORMAL
    lifecycle: PluginLifecycle = PluginLifecycle.DISCOVERED
    config: Dict = None


class PluginInterface(ABC):
    """
    插件接口基类
    所有插件必须实现此接口
    """
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """获取插件元数据"""
        pass
    
    @abstractmethod
    def initialize(self, kernel: Any) -> bool:
        """
        初始化插件
        
        参数:
            kernel: 内核实例
        
        返回:
            是否初始化成功
        """
        pass
    
    @abstractmethod
    def activate(self):
        """激活插件"""
        pass
    
    @abstractmethod
    def deactivate(self):
        """停用插件"""
        pass
    
    def on_kernel_event(self, event: str, data: Any = None):
        """处理内核事件"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """获取插件能力列表"""
        return []


class PluginManager:
    """
    插件管理器
    负责插件的发现、加载、生命周期管理
    """
    
    def __init__(self, plugin_dir: str = None):
        if plugin_dir is None:
            plugin_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "core", "plugin"
            )
        self.plugin_dir = plugin_dir
        self._plugins: Dict[str, Type[PluginInterface]] = {}
        self._instances: Dict[str, PluginInterface] = {}
        self._metadata: Dict[str, PluginMetadata] = {}
        self._kernel: Any = None
    
    def set_kernel(self, kernel: Any):
        """设置内核实例"""
        self._kernel = kernel
    
    def discover_plugins(self):
        """发现插件"""
        if not os.path.exists(self.plugin_dir):
            logger.info(f"Plugin directory not found: {self.plugin_dir}")
            return
        
        # 扫描插件目录
        for filename in os.listdir(self.plugin_dir):
            if filename.startswith("_") or filename.startswith("."):
                continue
            
            if filename.endswith(".py"):
                module_name = filename[:-3]
            elif os.path.isdir(os.path.join(self.plugin_dir, filename)):
                module_name = filename
            else:
                continue
            
            self._discover_plugin(module_name)
    
    def _discover_plugin(self, module_name: str):
        """发现单个插件"""
        try:
            full_name = f"core.plugin.{module_name}"
            module = importlib.import_module(full_name)
            
            # 查找插件类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, PluginInterface) and attr != PluginInterface:
                    self._plugins[module_name] = attr
                    logger.info(f"Discovered plugin: {module_name}")
                    break
        except Exception as e:
            logger.error(f"Failed to discover plugin {module_name}: {e}")
    
    def load_plugin(self, name: str) -> bool:
        """加载插件"""
        if name in self._instances:
            logger.warning(f"Plugin {name} already loaded")
            return True
        
        plugin_class = self._plugins.get(name)
        if not plugin_class:
            logger.error(f"Plugin not found: {name}")
            return False
        
        try:
            # 实例化插件
            plugin = plugin_class()
            metadata = plugin.get_metadata()
            self._metadata[name] = metadata
            
            # 初始化插件
            if self._kernel:
                if not plugin.initialize(self._kernel):
                    metadata.lifecycle = PluginLifecycle.FAILED
                    logger.error(f"Plugin {name} initialization failed")
                    return False
            
            # 激活插件
            plugin.activate()
            metadata.lifecycle = PluginLifecycle.ACTIVE
            
            # 保存实例
            self._instances[name] = plugin
            logger.info(f"Loaded plugin: {name} v{metadata.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {name}: {e}")
            if name in self._metadata:
                self._metadata[name].lifecycle = PluginLifecycle.FAILED
            return False
    
    def unload_plugin(self, name: str) -> bool:
        """卸载插件"""
        if name not in self._instances:
            return False
        
        try:
            plugin = self._instances[name]
            plugin.deactivate()
            
            if name in self._metadata:
                self._metadata[name].lifecycle = PluginLifecycle.UNLOADED
            
            del self._instances[name]
            logger.info(f"Unloaded plugin: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to unload plugin {name}: {e}")
            return False
    
    def load_all(self):
        """加载所有插件"""
        # 按优先级排序
        sorted_plugins = sorted(
            self._plugins.items(),
            key=lambda x: self._get_priority(x[0])
        )
        
        for name, _ in sorted_plugins:
            if self._get_priority(name) < PluginPriority.DISABLED.value:
                self.load_plugin(name)
    
    def reload_all(self):
        """重新加载所有插件"""
        for name in list(self._instances.keys()):
            self.unload_plugin(name)
        
        self._plugins.clear()
        self.discover_plugins()
        self.load_all()
    
    def _get_priority(self, name: str) -> int:
        """获取插件优先级"""
        if name in self._metadata:
            return self._metadata[name].priority.value
        return PluginPriority.NORMAL.value
    
    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """获取插件实例"""
        return self._instances.get(name)
    
    def list_plugins(self) -> List[Dict]:
        """列出所有插件"""
        result = []
        for name, metadata in self._metadata.items():
            result.append({
                "name": name,
                "version": metadata.version,
                "author": metadata.author,
                "description": metadata.description,
                "lifecycle": metadata.lifecycle.value,
                "priority": metadata.priority.value,
                "loaded": name in self._instances
            })
        return result
    
    def get_capabilities(self) -> Dict[str, List[str]]:
        """获取所有插件能力"""
        capabilities = {}
        for name, plugin in self._instances.items():
            capabilities[name] = plugin.get_capabilities()
        return capabilities


# 示例：内置日志插件
class LoggingPlugin(PluginInterface):
    """日志插件"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="logging",
            version="1.0.0",
            author="Xujing",
            description="内置日志插件",
            priority=PluginPriority.CRITICAL
        )
    
    def initialize(self, kernel) -> bool:
        return True
    
    def activate(self):
        logger.info("Logging plugin activated")
    
    def deactivate(self):
        logger.info("Logging plugin deactivated")


class MetricsPlugin(PluginInterface):
    """指标收集插件"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="metrics",
            version="1.0.0",
            author="Xujing",
            description="指标收集插件",
            priority=PluginPriority.HIGH
        )
    
    def initialize(self, kernel) -> bool:
        return True
    
    def activate(self):
        logger.info("Metrics plugin activated")
    
    def deactivate(self):
        logger.info("Metrics plugin deactivated")
    
    def get_capabilities(self) -> List[str]:
        return ["collect_metrics", "export_prometheus", "export_statsd"]
