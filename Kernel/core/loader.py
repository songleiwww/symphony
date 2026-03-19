# -*- coding: utf-8 -*-
"""
序境内核 - 微内核动态加载器
支持模块按需加载、延迟加载、热更新
"""

import importlib
import os
import sys
import logging
from typing import Dict, Optional, Any, List, Type
from pathlib import Path

logger = logging.getLogger(__name__)


class MicroKernelLoader:
    """
    微内核动态加载器
    实现模块的动态加载、缓存、热更新
    
    P2修复: 使用 registry 管理模块状态，避免双重缓存
    """
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_path = base_path
        self._modules: Dict[str, Any] = {}  # 仅缓存模块实例
        self._module_mtime: Dict[str, float] = {}  # 文件修改时间
        
        # P2修复: 统一使用 registry 管理模块元数据
        self._registry = None  # 延迟加载
        
        self._manifest = self._build_manifest()
    
    @property
    def registry(self):
        """延迟加载 registry"""
        if self._registry is None:
            try:
                from core.registry import ModuleRegistry, ModuleType, ModuleState
                self._registry = ModuleRegistry()
                logger.info("模块注册中心已关联")
            except Exception as e:
                logger.warning(f"无法加载 registry: {e}")
        return self._registry
    
    def _build_manifest(self) -> Dict[str, Dict]:
        """构建模块清单"""
        return {
            "core": {
                "path": "core",
                "required": True,
                "modules": {
                    "scheduler": "Scheduler",
                    "load_balancer": "LoadBalancer"
                }
            },
            "infra": {
                "path": "infra",
                "required": True,
                "modules": {
                    "database": "ModelRepository",
                    "api_client": "APIClient",
                    "model_registry": "ModelRegistry"
                }
            },
            "rules": {
                "path": "rules",
                "required": True,
                "modules": {
                    "engine": "RuleEngine"
                }
            },
            "monitor": {
                "path": "monitor",
                "required": False,
                "modules": {
                    "monitor": "Monitor",
                    "health_checker": "HealthChecker"
                }
            },
            "logs": {
                "path": "logs",
                "required": True,
                "modules": {
                    "logger": "XujingLogger"
                }
            },
            "dispatcher": {
                "path": ".",
                "required": True,
                "modules": {
                    "dispatcher_multiprovider": "MultiProviderDispatcher",
                    "dispatcher_evolution": "EvolutionDispatcher"
                }
            },
            "session": {
                "path": "session",
                "required": False,
                "modules": {
                    "task_manager": "TaskManager",
                    "session_manager": "SessionManager"
                }
            },
            "progress": {
                "path": "progress",
                "required": False,
                "modules": {
                    "realtime_progress": "MultiModelExecutorWithProgress"
                }
            },
            "evolution": {
                "path": "evolution",
                "required": False,
                "modules": {
                    "self_evolver": "SelfEvolver"
                }
            }
        }
    
    def load_module(self, module_name: str, package: str = None) -> Optional[Any]:
        """加载指定模块"""
        # 检查缓存
        if module_name in self._modules:
            # 检查是否需要热更新
            if self._needs_reload(module_name):
                self._reload_module(module_name)
            return self._modules[module_name]
        
        # 查找模块路径
        full_path = self._find_module_path(module_name, package)
        if not full_path:
            logger.warning(f"Module not found: {module_name}")
            return None
        
        try:
            # 动态导入
            module = importlib.import_module(full_path)
            self._modules[module_name] = module
            self._module_mtime[module_name] = os.path.getmtime(
                module.__file__ if hasattr(module, '__file__') else __file__
            )
            logger.info(f"Loaded module: {full_path}")
            return module
        except ImportError as e:
            logger.error(f"Failed to load module {full_path}: {e}")
            return None
    
    def _find_module_path(self, module_name: str, package: str = None) -> Optional[str]:
        """查找模块路径"""
        if package:
            return f"{package}.{module_name}"
        
        # 在清单中查找
        for dir_name, info in self._manifest.items():
            if module_name in info.get("modules", {}):
                if info["path"] == ".":
                    return module_name
                return f"{info['path']}.{module_name}"
        
        # 直接导入尝试
        return module_name
    
    def _needs_reload(self, module_name: str) -> bool:
        """检查模块是否需要热更新"""
        if module_name not in self._module_mtime:
            return False
        
        try:
            module = self._modules.get(module_name)
            if module and hasattr(module, '__file__'):
                mtime = os.path.getmtime(module.__file__)
                return mtime > self._module_mtime[module_name]
        except Exception:
            pass
        return False
    
    def _reload_module(self, module_name: str):
        """热更新模块"""
        try:
            if module_name in self._modules:
                module = self._modules[module_name]
                if hasattr(module, '__file__'):
                    importlib.reload(module)
                    self._module_mtime[module_name] = os.path.getmtime(module.__file__)
                    logger.info(f"Reloaded module: {module_name}")
        except Exception as e:
            logger.error(f"Failed to reload module {module_name}: {e}")
    
    def load_required(self) -> Dict[str, Any]:
        """加载所有必需模块"""
        loaded = {}
        for dir_name, info in self._manifest.items():
            if info.get("required", False):
                for mod_name in info.get("modules", {}).keys():
                    mod = self.load_module(mod_name, info["path"] if info["path"] != "." else None)
                    if mod:
                        loaded[mod_name] = mod
        return loaded
    
    def load_optional(self, module_names: List[str] = None) -> Dict[str, Any]:
        """加载可选模块"""
        loaded = {}
        
        if module_names is None:
            # 加载所有非必需模块
            for dir_name, info in self._manifest.items():
                if not info.get("required", False):
                    for mod_name in info.get("modules", {}).keys():
                        mod = self.load_module(mod_name, info["path"] if info["path"] != "." else None)
                        if mod:
                            loaded[mod_name] = mod
        else:
            for name in module_names:
                mod = self.load_module(name)
                if mod:
                    loaded[name] = mod
        
        return loaded
    
    def unload_module(self, module_name: str):
        """卸载模块"""
        if module_name in self._modules:
            del self._modules[module_name]
        if module_name in self._module_mtime:
            del self._module_mtime[module_name]
        logger.info(f"Unloaded module: {module_name}")
    
    def get_loaded_modules(self) -> List[str]:
        """获取已加载模块列表"""
        return list(self._modules.keys())
    
    def get_module_info(self) -> Dict[str, Dict]:
        """获取模块信息"""
        return self._manifest.copy()


# 全局加载器
_loader: Optional[MicroKernelLoader] = None


def get_loader(base_path: str = None) -> MicroKernelLoader:
    """获取全局加载器"""
    global _loader
    if _loader is None:
        _loader = MicroKernelLoader(base_path)
    return _loader
