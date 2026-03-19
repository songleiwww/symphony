# -*- coding: utf-8 -*-
"""
序境内核 - 微内核架构核心
基于序境系统总则构建

架构设计:
1. 核心模块 (Core): 仅包含调度、规则、API调用最基本功能
2. 插件系统 (Plugin): 扩展接口标准化，支持动态加载
3. 统一入口 (Integration): 统一的初始化和访问接口
4. 热更新 (HotReload): 配置和规则运行时更新
5. 版本兼容 (Compat): 向后兼容处理

版本: 3.3.0
"""

import os
import sys
from typing import Optional, Dict, Any, List

# 内核根路径
KERNEL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_PATH = os.path.join(KERNEL_ROOT, "Kernel", "core")
PLUGIN_PATH = os.path.join(KERNEL_ROOT, "Kernel", "core", "plugin")

# 版本信息
VERSION = "3.3.0"
VERSION_INFO = {
    "major": 3,
    "minor": 3,
    "patch": 0,
    "release": "micro-kernel",
    "build_date": "2026-03-19"
}


def get_version() -> str:
    """获取内核版本"""
    return VERSION


def get_version_info() -> Dict[str, Any]:
    """获取详细版本信息"""
    return VERSION_INFO.copy()


# 核心模块导出
from .scheduler import Scheduler, ModelConfig, ModelStatus, SchedulerConfig, get_scheduler
from .load_balancer import LoadBalancer, LoadBalanceAlgorithm, get_balancer
from .loader import MicroKernelLoader, get_loader
from .registry import ModuleRegistry, get_registry
from .plugin import PluginManager, PluginInterface, PluginLifecycle
from .compat import VersionCompat, check_compat
from .hot_reload import HotReloadManager, get_hot_reload_manager

__all__ = [
    # 版本信息
    "VERSION",
    "VERSION_INFO",
    "get_version",
    "get_version_info",
    
    # 核心调度
    "Scheduler",
    "ModelConfig", 
    "ModelStatus",
    "SchedulerConfig",
    "get_scheduler",
    
    # 负载均衡
    "LoadBalancer",
    "LoadBalanceAlgorithm",
    "get_balancer",
    
    # 微内核加载器
    "MicroKernelLoader",
    "get_loader",
    
    # 模块注册
    "ModuleRegistry",
    "get_registry",
    
    # 插件系统
    "PluginManager",
    "PluginInterface",
    "PluginLifecycle",
    
    # 版本兼容
    "VersionCompat",
    "check_compat",
    
    # 热更新
    "HotReloadManager",
    "get_hot_reload_manager",
]


class MicroKernel:
    """
    序境微内核
    精简核心，仅包含最基本的功能
    其他功能通过插件扩展
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(KERNEL_ROOT, "data", "symphony.db")
        self._initialized = False
        self._scheduler: Optional[Scheduler] = None
        self._balancer: Optional[LoadBalancer] = None
        self._loader: Optional[MicroKernelLoader] = None
        self._registry: Optional[ModuleRegistry] = None
        self._plugin_manager: Optional[PluginManager] = None
    
    def initialize(self, load_plugins: bool = True):
        """初始化内核"""
        if self._initialized:
            return
        
        # 1. 初始化核心模块
        self._scheduler = get_scheduler()
        self._balancer = get_balancer()
        self._loader = get_loader()
        self._registry = get_registry()
        
        # 2. 加载模型配置
        self._load_models()
        
        # 3. 初始化插件系统
        if load_plugins:
            self._plugin_manager = PluginManager()
            self._plugin_manager.discover_plugins()
            self._plugin_manager.load_all()
        
        self._initialized = True
        print(f"序境微内核 {VERSION} 初始化完成")
    
    def _load_models(self):
        """加载模型配置"""
        from ..infra.database import ModelRepository
        repo = ModelRepository(self.db_path)
        models = repo.get_all_enabled()
        
        for m in models:
            model = ModelConfig(
                model_id=str(m['id']),
                model_name=m['model_name'],
                provider=m['provider'],
                api_url=m['api_url'],
                api_key=m['api_key']
            )
            self._scheduler.register_model(model)
    
    @property
    def scheduler(self) -> Scheduler:
        """获取调度器"""
        return self._scheduler
    
    @property
    def balancer(self) -> LoadBalancer:
        """获取负载均衡器"""
        return self._balancer
    
    @property
    def plugin_manager(self) -> PluginManager:
        """获取插件管理器"""
        return self._plugin_manager
    
    def dispatch(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """调度请求"""
        if not self._initialized:
            self.initialize()
        
        # 选择模型
        model = self._scheduler.select_model()
        if not model:
            return {"success": False, "error": "无可用模型"}
        
        # 调用API
        from ..infra.api_client import get_client
        client = get_client()
        result = client.call(
            api_url=model.api_url,
            api_key=model.api_key,
            model=model.model_name,
            prompt=prompt,
            **kwargs
        )
        
        # 记录结果
        if result.get("success"):
            self._scheduler.on_success(model, result.get("total_tokens", 0), 0)
        else:
            self._scheduler.on_fail(model)
        
        return result
    
    def reload(self):
        """热重载"""
        self._load_models()
        if self._plugin_manager:
            self._plugin_manager.reload_all()


# 全局内核实例
_micro_kernel: Optional[MicroKernel] = None


def get_micro_kernel(db_path: str = None) -> MicroKernel:
    """获取微内核实例"""
    global _micro_kernel
    if _micro_kernel is None:
        _micro_kernel = MicroKernel(db_path)
    return _micro_kernel
