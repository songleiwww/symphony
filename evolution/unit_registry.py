#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境3.0 单元注册中心 (Unit Registry)
=====================================
提供模块单元的注册、发现、版本管理和生命周期控制。

作者: 少府监·智囊博士 沈星衍
版本: 3.0.0
"""

import json
import os
import re
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from copy import deepcopy

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnitState(Enum):
    """单元状态枚举"""
    DISCOVERED = auto()    # 已发现（扫描到但未加载）
    LOADED = auto()         # 已加载
    INITIALIZED = auto()    # 已初始化
    ACTIVE = auto()         # 活跃运行中
    SUSPENDED = auto()      # 已暂停
    UNLOADED = auto()       # 已卸载
    ERROR = auto()          # 错误状态
    DEPRECATED = auto()     # 已弃用


class UnitType(Enum):
    """单元类型枚举"""
    CORE = auto()           # 核心单元
    MODULE = auto()         # 功能模块
    PLUGIN = auto()         # 插件单元
    EXTENSION = auto()      # 扩展单元
    SERVICE = auto()        # 服务单元
    ADAPTER = auto()        # 适配器单元


@dataclass
class UnitManifest:
    """
    单元描述文件 (Unit Manifest)
    
    每个模块单元必须包含一个 manifest.json 文件来描述其元数据。
    """
    # 必需字段
    unit_id: str                    # 单元唯一标识符 (格式: namespace.name)
    name: str                        # 单元显示名称
    version: str                     # 语义化版本号 (semver)
    entry_point: str                # 入口文件路径
    
    # 可选字段
    description: str = ""            # 单元描述
    author: str = ""                 # 作者
    license: str = ""                # 许可证
    homepage: str = ""               # 主页URL
    repository: str = ""             # 代码仓库URL
    
    # 类型与分类
    unit_type: UnitType = UnitType.MODULE
    tags: List[str] = field(default_factory=list)
    category: str = ""               # 分类
    
    # 依赖关系
    dependencies: Dict[str, str] = field(default_factory=dict)  # {unit_id: version_spec}
    peer_dependencies: Dict[str, str] = field(default_factory=dict)
    optional_dependencies: Dict[str, str] = field(default_factory=dict)
    
    # 运行时配置
    config_schema: Dict[str, Any] = field(default_factory=dict)
    default_config: Dict[str, Any] = field(default_factory=dict)
    
    # 能力声明
    capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    
    # 生命周期钩子
    hooks: Dict[str, str] = field(default_factory=dict)  # {hook_name: handler_path}
    
    # 元数据
    manifest_version: str = "3.0"
    created_at: str = ""
    updated_at: str = ""
    checksum: str = ""                # manifest文件校验和
    
    # 加载控制
    priority: int = 100              # 加载优先级 (越小越先加载)
    lazy_load: bool = False          # 是否延迟加载
    singleton: bool = True           # 是否单例模式
    
    # 资源
    assets: List[str] = field(default_factory=list)
    resources: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnitManifest':
        """从字典创建单元清单"""
        # 转换 unit_type 字符串为枚举
        if 'unit_type' in data:
            if isinstance(data['unit_type'], str):
                data['unit_type'] = UnitType[data['unit_type'].upper()]
        
        # 转换列表类型字段
        for field_name in ['tags', 'capabilities', 'permissions', 'assets']:
            if field_name in data and isinstance(data[field_name], str):
                data[field_name] = [item.strip() for item in data[field_name].split(',')]
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 转换枚举为字符串
        data['unit_type'] = self.unit_type.name
        return data
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        验证清单有效性
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # 必需字段检查
        if not self.unit_id or not re.match(r'^[a-zA-Z0-9_.-]+$', self.unit_id):
            errors.append("unit_id 必须是有效的标识符 (字母、数字、点、下划线、连字符)")
        
        if not self.name:
            errors.append("name 不能为空")
        
        if not self.version or not self._validate_version(self.version):
            errors.append("version 必须是有效的语义化版本号 (如 1.0.0)")
        
        if not self.entry_point:
            errors.append("entry_point 不能为空")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_version(version: str) -> bool:
        """验证语义化版本号"""
        return bool(re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$', version))
    
    def compute_checksum(self, content: str) -> str:
        """计算内容校验和"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]


