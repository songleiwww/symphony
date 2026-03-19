# -*- coding: utf-8 -*-
"""
序境内核 - 模块注册机制
支持模块注册、发现、依赖管理
"""

import logging
from typing import Dict, Optional, Any, List, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ModuleType(Enum):
    """模块类型"""
    CORE = "core"           # 核心模块
    PLUGIN = "plugin"       # 插件模块
    EXTENSION = "extension" # 扩展模块
    ADAPTER = "adapter"     # 适配器


class ModuleState(Enum):
    """模块状态"""
    UNREGISTERED = "unregistered"
    REGISTERED = "registered"
    LOADED = "loaded"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class ModuleInfo:
    """模块信息"""
    name: str
    module_type: ModuleType
    class_name: str
    module_path: str
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    state: ModuleState = ModuleState.UNREGISTERED
    instance: Any = None
    metadata: Dict = field(default_factory=dict)


class ModuleRegistry:
    """
    模块注册中心
    管理所有内核模块的注册、发现、依赖
    """
    
    def __init__(self):
        self._modules: Dict[str, ModuleInfo] = {}
        self._hooks: Dict[str, List] = {
            "on_register": [],
            "on_load": [],
            "on_unload": [],
            "on_error": []
        }
    
    def register(
        self,
        name: str,
        module_type: ModuleType,
        class_name: str,
        module_path: str,
        version: str = "1.0.0",
        dependencies: List[str] = None,
        metadata: Dict = None
    ) -> bool:
        """
        注册模块
        
        参数:
            name: 模块名称
            module_type: 模块类型
            class_name: 类名
            module_path: 模块路径
            version: 版本号
            dependencies: 依赖列表
            metadata: 额外元数据
        
        返回:
            是否注册成功
        """
        if name in self._modules:
            logger.warning(f"Module {name} already registered, skipping")
            return False
        
        info = ModuleInfo(
            name=name,
            module_type=module_type,
            class_name=class_name,
            module_path=module_path,
            version=version,
            dependencies=dependencies or [],
            state=ModuleState.REGISTERED,
            metadata=metadata or {}
        )
        
        self._modules[name] = info
        self._trigger("on_register", info)
        logger.info(f"Registered module: {name} ({module_type.value})")
        return True
    
    def unregister(self, name: str) -> bool:
        """注销模块"""
        if name not in self._modules:
            return False
        
        info = self._modules[name]
        if info.state == ModuleState.LOADED:
            self._trigger("on_unload", info)
        
        del self._modules[name]
        logger.info(f"Unregistered module: {name}")
        return True
    
    def get(self, name: str) -> Optional[ModuleInfo]:
        """获取模块信息"""
        return self._modules.get(name)
    
    def get_instance(self, name: str) -> Optional[Any]:
        """获取模块实例"""
        info = self._modules.get(name)
        return info.instance if info else None
    
    def set_instance(self, name: str, instance: Any):
        """设置模块实例"""
        if name in self._modules:
            self._modules[name].instance = instance
            self._modules[name].state = ModuleState.LOADED
            self._trigger("on_load", self._modules[name])
    
    def list_by_type(self, module_type: ModuleType) -> List[ModuleInfo]:
        """按类型列出模块"""
        return [m for m in self._modules.values() if m.module_type == module_type]
    
    def list_loaded(self) -> List[ModuleInfo]:
        """列出已加载模块"""
        return [m for m in self._modules.values() if m.state == ModuleState.LOADED]
    
    def check_dependencies(self, name: str) -> Set[str]:
        """检查依赖，返回缺失的依赖"""
        info = self._modules.get(name)
        if not info:
            return set()
        
        missing = set()
        for dep in info.dependencies:
            dep_info = self._modules.get(dep)
            if not dep_info or dep_info.state != ModuleState.LOADED:
                missing.add(dep)
        
        return missing
    
    def load_order(self) -> List[str]:
        """计算模块加载顺序（按依赖排序）"""
        loaded = []
        remaining = set(self._modules.keys())
        
        while remaining:
            for name in list(remaining):
                info = self._modules[name]
                deps = set(info.dependencies)
                
                if deps.issubset(loaded):
                    loaded.append(name)
                    remaining.remove(name)
                    break
            else:
                # 无法解决依赖
                break
        
        return loaded
    
    def add_hook(self, event: str, callback):
        """添加钩子"""
        if event in self._hooks:
            self._hooks[event].append(callback)
    
    def _trigger(self, event: str, *args, **kwargs):
        """触发钩子"""
        for callback in self._hooks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Hook {event} error: {e}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = {
            "total": len(self._modules),
            "by_type": {},
            "by_state": {}
        }
        
        for m in self._modules.values():
            type_key = m.module_type.value
            state_key = m.state.value
            stats["by_type"][type_key] = stats["by_type"].get(type_key, 0) + 1
            stats["by_state"][state_key] = stats["by_state"].get(state_key, 0) + 1
        
        return stats


# 全局注册中心
_registry: Optional[ModuleRegistry] = None


def get_registry() -> ModuleRegistry:
    """获取全局注册中心"""
    global _registry
    if _registry is None:
        _registry = ModuleRegistry()
        _register_builtin_modules(_registry)
    return _registry


def _register_builtin_modules(registry: ModuleRegistry):
    """注册内置模块"""
    # 核心模块
    registry.register(
        name="scheduler",
        module_type=ModuleType.CORE,
        class_name="Scheduler",
        module_path="core.scheduler",
        version="3.3.0"
    )
    
    registry.register(
        name="load_balancer",
        module_type=ModuleType.CORE,
        class_name="LoadBalancer",
        module_path="core.load_balancer",
        version="3.3.0"
    )
    
    # 基础设施模块
    registry.register(
        name="database",
        module_type=ModuleType.CORE,
        class_name="ModelRepository",
        module_path="infra.database",
        version="3.3.0"
    )
    
    registry.register(
        name="api_client",
        module_type=ModuleType.CORE,
        class_name="APIClient",
        module_path="infra.api_client",
        version="3.3.0"
    )
    
    # 规则引擎
    registry.register(
        name="rule_engine",
        module_type=ModuleType.CORE,
        class_name="RuleEngine",
        module_path="rules.engine",
        version="3.3.0"
    )
    
    # 插件模块
    registry.register(
        name="plugin_manager",
        module_type=ModuleType.PLUGIN,
        class_name="PluginManager",
        module_path="core.plugin",
        version="3.3.0"
    )
