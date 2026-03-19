# -*- coding: utf-8 -*-
"""
序境系统 - 统一模块加载器
按需动态加载模块，支持模块依赖管理
"""

import importlib
import os
import sys
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ModuleLoader:
    """
    统一模块加载器
    实现按需加载、延迟加载、模块缓存
    """

    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_path = base_path
        self.modules = {}  # 已加载模块缓存
        self.module_manifest = self._scan_modules()

    def _scan_modules(self) -> Dict[str, Dict]:
        """扫描可用模块"""
        manifest = {
            "core": {
                "description": "核心调度模块",
                "required": True,
                "modules": ["scheduler", "load_balancer"]
            },
            "infra": {
                "description": "基础设施模块",
                "required": True,
                "modules": ["database", "api_client", "model_registry"]
            },
            "rules": {
                "description": "规则引擎模块",
                "required": True,
                "modules": ["engine", "hot_reload", "self_adaptive"]
            },
            "monitor": {
                "description": "监控模块",
                "required": True,
                "modules": ["monitor", "health_checker", "fault_detector", "self_healer"]
            },
            "logs": {
                "description": "日志模块",
                "required": True,
                "modules": ["logger"]
            },
            "multi_agent": {
                "description": "多Agent协作模块",
                "required": False,
                "modules": ["xujing_multi_agent", "detect_then_team"]
            },
            "health": {
                "description": "健康检查模块",
                "required": False,
                "modules": ["kernel_health"]
            },
            "skills": {
                "description": "技能模块",
                "required": False,
                "modules": ["takeover_skill"]
            },
            "progress": {
                "description": "进度反馈模块",
                "required": False,
                "modules": ["realtime_progress"]
            },
            "evolution": {
                "description": "自进化模块",
                "required": False,
                "modules": ["self_evolver", "lifecycle_manager", "memory_system_v2"]
            }
        }

        return manifest

    def load_module(self, module_name: str, package: str = None) -> Any:
        """加载指定模块"""
        if module_name in self.modules:
            return self.modules[module_name]

        # 查找模块所在目录
        for dir_name, info in self.module_manifest.items():
            if module_name in info["modules"]:
                full_name = f"{dir_name}.{module_name}"
                break
        else:
            # 直接导入
            full_name = module_name

        try:
            if package:
                full_name = f"{package}.{module_name}"
            
            # 动态导入
            module = importlib.import_module(full_name)
            self.modules[module_name] = module
            logger.info(f"Loaded module: {full_name}")
            return module

        except ImportError as e:
            logger.error(f"Failed to load module {full_name}: {e}")
            return None

    def load_required_modules(self) -> Dict[str, Any]:
        """加载所有必需模块"""
        loaded = {}
        
        for dir_name, info in self.module_manifest.items():
            if info["required"]:
                for mod_name in info["modules"]:
                    mod = self.load_module(mod_name, dir_name)
                    if mod:
                        loaded[mod_name] = mod
        
        return loaded

    def load_optional_modules(self, module_names: list = None) -> Dict[str, Any]:
        """加载可选模块"""
        loaded = {}
        
        if module_names is None:
            # 加载所有非必需模块
            for dir_name, info in self.module_manifest.items():
                if not info["required"]:
                    for mod_name in info["modules"]:
                        mod = self.load_module(mod_name, dir_name)
                        if mod:
                            loaded[mod_name] = mod
        else:
            # 加载指定模块
            for name in module_names:
                mod = self.load_module(name)
                if mod:
                    loaded[name] = mod
        
        return loaded

    def get_module_info(self) -> Dict:
        """获取模块信息"""
        info = {}
        for dir_name, dir_info in self.module_manifest.items():
            info[dir_name] = {
                "description": dir_info["description"],
                "required": dir_info["required"],
                "modules": dir_info["modules"],
                "loaded": any(m in self.modules for m in dir_info["modules"])
            }
        return info

    def unload_module(self, module_name: str):
        """卸载模块"""
        if module_name in self.modules:
            del self.modules[module_name]
            logger.info(f"Unloaded module: {module_name}")


# 全局加载器
_loader = None

def get_module_loader(base_path: str = None) -> ModuleLoader:
    """获取全局模块加载器"""
    global _loader
    if _loader is None:
        _loader = ModuleLoader(base_path)
    return _loader


def lazy_load(module_name: str, package: str = None):
    """
    延迟加载装饰器
    用于类或函数的延迟加载
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            loader = get_module_loader()
            mod = loader.load_module(module_name, package)
            return func(mod, *args, **kwargs)
        return wrapper
    return decorator


# 测试
if __name__ == '__main__':
    print('=== Module Loader Test ===\n')

    loader = get_module_loader()

    # 查看模块信息
    info = loader.get_module_info()
    print('Module Manifest:')
    for name, data in info.items():
        status = '✓' if data['loaded'] else '○'
        req = '[必需]' if data['required'] else '[可选]'
        print(f'  {status} {name} {req}')
        print(f'      {data["description"]}')

    print('\n--- Loading Required ---')
    loaded = loader.load_required_modules()
    print(f'Loaded {len(loaded)} required modules')