@dataclass
class UnitMetadata:
    """运行时单元元数据"""
    unit_id: str
    manifest: UnitManifest
    state: UnitState = UnitState.DISCOVERED
    
    # 路径信息
    base_path: str = ""
    manifest_path: str = ""
    
    # 运行时信息
    instance: Any = None
    loaded_at: str = ""
    last_active: str = ""
    error_message: str = ""
    
    # 统计信息
    load_count: int = 0
    error_count: int = 0
    
    def transition_to(self, new_state: UnitState, error: str = "") -> bool:
        """
        状态转换
        
        Args:
            new_state: 目标状态
            error: 错误信息（如果转换到错误状态）
            
        Returns:
            是否转换成功
        """
        valid_transitions = {
            UnitState.DISCOVERED: [UnitState.LOADED, UnitState.ERROR],
            UnitState.LOADED: [UnitState.INITIALIZED, UnitState.UNLOADED, UnitState.ERROR],
            UnitState.INITIALIZED: [UnitState.ACTIVE, UnitState.SUSPENDED, UnitState.UNLOADED, UnitState.ERROR],
            UnitState.ACTIVE: [UnitState.SUSPENDED, UnitState.ERROR],
            UnitState.SUSPENDED: [UnitState.ACTIVE, UnitState.UNLOADED],
            UnitState.UNLOADED: [UnitState.LOADED],
            UnitState.ERROR: [UnitState.LOADED, UnitState.DEPRECATED],
            UnitState.DEPRECATED: [],
        }
        
        if new_state in valid_transitions.get(self.state, []):
            self.state = new_state
            self.last_active = datetime.now().isoformat()
            
            if error:
                self.error_message = error
                self.error_count += 1
            
            return True
        
        logger.warning(f"无效的状态转换: {self.unit_id} from {self.state.name} to {new_state.name}")
        return False


