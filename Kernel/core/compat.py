# -*- coding: utf-8 -*-
"""
序境内核 - 版本兼容层
处理版本检测、兼容性检查、自动迁移
"""

import logging
from typing import Dict, Optional, Tuple, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CompatLevel(Enum):
    """兼容级别"""
    FULL = "full"           # 完全兼容
    PARTIAL = "partial"     # 部分兼容
    COMPATIBLE = "compatible"  # 兼容但有警告
    INCOMPATIBLE = "incompatible"  # 不兼容


@dataclass
class Version:
    """版本号"""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __lt__(self, other) -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.patch < other.patch
    
    def __le__(self, other) -> bool:
        return self == other or self < other
    
    def __gt__(self, other) -> bool:
        return not self <= other
    
    def __ge__(self, other) -> bool:
        return not self < other
    
    @classmethod
    def parse(cls, version_str: str) -> "Version":
        """解析版本字符串"""
        parts = version_str.split(".")
        return cls(
            major=int(parts[0]) if len(parts) > 0 else 0,
            minor=int(parts[1]) if len(parts) > 1 else 0,
            patch=int(parts[2]) if len(parts) > 2 else 0
        )


@dataclass
class CompatRule:
    """兼容规则"""
    from_version: str
    to_version: str
    level: CompatLevel
    message: str
    migration: str = ""


class VersionCompat:
    """
    版本兼容性检查器
    """
    
    # 内核版本历史
    VERSION_HISTORY = [
        "3.0.0",  # 初始版本
        "3.1.0",  # 添加调度器
        "3.2.0",  # 添加规则引擎
        "3.3.0",  # 微内核版本
    ]
    
    # 兼容规则
    COMPAT_RULES = [
        # 3.2.0 -> 3.3.0
        CompatRule(
            from_version="3.2.0",
            to_version="3.3.0",
            level=CompatLevel.FULL,
            message="完全兼容",
            migration=""
        ),
    ]
    
    def __init__(self, current_version: str = "3.3.0"):
        self.current_version = Version.parse(current_version)
    
    def check(self, target_version: str) -> Tuple[CompatLevel, str]:
        """
        检查兼容性
        
        返回:
            (兼容级别, 消息)
        """
        target = Version.parse(target_version)
        
        # 同一版本完全兼容
        if target == self.current_version:
            return CompatLevel.FULL, "相同版本"
        
        # 主版本号不兼容
        if target.major != self.current_version.major:
            return CompatLevel.INCOMPATIBLE, f"主版本不兼容: {target.major} != {self.current_version.major}"
        
        # 查找兼容规则
        for rule in self.COMPAT_RULES:
            if Version.parse(rule.from_version) <= target <= Version.parse(rule.to_version):
                return rule.level, rule.message
        
        # 默认兼容
        if target.minor <= self.current_version.minor:
            return CompatLevel.PARTIAL, "旧版本，可能缺少新功能"
        else:
            return CompatLevel.COMPATIBLE, "新版本，部分API可能有变化"
    
    def is_compatible(self, target_version: str) -> bool:
        """检查是否兼容"""
        level, _ = self.check(target_version)
        return level in [CompatLevel.FULL, CompatLevel.PARTIAL, CompatLevel.COMPATIBLE]
    
    def get_migration_guide(self, from_version: str, to_version: str) -> str:
        """获取迁移指南"""
        for rule in self.COMPAT_RULES:
            if rule.from_version == from_version and rule.to_version == to_version:
                return rule.migration
        return "无特殊迁移要求"
    
    def check_module_compat(self, module_name: str, module_version: str) -> Tuple[bool, str]:
        """检查模块兼容性"""
        # 模块版本映射
        module_map = {
            "scheduler": "3.3.0",
            "load_balancer": "3.3.0",
            "database": "3.3.0",
            "api_client": "3.3.0",
            "rule_engine": "3.3.0",
        }
        
        expected = module_map.get(module_name)
        if not expected:
            return True, "未知模块"
        
        level, msg = self.check(module_version)
        return level != CompatLevel.INCOMPATIBLE, msg
    
    def get_deprecated_features(self, version: str) -> List[str]:
        """获取废弃功能列表"""
        deprecated = {
            "3.3.0": [
                "dispatcher_multiprovider (请使用 core.scheduler)",
                "direct_api_call (请使用 core.api_client)"
            ]
        }
        return deprecated.get(version, [])


# 全局兼容性检查器
_compat: Optional[VersionCompat] = None


def check_compat(target_version: str) -> Tuple[CompatLevel, str]:
    """检查兼容性"""
    global _compat
    if _compat is None:
        _compat = VersionCompat()
    return _compat.check(target_version)


def get_compat() -> VersionCompat:
    """获取兼容性检查器"""
    global _compat
    if _compat is None:
        _compat = VersionCompat()
    return _compat
