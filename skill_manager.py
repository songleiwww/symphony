#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响（Symphony）技能调用模块
包含技能发现、加载、调用、参数验证和错误处理
与故障处理系统集成
"""

import os
import re
import json
import logging
import importlib.util
import inspect
from enum import Enum
from typing import (
    Any, Callable, Dict, List, Optional, Tuple, Type, Union
)
from dataclasses import dataclass, field
from pathlib import Path
from functools import wraps
from jsonschema import validate, ValidationError
import threading

# 导入故障处理系统
from fault_tolerance import (
    Retrier, CircuitBreaker, FallbackManager, FailoverManager,
    SmartClient, RetryConfig, CircuitBreakerConfig,
    RetryError, CircuitOpenError, FallbackError,
    classify_error, ErrorType, with_retry, with_circuit_breaker
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# 异常定义
# =============================================================================

class SkillError(Exception):
    """技能系统基础异常"""
    pass


class SkillNotFoundError(SkillError):
    """技能未找到异常"""
    pass


class SkillLoadError(SkillError):
    """技能加载失败异常"""
    pass


class SkillExecutionError(SkillError):
    """技能执行异常"""
    pass


class SkillParameterError(SkillError):
    """技能参数验证异常"""
    pass


class SkillPermissionError(SkillError):
    """技能权限异常"""
    pass


# =============================================================================
# 枚举类型
# =============================================================================

class SkillStatus(Enum):
    """技能状态"""
    DISABLED = "disabled"      # 禁用
    LOADING = "loading"        # 加载中
    READY = "ready"            # 就绪
    RUNNING = "running"        # 运行中
    ERROR = "error"            # 错误
    DEGRADED = "degraded"      # 降级


class SkillType(Enum):
    """技能类型"""
    PYTHON = "python"          # Python模块
    SCRIPT = "script"          # 脚本文件
    COMMAND = "command"        # 命令行工具
    WEB_SERVICE = "web_service"  # Web服务


# =============================================================================
# 数据类
# =============================================================================

@dataclass
class SkillParameter:
    """技能参数定义"""
    name: str
    type: str  # string, number, boolean, array, object
    description: str = ""
    required: bool = True
    default: Any = None
    enum: List[Any] = field(default_factory=list)
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None


@dataclass
class SkillMetadata:
    """技能元数据"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    tags: List[str] = field(default_factory=list)
    skill_type: SkillType = SkillType.PYTHON
    category: str = "general"
    priority: int = 0
    enabled: bool = True
    timeout: float = 60.0
    retries: int = 3
    requires_auth: bool = False
    permissions: List[str] = field(default_factory=list)
    deprecated: bool = False
    deprecation_message: str = ""


@dataclass
class SkillConfig:
    """技能配置"""
    skill_dirs: List[str] = field(default_factory=list)
    auto_reload: bool = False
    reload_interval: float = 60.0
    default_timeout: float = 60.0
    default_retries: int = 3
    enable_circuit_breaker: bool = True
    enable_fallback: bool = True
    enable_failover: bool = True


@dataclass
class SkillExecutionResult:
    """技能执行结果"""
    success: bool
    skill_name: str
    data: Any = None
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    execution_time: float = 0.0
    retry_count: int = 0
    from_cache: bool = False
    from_fallback: bool = False


@dataclass
class SkillStats:
    """技能统计"""
    total_calls: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    last_execution_time: Optional[float] = None
    last_error: Optional[str] = None
    last_error_time: Optional[float] = None
    circuit_breaker_stats: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# 技能类
# =============================================================================