class UnitRegistry:
    """
    单元注册中心
    
    负责模块单元的注册、发现、加载、版本管理和生命周期控制。
    
    功能特性:
    - 单元自动发现与扫描
    - 语义化版本匹配
    - 依赖解析与排序
    - 单元状态管理
    - 热插拔支持
    """
    
    def __init__(self, base_path: str = "", config: Optional[Dict] = None):
        """
        初始化注册中心
        
        Args:
            base_path: 单元根目录路径
            config: 配置选项
        """
        self.base_path = Path(base_path) if base_path else Path.cwd() / "units"
        self.config = config or {}
        
        # 单元存储
        self._units: Dict[str, UnitMetadata] = {}
        self._units_by_tag: Dict[str, Set[str]] = {}
        self._units_by_category: Dict[str, Set[str]] = {}
        self._units_by_type: Dict[UnitType, Set[str]] = {t: set() for t in UnitType}
        
        # 索引缓存
        self._search_index: Dict[str, str] = {}  # {keyword: unit_id}
        self._dependency_graph: Dict[str, Set[str]] = {}  # {unit_id: dependencies}
        
        # 钩子回调
        self._hooks: Dict[str, List[callable]] = {
            'before_register': [],
            'after_register': [],
            'before_load': [],
            'after_load': [],
            'before_unload': [],
            'after_unload': [],
            'on_error': [],
            'on_state_change': [],
        }
        
        # 统计
        self._stats = {
            'total_discovered': 0,
            'total_loaded': 0,
            'total_errors': 0,
            'last_scan': None,
        }
        
        logger.info(f"单元注册中心初始化完成: {self.base_path}")
    
    # ==================== 单元注册 ====================
    
    def register(self, manifest: UnitManifest, base_path: str = "") -> bool:
        """
        注册单元
        
        Args:
            manifest: 单元清单
            base_path: 单元基础路径
            
        Returns:
            是否注册成功
        """
        # 验证清单
        is_valid, errors = manifest.validate()
        if not is_valid:
            logger.error(f"单元清单验证失败 [{manifest.unit_id}]: {errors}")
            return False
        
        # 触发前置钩子
        self._trigger_hook('before_register', manifest)
        
        # 检查是否已注册
        if manifest.unit_id in self._units:
            existing = self._units[manifest.unit_id]
            if existing.state != UnitState.DEPRECATED:
                logger.warning(f"单元已注册: {manifest.unit_id}")
                return False
        
        # 创建单元元数据
        metadata = UnitMetadata(
            unit_id=manifest.unit_id,
            manifest=manifest,
            state=UnitState.DISCOVERED,
            base_path=base_path,
            manifest_path=str(Path(base_path) / "manifest.json") if base_path else "",
            loaded_at=datetime.now().isoformat()
        )
        
        # 存储单元
        self._units[manifest.unit_id] = metadata
        
        # 更新索引
        self._index_unit(metadata)
        
        # 触发后置钩子
        self._trigger_hook('after_register', metadata)
        
        self._stats['total_discovered'] += 1
        logger.info(f"单元注册成功: {manifest.unit_id} v{manifest.version}")
        return True
    
    def unregister(self, unit_id: str) -> bool:
        """
        注销单元
        
        Args:
            unit_id: 单元标识符
            
        Returns:
            是否注销成功
        """
        if unit_id not in self._units:
            logger.warning(f"单元不存在: {unit_id}")
            return False
        
        metadata = self._units[unit_id]
        
        # 如果单元处于活跃状态，先卸载
        if metadata.state == UnitState.ACTIVE:
            self.unload(unit_id)
        
        # 从索引中移除
        self._unindex_unit(metadata)
        
        # 移除单元
        del self._units[unit_id]
        
        logger.info(f"单元已注销: {unit_id}")
        return True
    
    # ==================== 单元发现 ====================
    
    def discover(self, path: Optional[str] = None) -> List[str]:
        """
        扫描并发现单元
        
        Args:
            path: 扫描路径，默认为基础路径
            
        Returns:
            发现的单元ID列表
        """
        scan_path = Path(path) if path else self.base_path
        discovered = []
        
        logger.info(f"开始扫描单元: {scan_path}")
        
        # 遍历目录查找 manifest.json
        for unit_dir in scan_path.rglob("*"):
            if unit_dir.is_dir():
                manifest_path = unit_dir / "manifest.json"
                if manifest_path.exists():
                    try:
                        unit_id = self._discover_unit(unit_dir, str(manifest_path))
                        if unit_id:
                            discovered.append(unit_id)
                    except Exception as e:
                        logger.error(f"扫描单元失败 [{unit_dir}]: {e}")
        
        self._stats['last_scan'] = datetime.now().isoformat()
        logger.info(f"扫描完成，发现 {len(discovered)} 个单元")
        return discovered
    
    def _discover_unit(self, unit_dir: Path, manifest_path: str) -> Optional[str]:
        """发现单个单元"""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = json.loads(content)
            
            # 创建清单并计算校验和
            manifest = UnitManifest.from_dict(data)
            manifest.checksum = manifest.compute_checksum(content)
            manifest.updated_at = datetime.now().isoformat()
            
            # 注册单元
            if self.register(manifest, str(unit_dir)):
                return manifest.unit_id
        
        except json.JSONDecodeError as e:
            logger.error(f"manifest.json 解析失败 [{manifest_path}]: {e}")
        except Exception as e:
            logger.error(f"发现单元异常 [{manifest_path}]: {e}")
        
        return None
    
    def find(self, query: str, limit: int = 10) -> List[str]:
        """
        查找单元
        
        支持按 ID、名称、标签、分类搜索
        
        Args:
            query: 查询关键词
            limit: 返回结果数量限制
            
        Returns:
            匹配的单元ID列表
        """
        query = query.lower()
        results = []
        
        # 精确匹配 unit_id
        if query in self._units:
            results.append(query)
        
        # 模糊匹配
        for unit_id, metadata in self._units.items():
            manifest = metadata.manifest
            
            # 匹配名称
            if query in manifest.name.lower():
                results.append(unit_id)
            # 匹配标签
            elif any(query in tag.lower() for tag in manifest.tags):
                results.append(unit_id)
            # 匹配分类
            elif query in manifest.category.lower():
                results.append(unit_id)
            # 匹配描述
            elif query in manifest.description.lower():
                results.append(unit_id)
        
        return results[:limit]
    
    def find_by_tag(self, tag: str) -> List[str]:
        """按标签查找单元"""
        return list(self._units_by_tag.get(tag.lower(), set()))
    
    def find_by_category(self, category: str) -> List[str]:
        """按分类查找单元"""
        return list(self._units_by_category.get(category.lower(), set()))
    
    def find_by_type(self, unit_type: UnitType) -> List[str]:
        """按类型查找单元"""
        return list(self._units_by_type.get(unit_type, set()))
    
    # ==================== 单元加载 ====================
    
    def load(self, unit_id: str, force: bool = False) -> bool:
        """
        加载单元
        
        Args:
            unit_id: 单元标识符
            force: 是否强制重新加载
            
        Returns:
            是否加载成功
        """
        if unit_id not in self._units:
            logger.error(f"单元不存在: {unit_id}")
            return False
        
        metadata = self._units[unit_id]
        
        # 检查状态
        if metadata.state == UnitState.ACTIVE and not force:
            logger.info(f"单元已加载: {unit_id}")
            return True
        
        # 加载依赖
        if not self._load_dependencies(metadata):
            return False
        
        # 触发前置钩子
        self._trigger_hook('before_load', metadata)
        
        try:
            # 动态导入单元
            base_path = metadata.base_path
            entry_point = metadata.manifest.entry_point
            
            if not Path(base_path).exists():
                raise FileNotFoundError(f"单元路径不存在: {base_path}")
            
            # 添加到 Python 路径
            import sys
            if base_path not in sys.path:
                sys.path.insert(0, base_path)
            
            # 导入模块
            module_name = Path(entry_point).stem
            module = __import__(module_name)
            
            # 获取单元实例
            if metadata.manifest.singleton:
                if hasattr(module, 'get_instance'):
                    metadata.instance = module.get_instance(metadata.manifest.default_config)
                else:
                    metadata.instance = module
            else:
                metadata.instance = module
            
            # 状态转换
            metadata.transition_to(UnitState.LOADED)
            metadata.load_count += 1
            
            # 触发后置钩子
            self._trigger_hook('after_load', metadata)
            
            self._stats['total_loaded'] += 1
            logger.info(f"单元加载成功: {unit_id}")
            return True
            
        except Exception as e:
            metadata.transition_to(UnitState.ERROR, str(e))
            self._trigger_hook('on_error', metadata, e)
            self._stats['total_errors'] += 1
            logger.error(f"单元加载失败 [{unit_id}]: {e}")
            return False
    
    def unload(self, unit_id: str) -> bool:
        """
        卸载单元
        
        Args:
            unit_id: 单元标识符
            
        Returns:
            是否卸载成功
        """
        if unit_id not in self._units:
            logger.error(f"单元不存在: {unit_id}")
            return False
        
        metadata = self._units[unit_id]
        
        # 检查是否有依赖此单元的其他活跃单元
        for uid, deps in self._dependency_graph.items():
            if unit_id in deps:
                dependent = self._units.get(uid)
                if dependent and dependent.state == UnitState.ACTIVE:
                    logger.error(f"单元被依赖，无法卸载: {unit_id} -> {uid}")
                    return False
        
        # 触发前置钩子
        self._trigger_hook('before_unload', metadata)
        
        try:
            # 清理实例
            if hasattr(metadata.instance, 'shutdown'):
                metadata.instance.shutdown()
            
            metadata.instance = None
            metadata.transition_to(UnitState.UNLOADED)
            
            # 触发后置钩子
            self._trigger_hook('after_unload', metadata)
            
            logger.info(f"单元已卸载: {unit_id}")
            return True
            
        except Exception as e:
            logger.error(f"单元卸载异常 [{unit_id}]: {e}")
            return False
    
    def initialize(self, unit_id: str) -> bool:
        """初始化单元"""
        if unit_id not in self._units:
            return False
        
        metadata = self._units[unit_id]
        
        if metadata.state != UnitState.LOADED:
            logger.warning(f"单元未加载，无法初始化: {unit_id}")
            return False
        
        try:
            if hasattr(metadata.instance, 'initialize'):
                metadata.instance.initialize(metadata.manifest.config or {})
            
            metadata.transition_to(UnitState.INITIALIZED)
            return True
            
        except Exception as e:
            metadata.transition_to(UnitState.ERROR, str(e))
            logger.error(f"单元初始化失败 [{unit_id}]: {e}")
            return False
    
    def activate(self, unit_id: str) -> bool:
        """激活单元"""
        if unit_id not in self._units:
            return False
        
        metadata = self._units[unit_id]
        
        # 确保已加载和初始化
        if metadata.state == UnitState.LOADED:
            self.initialize(unit_id)
        
        if metadata.state != UnitState.INITIALIZED:
            logger.warning(f"单元未初始化，无法激活: {unit_id}")
            return False
        
        try:
            if hasattr(metadata.instance, 'activate'):
                metadata.instance.activate()
            
            metadata.transition_to(UnitState.ACTIVE)
            return True
            
        except Exception as e:
            metadata.transition_to(UnitState.ERROR, str(e))
            logger.error(f"单元激活失败 [{unit_id}]: {e}")
            return False
    
    def deactivate(self, unit_id: str) -> bool:
        """停用单元"""
        if unit_id not in self._units:
            return False
        
        metadata = self._units[unit_id]
        
        if metadata.state != UnitState.ACTIVE:
            return True
        
        try:
            if hasattr(metadata.instance, 'deactivate'):
                metadata.instance.deactivate()
            
            metadata.transition_to(UnitState.SUSPENDED)
            return True
            
        except Exception as e:
            logger.error(f"单元停用失败 [{unit_id}]: {e}")
            return False
    
    # ==================== 版本管理 ====================
    
    def resolve_version(self, unit_id: str, version_spec: str) -> Optional[str]:
        """
        解析版本规范到具体版本
        
        Args:
            unit_id: 单元标识符
            version_spec: 版本规范 (如 ^1.0.0, >=1.0.0 <2.0.0)
            
        Returns:
            匹配的版本号，如果无法解析则返回 None
        """
        if unit_id not in self._units:
            return None
        
        available_version = self._units[unit_id].manifest.version
        return self._match_version(available_version, version_spec)
    
    @staticmethod
    def _match_version(version: str, spec: str) -> Optional[str]:
        """
        匹配版本
        
        支持的规范:
        - 精确版本: "1.0.0"
        - caret: "^1.0.0" (兼容版本)
        - tilde: "~1.0.0" (补丁兼容)
        - 范围: ">=1.0.0 <2.0.0"
        """
        spec = spec.strip()
        
        # 精确版本
        if spec == version:
            return version
        
        # caret (^)
        if spec.startswith('^'):
            base = spec[1:]
            parts = version.split('.')
            base_parts = base.split('.')
            if parts[0] == base_parts[0]:
                return version
        
        # tilde (~)
        if spec.startswith('~'):
            base = spec[1:]
            parts = version.split('.')
            base_parts = base.split('.')
            if parts[0] == base_parts[0] and parts[1] == base_parts[1]:
                return version
        
        # 范围
        if '>' in spec or '<' in spec:
            import re
            constraints = re.findall(r'(>=|<=|>|<)?\s*(\d+\.\d+\.\d+)', spec)
            for op, ver in constraints:
                cmp_result = version.compare(ver) if hasattr(version, 'compare') else 0
                if cmp_result < 0 and op in ['>', '>=']:
                    return None
                if cmp_result > 0 and op in ['<', '<=']:
                    return None
            return version
        
        return None
    
    def get_latest_version(self, unit_id_prefix: str) -> Optional[Tuple[str, str]]:
        """
        获取最新版本
        
        Args:
            unit_id_prefix: 单元ID前缀 (如 "core.")
            
        Returns:
            (unit_id, version) 或 None
        """
        candidates = [
            (uid, meta.manifest.version)
            for uid, meta in self._units.items()
            if uid.startswith(unit_id_prefix)
        ]
        
        if not candidates:
            return None
        
        # 简单版本比较 (实际应使用 semver 库)
        candidates.sort(key=lambda x: [int(p) for p in x[1].split('.')], reverse=True)
        return candidates[0]
    
    def check_updates(self, unit_id: str) -> Dict[str, Any]:
        """检查单元更新"""
        if unit_id not in self._units:
            return {}
        
        metadata = self._units[unit_id]
        
        return {
            'unit_id': unit_id,
            'current_version': metadata.manifest.version,
            'is_latest': True,  # 需要对比注册表
            'update_available': False,
        }
    
    # ==================== 依赖管理 ====================
    
    def _load_dependencies(self, metadata: UnitMetadata) -> bool:
        """加载单元依赖"""
        manifest = metadata.manifest
        
        for dep_id, version_spec in manifest.dependencies.items():
            if dep_id not in self._units:
                logger.error(f"缺少依赖: {metadata.unit_id} -> {dep_id}")
                return False
            
            dep_metadata = self._units[dep_id]
            
            # 检查版本兼容性
            if not self.resolve_version(dep_id, version_spec):
                logger.error(f"版本不兼容: {metadata.unit_id} 需要 {dep_id} {version_spec}")
                return False
            
            # 递归加载依赖
            if dep_metadata.state in [UnitState.DISCOVERED, UnitState.UNLOADED]:
                if not self.load(dep_id):
                    return False
        
        return True
    
    def resolve_dependencies(self, unit_ids: List[str]) -> List[str]:
        """
        解析依赖并返回加载顺序
        
        使用拓扑排序确保依赖顺序正确
        
        Args:
            unit_ids: 单元ID列表
            
        Returns:
            排序后的单元ID列表
        """
        # 构建依赖图
        graph = {}
        for unit_id in unit_ids:
            if unit_id in self._units:
                deps = set(self._units[unit_id].manifest.dependencies.keys())
                graph[unit_id] = deps & set(unit_ids)  # 只考虑请求中的依赖
        
        # 拓扑排序 (Kahn算法)
        sorted_ids = []
        in_degree = {uid: 0 for uid in graph}
        
        for uid, deps in graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[uid] += 1
        
        queue = [uid for uid, degree in in_degree.items() if degree == 0]
        
        while queue:
            current = queue.pop(0)
            sorted_ids.append(current)
            
            for uid, deps in graph.items():
                if current in deps:
                    in_degree[uid] -= 1
                    if in_degree[uid] == 0:
                        queue.append(uid)
        
        if len(sorted_ids) != len(unit_ids):
            logger.warning("存在循环依赖")
        
        return sorted_ids
    
    def get_dependents(self, unit_id: str) -> List[str]:
        """获取依赖此单元的所有单元"""
        dependents = []
        
        for uid, metadata in self._units.items():
            if unit_id in metadata.manifest.dependencies:
                dependents.append(uid)
        
        return dependents
    
    # ==================== 索引管理 ====================
    
    def _index_unit(self, metadata: UnitMetadata):
        """索引单元"""
        manifest = metadata.manifest
        
        # 按标签索引
        for tag in manifest.tags:
            tag_lower = tag.lower()
            if tag_lower not in self._units_by_tag:
                self._units_by_tag[tag_lower] = set()
            self._units_by_tag[tag_lower].add(metadata.unit_id)
        
        # 按分类索引
        if manifest.category:
            cat_lower = manifest.category.lower()
            if cat_lower not in self._units_by_category:
                self._units_by_category[cat_lower] = set()
            self._units_by_category[cat_lower].add(metadata.unit_id)
        
        # 按类型索引
        self._units_by_type[manifest.unit_type].add(metadata.unit_id)
        
        # 更新依赖图
        self._dependency_graph[metadata.unit_id] = set(manifest.dependencies.keys())
        
        # 搜索索引
        self._search_index[metadata.unit_id.lower()] = metadata.unit_id
        self._search_index[manifest.name.lower()] = metadata.unit_id
    
    def _unindex_unit(self, metadata: UnitMetadata):
        """移除单元索引"""
        manifest = metadata.manifest
        
        # 移除标签索引
        for tag in manifest.tags:
            tag_lower = tag.lower()
            if tag_lower in self._units_by_tag:
                self._units_by_tag[tag_lower].discard(metadata.unit_id)
        
        # 移除分类索引
        if manifest.category:
            cat_lower = manifest.category.lower()
            if cat_lower in self._units_by_category:
                self._units_by_category[cat_lower].discard(metadata.unit_id)
        
        # 移除类型索引
        self._units_by_type[manifest.unit_type].discard(metadata.unit_id)
        
        # 移除搜索索引
        self._search_index.pop(metadata.unit_id.lower(), None)
        self._search_index.pop(manifest.name.lower(), None)
        
        # 移除依赖图
        self._dependency_graph.pop(metadata.unit_id, None)
    
    # ==================== 钩子系统 ====================
    
    def register_hook(self, event: str, callback: callable):
        """注册钩子回调"""
        if event in self._hooks:
            self._hooks[event].append(callback)
            logger.debug(f"钩子已注册: {event}")
    
    def _trigger_hook(self, event: str, *args, **kwargs):
        """触发钩子"""
        for callback in self._hooks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"钩子执行失败 [{event}]: {e}")
    
    # ==================== 查询接口 ====================
    
    def get(self, unit_id: str) -> Optional[UnitMetadata]:
        """获取单元元数据"""
        return self._units.get(unit_id)
    
    def get_manifest(self, unit_id: str) -> Optional[UnitManifest]:
        """获取单元清单"""
        metadata = self._units.get(unit_id)
        return metadata.manifest if metadata else None
    
    def list_all(self) -> List[str]:
        """列出所有单元ID"""
        return list(self._units.keys())
    
    def list_by_state(self, state: UnitState) -> List[str]:
        """按状态列出单元"""
        return [
            uid for uid, meta in self._units.items()
            if meta.state == state
        ]
    
    def list_active(self) -> List[str]:
        """列出所有活跃单元"""
        return self.list_by_state(UnitState.ACTIVE)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        state_counts = {}
        for state in UnitState:
            state_counts[state.name] = sum(
                1 for m in self._units.values() if m.state == state
            )
        
        return {
            'total_units': len(self._units),
            'by_state': state_counts,
            'total_discovered': self._stats['total_discovered'],
            'total_loaded': self._stats['total_loaded'],
            'total_errors': self._stats['total_errors'],
            'last_scan': self._stats['last_scan'],
        }
    
    # ==================== 批量操作 ====================
    
    def load_all(self, unit_ids: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        批量加载单元
        
        Args:
            unit_ids: 单元ID列表，None 表示加载所有已发现单元
            
        Returns:
            {unit_id: success}
        """
        if unit_ids is None:
            unit_ids = self.list_by_state(UnitState.DISCOVERED)
        
        # 解析依赖顺序
        sorted_ids = self.resolve_dependencies(unit_ids)
        
        results = {}
        for uid in sorted_ids:
            results[uid] = self.load(uid)
            
            # 初始化并激活
            if results[uid]:
                self.initialize(uid)
                self.activate(uid)
        
        return results
    
    def unload_all(self) -> Dict[str, bool]:
        """卸载所有单元"""
        # 先停用所有活跃单元
        for uid in self.list_active():
            self.deactivate(uid)
        
        # 按依赖逆序卸载
        all_ids = list(self._units.keys())
        all_ids.reverse()
        
        results = {}
        for uid in all_ids:
            results[uid] = self.unload(uid)
        
        return results
    
    # ==================== 持久化 ====================
    
    def export_registry(self, path: str) -> bool:
        """
        导出注册表
        
        Args:
            path: 导出文件路径
            
        Returns:
            是否成功
        """
        try:
            data = {
                'version': '3.0',
                'exported_at': datetime.now().isoformat(),
                'units': {
                    uid: meta.to_dict()
                    for uid, meta in self._units.items()
                },
                'stats': self.get_stats()
            }
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"注册表已导出: {path}")
            return True
            
        except Exception as e:
            logger.error(f"导出注册表失败: {e}")
            return False
    
    def import_registry(self, path: str) -> bool:
        """
        导入注册表
        
        Args:
            path: 导入文件路径
            
        Returns:
            是否成功
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for unit_id, unit_data in data.get('units', {}).items():
                manifest = UnitManifest.from_dict(unit_data['manifest'])
                self.register(manifest, unit_data.get('base_path', ''))
            
            logger.info(f"注册表已导入: {path}")
            return True
            
        except Exception as e:
            logger.error(f"导入注册表失败: {e}")
            return False


# ==================== 示例代码 ====================

def example():
    """使用示例"""
    # 创建注册中心
    registry = UnitRegistry("./units")
    
    # 创建示例清单
    manifest = UnitManifest(
        unit_id="core.base",
        name="基础核心",
        version="1.0.0",
        entry_point="__init__.py",
        description="序境3.0基础核心模块",
        author="少府监",
        unit_type=UnitType.CORE,
        tags=["core", "essential"],
        category="system",
        dependencies={},
        capabilities=["event_bus", "config_manager"],
        priority=1
    )
    
    # 注册单元
    registry.register(manifest, "/path/to/unit")
    
    # 发现单元
    discovered = registry.discover()
    print(f"发现单元: {discovered}")
    
    # 查找单元
    results = registry.find("base")
    print(f"搜索结果: {results}")
    
    # 加载单元
    if results:
        registry.load(results[0])
        registry.initialize(results[0])
        registry.activate(results[0])
    
    # 列出活跃单元
    active = registry.list_active()
    print(f"活跃单元: {active}")
    
    # 获取统计
    stats = registry.get_stats()
    print(f"统计信息: {stats}")


if __name__ == "__main__":
    example()