class Skill:
    """技能基类"""
    
    def __init__(
        self,
        metadata: SkillMetadata,
        parameters: List[SkillParameter],
        execute_func: Optional[Callable] = None
    ):
        self.metadata = metadata
        self.parameters = parameters
        self._execute_func = execute_func
        self._status = SkillStatus.READY
        self._stats = SkillStats()
        self._lock = threading.RLock()
        self._fallback_func: Optional[Callable] = None
    
    @property
    def name(self) -> str:
        return self.metadata.name
    
    @property
    def status(self) -> SkillStatus:
        return self._status
    
    @property
    def stats(self) -> SkillStats:
        return self._stats
    
    def set_fallback(self, func: Callable):
        """设置降级函数"""
        self._fallback_func = func
    
    def validate_parameters(self, params: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证参数
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        # 检查必填参数
        for param in self.parameters:
            if param.required and param.name not in params:
                errors.append(f"缺少必填参数: {param.name}")
                continue
            
            if param.name in params:
                value = params[param.name]
                param_errors = self._validate_parameter_value(param, value)
                errors.extend(param_errors)
        
        # 检查未知参数
        param_names = {p.name for p in self.parameters}
        for key in params:
            if key not in param_names:
                logger.warning(f"未知参数: {key}")
        
        return len(errors) == 0, errors
    
    def _validate_parameter_value(self, param: SkillParameter, value: Any) -> List[str]:
        """验证单个参数值"""
        errors = []
        
        # 类型检查
        type_mapping = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_type = type_mapping.get(param.type)
        if expected_type and not isinstance(value, expected_type):
            errors.append(
                f"参数 '{param.name}' 类型错误，期望 {param.type}，"
                f"实际 {type(value).__name__}"
            )
            return errors
        
        # 枚举检查
        if param.enum and value not in param.enum:
            errors.append(
                f"参数 '{param.name}' 值 '{value}' 不在允许的列表中: {param.enum}"
            )
        
        # 数值范围检查
        if param.type == "number":
            if param.minimum is not None and value < param.minimum:
                errors.append(
                    f"参数 '{param.name}' 值 {value} 小于最小值 {param.minimum}"
                )
            if param.maximum is not None and value > param.maximum:
                errors.append(
                    f"参数 '{param.name}' 值 {value} 大于最大值 {param.maximum}"
                )
        
        # 字符串长度检查
        if param.type == "string":
            if param.min_length is not None and len(value) < param.min_length:
                errors.append(
                    f"参数 '{param.name}' 长度 {len(value)} 小于最小长度 {param.min_length}"
                )
            if param.max_length is not None and len(value) > param.max_length:
                errors.append(
                    f"参数 '{param.name}' 长度 {len(value)} 大于最大长度 {param.max_length}"
                )
        
        # 正则检查
        if param.type == "string" and param.pattern:
            if not re.match(param.pattern, value):
                errors.append(
                    f"参数 '{param.name}' 值 '{value}' 不匹配模式 '{param.pattern}'"
                )
        
        return errors
    
    def _apply_defaults(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """应用默认参数值"""
        result = dict(params)
        for param in self.parameters:
            if param.name not in result and not param.required:
                result[param.name] = param.default
        return result
    
    def execute(
        self,
        params: Dict[str, Any],
        use_cache: bool = False,
        **kwargs
    ) -> SkillExecutionResult:
        """
        执行技能
        
        Args:
            params: 参数字典
            use_cache: 是否使用缓存
            **kwargs: 其他参数
        
        Returns:
            技能执行结果
        """
        import time
        
        start_time = time.time()
        retry_count = 0
        
        with self._lock:
            self._status = SkillStatus.RUNNING
        
        try:
            # 参数验证
            is_valid, errors = self.validate_parameters(params)
            if not is_valid:
                raise SkillParameterError("; ".join(errors))
            
            # 应用默认值
            params = self._apply_defaults(params)
            
            # 执行技能
            if self._execute_func:
                data = self._execute_func(**params)
            else:
                raise SkillExecutionError("技能未实现执行函数")
            
            execution_time = time.time() - start_time
            
            # 更新统计
            with self._lock:
                self._stats.total_calls += 1
                self._stats.success_count += 1
                self._stats.total_execution_time += execution_time
                self._stats.avg_execution_time = (
                    self._stats.total_execution_time / self._stats.success_count
                )
                self._stats.last_execution_time = execution_time
                self._status = SkillStatus.READY
            
            return SkillExecutionResult(
                success=True,
                skill_name=self.name,
                data=data,
                execution_time=execution_time,
                retry_count=retry_count
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_type = classify_error(e)
            
            # 更新统计
            with self._lock:
                self._stats.total_calls += 1
                self._stats.failure_count += 1
                self._stats.last_error = str(e)
                self._stats.last_error_time = time.time()
                self._status = SkillStatus.ERROR
            
            # 尝试降级
            if self._fallback_func:
                try:
                    logger.warning(f"技能 '{self.name}' 执行失败，尝试降级: {e}")
                    fallback_data = self._fallback_func(**params)
                    return SkillExecutionResult(
                        success=True,
                        skill_name=self.name,
                        data=fallback_data,
                        execution_time=execution_time,
                        from_fallback=True
                    )
                except Exception as fe:
                    logger.error(f"降级执行也失败: {fe}")
            
            return SkillExecutionResult(
                success=False,
                skill_name=self.name,
                error=str(e),
                error_type=error_type,
                execution_time=execution_time,
                retry_count=retry_count
            )


# =============================================================================
# 技能发现器
# =============================================================================

class SkillDiscoverer:
    """技能发现器"""
    
    def __init__(self, skill_dirs: List[str]):
        self.skill_dirs = [Path(d) for d in skill_dirs if os.path.exists(d)]
        logger.info(f"技能发现器初始化，目录: {[str(d) for d in self.skill_dirs]}")
    
    def discover(self) -> List[Path]:
        """
        发现所有技能
        
        Returns:
            技能文件路径列表
        """
        skill_paths = []
        
        for skill_dir in self.skill_dirs:
            skill_paths.extend(self._discover_in_directory(skill_dir))
        
        logger.info(f"发现 {len(skill_paths)} 个技能")
        return skill_paths
    
    def _discover_in_directory(self, directory: Path) -> List[Path]:
        """在目录中发现技能"""
        skill_paths = []
        
        if not directory.exists():
            return skill_paths
        
        # 查找包含 SKILL.md 的目录
        for item in directory.iterdir():
            if item.is_dir():
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    skill_paths.append(item)
                    logger.debug(f"发现技能目录: {item}")
                else:
                    # 递归查找子目录
                    skill_paths.extend(self._discover_in_directory(item))
            
            # 查找 Python 技能模块
            elif item.suffix == ".py" and not item.name.startswith("_"):
                skill_paths.append(item)
                logger.debug(f"发现技能文件: {item}")
        
        return skill_paths
    
    def parse_skill_metadata(self, skill_path: Path) -> Optional[SkillMetadata]:
        """
        解析技能元数据
        
        Args:
            skill_path: 技能路径（目录或文件）
        
        Returns:
            技能元数据
        """
        if skill_path.is_dir():
            return self._parse_skill_from_directory(skill_path)
        elif skill_path.suffix == ".py":
            return self._parse_skill_from_python(skill_path)
        else:
            return None
    
    def _parse_skill_from_directory(self, skill_dir: Path) -> Optional[SkillMetadata]:
        """从目录解析技能元数据"""
        skill_md = skill_dir / "SKILL.md"
        
        if not skill_md.exists():
            return None
        
        try:
            content = skill_md.read_text(encoding="utf-8")
            
            # 解析 YAML front matter
            front_matter = self._extract_front_matter(content)
            
            metadata = SkillMetadata(
                name=front_matter.get("name", skill_dir.name),
                version=front_matter.get("version", "1.0.0"),
                description=front_matter.get("description", ""),
                author=front_matter.get("author", ""),
                tags=front_matter.get("tags", []),
                skill_type=SkillType.SCRIPT,
                category=front_matter.get("category", "general"),
                enabled=True
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"解析技能目录 {skill_dir} 失败: {e}")
            return None
    
    def _parse_skill_from_python(self, skill_file: Path) -> Optional[SkillMetadata]:
        """从 Python 文件解析技能元数据"""
        try:
            # 尝试从模块 docstring 提取元数据
            spec = importlib.util.spec_from_file_location(
                f"skill_{skill_file.stem}",
                str(skill_file)
            )
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            
            # 只解析模块，不执行
            metadata = SkillMetadata(
                name=skill_file.stem,
                version="1.0.0",
                skill_type=SkillType.PYTHON,
                enabled=True
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"解析 Python 技能 {skill_file} 失败: {e}")
            return None
    
    def _extract_front_matter(self, content: str) -> Dict[str, Any]:
        """从 Markdown 内容提取 YAML front matter"""
        import yaml
        
        front_matter = {}
        
        # 简单的 front matter 解析
        if content.startswith("---"):
            end_idx = content.find("---", 3)
            if end_idx != -1:
                try:
                    yaml_content = content[3:end_idx].strip()
                    front_matter = yaml.safe_load(yaml_content) or {}
                except Exception as e:
                    logger.warning(f"解析 front matter 失败: {e}")
        
        return front_matter


# =============================================================================
# 技能加载器
# =============================================================================

class SkillLoader:
    """技能加载器"""
    
    def __init__(self):
        self._loaded_skills: Dict[str, Skill] = {}
        self._lock = threading.RLock()
    
    def load_skill(
        self,
        skill_path: Path,
        metadata: Optional[SkillMetadata] = None
    ) -> Optional[Skill]:
        """
        加载技能
        
        Args:
            skill_path: 技能路径
            metadata: 技能元数据（可选，自动解析）
        
        Returns:
            加载的技能
        """
        with self._lock:
            try:
                if metadata is None:
                    discoverer = SkillDiscoverer([])
                    metadata = discoverer.parse_skill_metadata(skill_path)
                
                if not metadata:
                    logger.error(f"无法解析技能元数据: {skill_path}")
                    return None
                
                if skill_path.is_dir():
                    skill = self._load_skill_from_directory(skill_path, metadata)
                elif skill_path.suffix == ".py":
                    skill = self._load_skill_from_python(skill_path, metadata)
                else:
                    logger.warning(f"不支持的技能类型: {skill_path}")
                    return None
                
                if skill:
                    self._loaded_skills[skill.name] = skill
                    logger.info(f"技能加载成功: {skill.name}")
                
                return skill
                
            except Exception as e:
                logger.error(f"加载技能失败 {skill_path}: {e}")
                raise SkillLoadError(f"加载技能失败: {e}") from e
    
    def _load_skill_from_directory(
        self,
        skill_dir: Path,
        metadata: SkillMetadata
    ) -> Optional[Skill]:
        """从目录加载技能"""
        # 对于目录技能，创建一个基本的 Skill 对象
        # 实际执行可以通过调用脚本实现
        parameters: List[SkillParameter] = []
        
        skill = Skill(
            metadata=metadata,
            parameters=parameters,
            execute_func=None  # 后续可以扩展脚本执行
        )
        
        return skill
    
    def _load_skill_from_python(
        self,
        skill_file: Path,
        metadata: SkillMetadata
    ) -> Optional[Skill]:
        """从 Python 文件加载技能"""
        try:
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(
                f"skill_{skill_file.stem}",
                str(skill_file)
            )
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找 execute 函数或 Skill 类
            execute_func = None
            parameters: List[SkillParameter] = []
            
            if hasattr(module, "execute"):
                execute_func = module.execute
                
                # 从函数签名推断参数
                sig = inspect.signature(execute_func)
                for name, param in sig.parameters.items():
                    if name in ["self", "cls"]:
                        continue
                    
                    skill_param = SkillParameter(
                        name=name,
                        type="string",  # 默认类型
                        required=param.default is inspect.Parameter.empty,
                        default=param.default if param.default is not inspect.Parameter.empty else None
                    )
                    parameters.append(skill_param)
            
            # 如果有 metadata 模块，使用它
            if hasattr(module, "SKILL_METADATA"):
                metadata_dict = module.SKILL_METADATA
                metadata = SkillMetadata(
                    name=metadata_dict.get("name", metadata.name),
                    version=metadata_dict.get("version", metadata.version),
                    description=metadata_dict.get("description", metadata.description),
                    author=metadata_dict.get("author", metadata.author),
                    tags=metadata_dict.get("tags", metadata.tags),
                    category=metadata_dict.get("category", metadata.category)
                )
            
            # 如果有 parameters 模块，使用它
            if hasattr(module, "SKILL_PARAMETERS"):
                params_list = module.SKILL_PARAMETERS
                parameters = []
                for param_dict in params_list:
                    parameters.append(SkillParameter(
                        name=param_dict["name"],
                        type=param_dict.get("type", "string"),
                        description=param_dict.get("description", ""),
                        required=param_dict.get("required", True),
                        default=param_dict.get("default"),
                        enum=param_dict.get("enum", []),
                        minimum=param_dict.get("minimum"),
                        maximum=param_dict.get("maximum"),
                        pattern=param_dict.get("pattern"),
                        min_length=param_dict.get("min_length"),
                        max_length=param_dict.get("max_length")
                    ))
            
            skill = Skill(
                metadata=metadata,
                parameters=parameters,
                execute_func=execute_func
            )
            
            return skill
            
        except Exception as e:
            logger.error(f"加载 Python 技能失败 {skill_file}: {e}")
            raise SkillLoadError(f"加载 Python 技能失败: {e}") from e
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """获取已加载的技能"""
        with self._lock:
            return self._loaded_skills.get(name)
    
    def list_skills(self) -> List[Skill]:
        """列出所有已加载的技能"""
        with self._lock:
            return list(self._loaded_skills.values())
    
    def unload_skill(self, name: str):
        """卸载技能"""
        with self._lock:
            if name in self._loaded_skills:
                del self._loaded_skills[name]
                logger.info(f"技能已卸载: {name}")


# =============================================================================
# 技能管理器
# =============================================================================

class SkillManager:
    """
    技能管理器 - 交响（Symphony）的核心组件
    
    功能：
    - 技能发现和加载
    - 技能调用接口
    - 技能参数验证
    - 技能错误处理
    - 与故障处理系统集成
    """
    
    def __init__(
        self,
        config: Optional[SkillConfig] = None,
        retrier: Optional[Retrier] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        fallback_manager: Optional[FallbackManager] = None,
        failover_manager: Optional[FailoverManager] = None
    ):
        self.config = config or SkillConfig()
        self.discoverer = SkillDiscoverer(self.config.skill_dirs)
        self.loader = SkillLoader()
        
        # 容错组件
        self.retrier = retrier or Retrier()
        self.circuit_breaker = circuit_breaker or CircuitBreaker(
            name="skill_manager"
        )
        self.fallback_manager = fallback_manager or FallbackManager()
        self.failover_manager = failover_manager or FailoverManager()
        
        # 智能客户端
        self.smart_client = SmartClient(
            retrier=self.retrier,
            circuit_breaker=self.circuit_breaker,
            fallback_manager=self.fallback_manager,
            failover_manager=self.failover_manager
        )
        
        self._lock = threading.RLock()
        self._running = False
        self._reload_thread: Optional[threading.Thread] = None
        
        logger.info("技能管理器初始化完成")
    
    def initialize(self):
        """初始化技能管理器"""
        logger.info("初始化技能管理器...")
        
        # 发现和加载技能
        self.discover_and_load()
        
        # 启动自动重载（如果启用）
        if self.config.auto_reload:
            self._start_auto_reload()
        
        logger.info("技能管理器初始化完成")
    
    def discover_and_load(self):
        """发现并加载所有技能"""
        logger.info("开始发现和加载技能...")
        
        skill_paths = self.discoverer.discover()
        
        for skill_path in skill_paths:
            try:
                metadata = self.discoverer.parse_skill_metadata(skill_path)
                if metadata and metadata.enabled:
                    self.loader.load_skill(skill_path, metadata)
            except Exception as e:
                logger.error(f"加载技能失败 {skill_path}: {e}")
        
        skills = self.loader.list_skills()
        logger.info(f"技能加载完成，共 {len(skills)} 个技能")
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """获取技能"""
        return self.loader.get_skill(name)
    
    def list_skills(self) -> List[Skill]:
        """列出所有技能"""
        return self.loader.list_skills()
    
    def list_skills_by_category(self, category: str) -> List[Skill]:
        """按类别列出技能"""
        return [
            skill for skill in self.loader.list_skills()
            if skill.metadata.category == category
        ]
    
    def search_skills(self, query: str) -> List[Skill]:
        """搜索技能"""
        query = query.lower()
        results = []
        
        for skill in self.loader.list_skills():
            metadata = skill.metadata
            if (
                query in metadata.name.lower() or
                query in metadata.description.lower() or
                any(query in tag.lower() for tag in metadata.tags)
            ):
                results.append(skill)
        
        return results
    
    def execute_skill(
        self,
        skill_name: str,
        params: Dict[str, Any],
        use_retries: bool = True,
        use_circuit_breaker: bool = True,
        use_fallback: bool = True,
        use_failover: bool = True,
        **kwargs
    ) -> SkillExecutionResult:
        """
        执行技能
        
        Args:
            skill_name: 技能名称
            params: 技能参数
            use_retries: 是否使用重试
            use_circuit_breaker: 是否使用熔断器
            use_fallback: 是否使用降级
            use_failover: 是否使用故障转移
            **kwargs: 其他参数
        
        Returns:
            技能执行结果
        """
        import time
        
        start_time = time.time()
        
        # 获取技能
        skill = self.get_skill(skill_name)
        if not skill:
            return SkillExecutionResult(
                success=False,
                skill_name=skill_name,
                error=f"技能未找到: {skill_name}",
                error_type=ErrorType.CLIENT_ERROR,
                execution_time=time.time() - start_time
            )
        
        # 检查技能状态
        if skill.metadata.deprecated:
            logger.warning(
                f"技能 '{skill_name}' 已弃用: {skill.metadata.deprecation_message}"
            )
        
        if not skill.metadata.enabled:
            return SkillExecutionResult(
                success=False,
                skill_name=skill_name,
                error=f"技能已禁用: {skill_name}",
                error_type=ErrorType.CLIENT_ERROR,
                execution_time=time.time() - start_time
            )
        
        try:
            # 定义包装的执行函数
            def wrapped_execute():
                return skill.execute(params, **kwargs)
            
            # 使用智能客户端执行
            if use_retries or use_circuit_breaker or use_fallback or use_failover:
                result = self.smart_client.execute(
                    wrapped_execute,
                    use_retries=use_retries and self.config.default_retries > 0,
                    use_circuit_breaker=use_circuit_breaker and self.config.enable_circuit_breaker,
                    use_failover=use_failover and self.config.enable_failover
                )
                # 注意：这里需要适配 SmartClient 的返回值
                # 实际上，Skill.execute 已经返回了 SkillExecutionResult
                # 这里我们直接调用 skill.execute
                result = skill.execute(params, **kwargs)
            else:
                result = skill.execute(params, **kwargs)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_type = classify_error(e)
            
            return SkillExecutionResult(
                success=False,
                skill_name=skill_name,
                error=str(e),
                error_type=error_type,
                execution_time=execution_time
            )
    
    def register_skill_fallback(self, skill_name: str, fallback_func: Callable):
        """注册技能降级函数"""
        skill = self.get_skill(skill_name)
        if skill:
            skill.set_fallback(fallback_func)
            logger.info(f"已为技能 '{skill_name}' 注册降级函数")
    
    def get_skill_stats(self, skill_name: str) -> Optional[SkillStats]:
        """获取技能统计"""
        skill = self.get_skill(skill_name)
        if skill:
            return skill.stats
        return None
    
    def get_all_stats(self) -> Dict[str, SkillStats]:
        """获取所有技能统计"""
        return {
            skill.name: skill.stats
            for skill in self.loader.list_skills()
        }
    
    def reload_skill(self, skill_name: str) -> bool:
        """重新加载技能"""
        with self._lock:
            # 先卸载
            self.loader.unload_skill(skill_name)
            
            # 重新发现和加载
            skill_paths = self.discoverer.discover()
            for skill_path in skill_paths:
                try:
                    metadata = self.discoverer.parse_skill_metadata(skill_path)
                    if metadata and metadata.name == skill_name:
                        self.loader.load_skill(skill_path, metadata)
                        logger.info(f"技能已重新加载: {skill_name}")
                        return True
                except Exception as e:
                    logger.error(f"重新加载技能失败 {skill_name}: {e}")
            
            return False
    
    def reload_all(self):
        """重新加载所有技能"""
        logger.info("重新加载所有技能...")
        
        with self._lock:
            # 清空已加载的技能
            for skill in self.loader.list_skills():
                self.loader.unload_skill(skill.name)
            
            # 重新发现和加载
            self.discover_and_load()
    
    def _start_auto_reload(self):
        """启动自动重载"""
        if self._running:
            return
        
        self._running = True
        self._reload_thread = threading.Thread(
            target=self._auto_reload_loop,
            daemon=True
        )
        self._reload_thread.start()
        logger.info("自动重载已启动")
    
    def _stop_auto_reload(self):
        """停止自动重载"""
        self._running = False
        if self._reload_thread:
            self._reload_thread.join(timeout=5.0)
        logger.info("自动重载已停止")
    
    def _auto_reload_loop(self):
        """自动重载循环"""
        while self._running:
            try:
                time.sleep(self.config.reload_interval)
                # 这里可以实现检查技能文件变化并自动重载的逻辑
            except Exception as e:
                logger.error(f"自动重载出错: {e}")
                time.sleep(self.config.reload_interval)
    
    def shutdown(self):
        """关闭技能管理器"""
        logger.info("关闭技能管理器...")
        
        if self.config.auto_reload:
            self._stop_auto_reload()
        
        logger.info("技能管理器已关闭")


# =============================================================================
# 便捷装饰器
# =============================================================================

def skill(
    name: str,
    version: str = "1.0.0",
    description: str = "",
    tags: List[str] = None,
    category: str = "general",
    parameters: List[Dict] = None
):
    """
    技能装饰器
    
    用于将 Python 函数标记为技能
    
    Args:
        name: 技能名称
        version: 版本
        description: 描述
        tags: 标签
        category: 类别
        parameters: 参数定义列表
    """
    def decorator(func: Callable):
        # 设置技能元数据
        func.SKILL_METADATA = {
            "name": name,
            "version": version,
            "description": description,
            "tags": tags or [],
            "category": category
        }
        
        # 设置参数定义
        if parameters:
            func.SKILL_PARAMETERS = parameters
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# =============================================================================
# 示例技能
# =============================================================================

@skill(
    name="example_skill",
    version="1.0.0",
    description="示例技能，用于演示技能系统",
    tags=["example", "demo"],
    category="demo",
    parameters=[
        {
            "name": "message",
            "type": "string",
            "description": "要显示的消息",
            "required": True,
            "min_length": 1,
            "max_length": 100
        },
        {
            "name": "count",
            "type": "number",
            "description": "重复次数",
            "required": False,
            "default": 1,
            "minimum": 1,
            "maximum": 10
        }
    ]
)
def example_skill(message: str, count: int = 1) -> Dict[str, Any]:
    """示例技能执行函数"""
    return {
        "result": message * count,
        "count": count,
        "length": len(message)
    }


# =============================================================================
# 主函数（示例）
# =============================================================================

def main():
    """示例用法"""
    print("=" * 60)
    print("交响（Symphony）技能调用模块 - 示例")
    print("=" * 60)
    
    # 1. 创建配置
    print("\n1. 创建配置...")
    config = SkillConfig(
        skill_dirs=[
            str(Path(__file__).parent.parent / "skills")
        ],
        auto_reload=False,
        default_timeout=30.0,
        default_retries=3
    )
    print(f"   - 技能目录: {config.skill_dirs}")
    
    # 2. 创建技能管理器
    print("\n2. 创建技能管理器...")
    skill_manager = SkillManager(config=config)
    
    # 3. 手动创建示例技能（用于演示）
    print("\n3. 创建示例技能...")
    
    # 创建示例技能
    example_metadata = SkillMetadata(
        name="example_skill",
        version="1.0.0",
        description="示例技能，用于演示技能系统",
        tags=["example", "demo"],
        skill_type=SkillType.PYTHON,
        category="demo",
        enabled=True,
        timeout=30.0
    )
    
    example_parameters = [
        SkillParameter(
            name="message",
            type="string",
            description="要显示的消息",
            required=True,
            min_length=1,
            max_length=100
        ),
        SkillParameter(
            name="count",
            type="number",
            description="重复次数",
            required=False,
            default=1,
            minimum=1,
            maximum=10
        )
    ]
    
    example_skill_obj = Skill(
        metadata=example_metadata,
        parameters=example_parameters,
        execute_func=example_skill
    )
    
    # 手动添加到加载器
    skill_manager.loader._loaded_skills["example_skill"] = example_skill_obj
    print("   - 示例技能已创建")
    
    # 4. 列出所有技能
    print("\n4. 列出所有技能:")
    skills = skill_manager.list_skills()
    if skills:
        for skill_obj in skills:
            print(f"   - {skill_obj.name} ({skill_obj.metadata.version})")
            print(f"     描述: {skill_obj.metadata.description}")
            print(f"     分类: {skill_obj.metadata.category}")
            print(f"     标签: {', '.join(skill_obj.metadata.tags)}")
    else:
        print("   - 没有发现技能")
    
    # 5. 执行示例技能
    print("\n5. 执行示例技能:")
    params = {
        "message": "Hello, Symphony! ",
        "count": 3
    }
    print(f"   - 参数: {params}")
    
    result = skill_manager.execute_skill("example_skill", params)
    print(f"   - 成功: {result.success}")
    print(f"   - 执行时间: {result.execution_time:.3f}秒")
    
    if result.success:
        print(f"   - 结果: {result.data}")
    else:
        print(f"   - 错误: {result.error}")
    
    # 6. 显示统计信息
    print("\n6. 技能统计:")
    stats = skill_manager.get_skill_stats("example_skill")
    if stats:
        print(f"   - 总调用次数: {stats.total_calls}")
        print(f"   - 成功次数: {stats.success_count}")
        print(f"   - 失败次数: {stats.failure_count}")
        print(f"   - 平均执行时间: {stats.avg_execution_time:.3f}秒")
    
    # 7. 测试参数验证
    print("\n7. 测试参数验证（错误参数）:")
    invalid_params = {
        "message": "",  # 太短
        "count": 100    # 超过最大值
    }
    result = skill_manager.execute_skill("example_skill", invalid_params)
    print(f"   - 成功: {result.success}")
    if not result.success:
        print(f"   - 错误: {result.error}")
    
    # 8. 测试搜索功能
    print("\n8. 搜索技能（关键词: 'example'）:")
    search_results = skill_manager.search_skills("example")
    if search_results:
        for skill_obj in search_results:
            print(f"   - 找到: {skill_obj.name}")
    
    # 9. 清理
    print("\n9. 清理...")
    skill_manager.shutdown()
    
    print("\n" + "=" * 60)
    print("示例演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()