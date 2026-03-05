#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模型协作系统 - MCP (Model Context Protocol) 工具管理器
实现MCP工具的发现、注册、调用、参数验证和错误处理
与 fault_tolerance.py 无缝集成
"""

import time
import logging
import threading
import json
from enum import Enum
from typing import (
    Any, Callable, Dict, List, Optional, Tuple, Type, Union, Set
)
from dataclasses import dataclass, field
from functools import wraps
from inspect import signature, Parameter
import re

# 导入故障处理模块
from fault_tolerance import (
    Retrier, CircuitBreaker, FallbackManager, FailoverManager,
    SmartClient, RetryConfig, CircuitBreakerConfig, TimeoutConfig,
    ModelConfig, HealthChecker, HealthCheckConfig,
    RetryError, CircuitOpenError, FallbackError,
    CircuitState, HealthStatus, ErrorType, classify_error
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

class MCPError(Exception):
    """MCP工具基础异常"""
    pass


class ToolNotFoundError(MCPError):
    """工具未找到异常"""
    pass


class ToolExecutionError(MCPError):
    """工具执行异常"""
    pass


class ParameterValidationError(MCPError):
    """参数验证异常"""
    pass


class ToolAlreadyRegisteredError(MCPError):
    """工具已注册异常"""
    pass


class ToolDisabledError(MCPError):
    """工具已禁用异常"""
    pass


# =============================================================================
# 枚举类型
# =============================================================================

class ToolStatus(Enum):
    """工具状态"""
    ACTIVE = "active"          # 活跃，可用
    DISABLED = "disabled"      # 禁用
    DEPRECATED = "deprecated"  # 已弃用
    MAINTENANCE = "maintenance"  # 维护中


class ParameterType(Enum):
    """参数类型"""
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    ANY = "any"


# =============================================================================
# 数据类
# =============================================================================

@dataclass
class ParameterSchema:
    """参数模式定义"""
    name: str
    type: ParameterType
    required: bool = True
    description: str = ""
    default: Any = None
    enum: List[Any] = field(default_factory=list)
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    items: Optional['ParameterSchema'] = None  # 数组元素类型
    properties: Optional[Dict[str, 'ParameterSchema']] = None  # 对象属性


@dataclass
class ToolSchema:
    """工具模式定义"""
    name: str
    description: str
    parameters: List[ParameterSchema]
    returns: ParameterSchema
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    author: str = ""


@dataclass
class ToolMetrics:
    """工具执行指标"""
    total_calls: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_latency: float = 0.0
    avg_latency: float = 0.0
    min_latency: float = float('inf')
    max_latency: float = 0.0
    error_counts: Dict[ErrorType, int] = field(default_factory=dict)
    last_called: Optional[float] = None
    last_success: Optional[float] = None
    last_failure: Optional[float] = None


@dataclass
class ToolRegistration:
    """工具注册信息"""
    schema: ToolSchema
    func: Callable
    status: ToolStatus = ToolStatus.ACTIVE
    metrics: ToolMetrics = field(default_factory=ToolMetrics)
    use_retries: bool = True
    use_circuit_breaker: bool = True
    use_failover: bool = False
    pool_name: str = "default"
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolExecutionResult:
    """工具执行结果"""
    tool_name: str
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    error_type: Optional[ErrorType] = None
    latency: float = 0.0
    retry_count: int = 0
    used_fallback: bool = False
    timestamp: float = field(default_factory=time.time)


# =============================================================================
# 参数验证器
# =============================================================================

class ParameterValidator:
    """
    参数验证器 - 验证工具输入参数
    """
    
    @staticmethod
    def validate_type(value: Any, param_type: ParameterType) -> Tuple[bool, Optional[str]]:
        """验证参数类型"""
        if param_type == ParameterType.ANY:
            return True, None
        
        type_checks = {
            ParameterType.STRING: lambda v: isinstance(v, str),
            ParameterType.INTEGER: lambda v: isinstance(v, int) and not isinstance(v, bool),
            ParameterType.NUMBER: lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            ParameterType.BOOLEAN: lambda v: isinstance(v, bool),
            ParameterType.ARRAY: lambda v: isinstance(v, (list, tuple)),
            ParameterType.OBJECT: lambda v: isinstance(v, dict),
        }
        
        checker = type_checks.get(param_type)
        if checker and not checker(value):
            return False, f"期望类型 {param_type.value}，实际类型 {type(value).__name__}"
        
        return True, None
    
    @staticmethod
    def validate_enum(value: Any, enum_values: List[Any]) -> Tuple[bool, Optional[str]]:
        """验证枚举值"""
        if enum_values and value not in enum_values:
            return False, f"值必须在 {enum_values} 中，当前值: {value}"
        return True, None
    
    @staticmethod
    def validate_range(value: Union[int, float], minimum: Optional[Union[int, float]], 
                       maximum: Optional[Union[int, float]]) -> Tuple[bool, Optional[str]]:
        """验证数值范围"""
        if minimum is not None and value < minimum:
            return False, f"值不能小于 {minimum}，当前值: {value}"
        if maximum is not None and value > maximum:
            return False, f"值不能大于 {maximum}，当前值: {value}"
        return True, None
    
    @staticmethod
    def validate_length(value: str, min_length: Optional[int], 
                        max_length: Optional[int]) -> Tuple[bool, Optional[str]]:
        """验证字符串长度"""
        length = len(value)
        if min_length is not None and length < min_length:
            return False, f"长度不能小于 {min_length}，当前长度: {length}"
        if max_length is not None and length > max_length:
            return False, f"长度不能大于 {max_length}，当前长度: {length}"
        return True, None
    
    @staticmethod
    def validate_pattern(value: str, pattern: Optional[str]) -> Tuple[bool, Optional[str]]:
        """验证正则表达式模式"""
        if pattern and not re.match(pattern, value):
            return False, f"值不匹配模式 '{pattern}'"
        return True, None
    
    @staticmethod
    def validate_array(value: List[Any], items_schema: Optional[ParameterSchema]) -> Tuple[bool, Optional[str]]:
        """验证数组元素"""
        if not items_schema:
            return True, None
        
        for i, item in enumerate(value):
            valid, error = ParameterValidator.validate_parameter(item, items_schema)
            if not valid:
                return False, f"数组元素 [{i}]: {error}"
        
        return True, None
    
    @staticmethod
    def validate_object(value: Dict[str, Any], properties: Optional[Dict[str, ParameterSchema]]) -> Tuple[bool, Optional[str]]:
        """验证对象属性"""
        if not properties:
            return True, None
        
        for prop_name, prop_schema in properties.items():
            if prop_schema.required and prop_name not in value:
                return False, f"缺少必需属性: {prop_name}"
            
            if prop_name in value:
                valid, error = ParameterValidator.validate_parameter(value[prop_name], prop_schema)
                if not valid:
                    return False, f"属性 '{prop_name}': {error}"
        
        return True, None
    
    @staticmethod
    def validate_parameter(value: Any, schema: ParameterSchema) -> Tuple[bool, Optional[str]]:
        """验证单个参数"""
        # 1. 检查是否必需
        if schema.required and value is None:
            return False, f"参数 '{schema.name}' 是必需的"
        
        # 如果值为None且不是必需的，跳过其他验证
        if value is None:
            return True, None
        
        # 2. 验证类型
        valid, error = ParameterValidator.validate_type(value, schema.type)
        if not valid:
            return False, f"参数 '{schema.name}': {error}"
        
        # 3. 验证枚举
        valid, error = ParameterValidator.validate_enum(value, schema.enum)
        if not valid:
            return False, f"参数 '{schema.name}': {error}"
        
        # 4. 验证数值范围
        if schema.type in [ParameterType.INTEGER, ParameterType.NUMBER]:
            valid, error = ParameterValidator.validate_range(value, schema.minimum, schema.maximum)
            if not valid:
                return False, f"参数 '{schema.name}': {error}"
        
        # 5. 验证字符串长度和模式
        if schema.type == ParameterType.STRING:
            valid, error = ParameterValidator.validate_length(value, schema.min_length, schema.max_length)
            if not valid:
                return False, f"参数 '{schema.name}': {error}"
            
            valid, error = ParameterValidator.validate_pattern(value, schema.pattern)
            if not valid:
                return False, f"参数 '{schema.name}': {error}"
        
        # 6. 验证数组
        if schema.type == ParameterType.ARRAY:
            valid, error = ParameterValidator.validate_array(value, schema.items)
            if not valid:
                return False, f"参数 '{schema.name}': {error}"
        
        # 7. 验证对象
        if schema.type == ParameterType.OBJECT:
            valid, error = ParameterValidator.validate_object(value, schema.properties)
            if not valid:
                return False, f"参数 '{schema.name}': {error}"
        
        return True, None
    
    @staticmethod
    def validate_parameters(parameters: Dict[str, Any], 
                           schemas: List[ParameterSchema]) -> Tuple[bool, Optional[str]]:
        """验证所有参数"""
        # 创建参数字典以便快速查找
        schema_dict = {schema.name: schema for schema in schemas}
        
        # 检查所有必需参数
        for schema in schemas:
            if schema.required and schema.name not in parameters:
                return False, f"缺少必需参数: {schema.name}"
        
        # 验证每个提供的参数
        for param_name, param_value in parameters.items():
            if param_name not in schema_dict:
                logger.warning(f"未知参数: {param_name}")
                continue
            
            valid, error = ParameterValidator.validate_parameter(param_value, schema_dict[param_name])
            if not valid:
                return False, error
        
        return True, None


# =============================================================================
# MCP工具管理器
# =============================================================================

class MCPManager:
    """
    MCP工具管理器 - 管理MCP工具的注册、发现和调用
    与 fault_tolerance.py 无缝集成
    """
    
    def __init__(
        self,
        smart_client: Optional[SmartClient] = None,
        retrier: Optional[Retrier] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        fallback_manager: Optional[FallbackManager] = None,
        failover_manager: Optional[FailoverManager] = None
    ):
        # 初始化容错组件
        if smart_client:
            self.smart_client = smart_client
        else:
            self.retrier = retrier or Retrier()
            self.circuit_breaker = circuit_breaker or CircuitBreaker(name="mcp_tools")
            self.fallback_manager = fallback_manager or FallbackManager()
            self.failover_manager = failover_manager or FailoverManager()
            
            self.smart_client = SmartClient(
                retrier=self.retrier,
                circuit_breaker=self.circuit_breaker,
                fallback_manager=self.fallback_manager,
                failover_manager=self.failover_manager
            )
        
        # 工具注册表
        self._tools: Dict[str, ToolRegistration] = {}
        self._lock = threading.RLock()
        
        # 参数验证器
        self.validator = ParameterValidator()
        
        logger.info("MCP工具管理器已初始化")
    
    # -------------------------------------------------------------------------
    # 工具注册
    # -------------------------------------------------------------------------
    
    def register_tool(
        self,
        schema: ToolSchema,
        func: Callable,
        status: ToolStatus = ToolStatus.ACTIVE,
        use_retries: bool = True,
        use_circuit_breaker: bool = True,
        use_failover: bool = False,
        pool_name: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ToolRegistration:
        """
        注册MCP工具
        
        Args:
            schema: 工具模式定义
            func: 工具实现函数
            status: 工具状态
            use_retries: 是否使用重试机制
            use_circuit_breaker: 是否使用熔断器
            use_failover: 是否使用故障转移
            pool_name: 故障转移池名称
            metadata: 额外元数据
        
        Returns:
            工具注册信息
        """
        with self._lock:
            if schema.name in self._tools:
                raise ToolAlreadyRegisteredError(f"工具 '{schema.name}' 已注册")
            
            registration = ToolRegistration(
                schema=schema,
                func=func,
                status=status,
                use_retries=use_retries,
                use_circuit_breaker=use_circuit_breaker,
                use_failover=use_failover,
                pool_name=pool_name,
                metadata=metadata or {}
            )
            
            self._tools[schema.name] = registration
            logger.info(f"已注册工具: {schema.name} v{schema.version}")
            
            return registration
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        注销工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            是否成功注销
        """
        with self._lock:
            if tool_name in self._tools:
                del self._tools[tool_name]
                logger.info(f"已注销工具: {tool_name}")
                return True
            return False
    
    def update_tool_status(self, tool_name: str, status: ToolStatus) -> bool:
        """
        更新工具状态
        
        Args:
            tool_name: 工具名称
            status: 新状态
        
        Returns:
            是否成功更新
        """
        with self._lock:
            if tool_name in self._tools:
                self._tools[tool_name].status = status
                logger.info(f"工具 '{tool_name}' 状态更新为: {status.value}")
                return True
            return False
    
    # -------------------------------------------------------------------------
    # 工具发现
    # -------------------------------------------------------------------------
    
    def list_tools(
        self,
        category: Optional[str] = None,
        status: Optional[ToolStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[ToolSchema]:
        """
        列出工具
        
        Args:
            category: 按类别筛选
            status: 按状态筛选
            tags: 按标签筛选
        
        Returns:
            工具模式列表
        """
        with self._lock:
            tools = []
            
            for registration in self._tools.values():
                schema = registration.schema
                
                # 应用筛选条件
                if category and schema.category != category:
                    continue
                if status and registration.status != status:
                    continue
                if tags and not any(tag in schema.tags for tag in tags):
                    continue
                
                tools.append(schema)
            
            return tools
    
    def get_tool_schema(self, tool_name: str) -> Optional[ToolSchema]:
        """
        获取工具模式
        
        Args:
            tool_name: 工具名称
        
        Returns:
            工具模式，如果不存在返回None
        """
        with self._lock:
            registration = self._tools.get(tool_name)
            return registration.schema if registration else None
    
    def get_tool_registration(self, tool_name: str) -> Optional[ToolRegistration]:
        """
        获取工具注册信息
        
        Args:
            tool_name: 工具名称
        
        Returns:
            工具注册信息，如果不存在返回None
        """
        with self._lock:
            return self._tools.get(tool_name)
    
    def tool_exists(self, tool_name: str) -> bool:
        """
        检查工具是否存在
        
        Args:
            tool_name: 工具名称
        
        Returns:
            工具是否存在
        """
        with self._lock:
            return tool_name in self._tools
    
    # -------------------------------------------------------------------------
    # 工具调用
    # -------------------------------------------------------------------------
    
    def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        use_retries: Optional[bool] = None,
        use_circuit_breaker: Optional[bool] = None,
        use_failover: Optional[bool] = None,
        fallback_context: Optional[Dict] = None
    ) -> ToolExecutionResult:
        """
        执行工具
        
        Args:
            tool_name: 工具名称
            parameters: 参数字典
            use_retries: 是否使用重试（覆盖工具配置）
            use_circuit_breaker: 是否使用熔断器（覆盖工具配置）
            use_failover: 是否使用故障转移（覆盖工具配置）
            fallback_context: 降级上下文
        
        Returns:
            工具执行结果
        """
        start_time = time.time()
        retry_count = 0
        used_fallback = False
        
        with self._lock:
            registration = self._tools.get(tool_name)
        
        if not registration:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=ToolNotFoundError(f"工具 '{tool_name}' 未找到"),
                error_type=ErrorType.CLIENT_ERROR,
                latency=time.time() - start_time
            )
        
        if registration.status != ToolStatus.ACTIVE:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=ToolDisabledError(f"工具 '{tool_name}' 处于 {registration.status.value} 状态"),
                error_type=ErrorType.CLIENT_ERROR,
                latency=time.time() - start_time
            )
        
        # 验证参数
        valid, error = self.validator.validate_parameters(parameters, registration.schema.parameters)
        if not valid:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                error=ParameterValidationError(error),
                error_type=ErrorType.CLIENT_ERROR,
                latency=time.time() - start_time
            )
        
        # 确定是否使用容错机制
        use_retries = use_retries if use_retries is not None else registration.use_retries
        use_circuit_breaker = use_circuit_breaker if use_circuit_breaker is not None else registration.use_circuit_breaker
        use_failover = use_failover if use_failover is not None else registration.use_failover
        
        try:
            # 定义包装函数
            def wrapped_func():
                return registration.func(**parameters)
            
            # 使用智能客户端执行
            result = self.smart_client.execute(
                wrapped_func,
                model_id=tool_name if use_failover else None,
                pool_name=registration.pool_name,
                use_retries=use_retries,
                use_circuit_breaker=use_circuit_breaker,
                use_failover=use_failover,
                fallback_context=fallback_context
            )
            
            latency = time.time() - start_time
            
            # 更新指标
            self._update_metrics(tool_name, True, latency)
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=True,
                result=result,
                latency=latency,
                retry_count=retry_count,
                used_fallback=used_fallback
            )
            
        except Exception as e:
            latency = time.time() - start_time
            error_type = classify_error(e)
            
            # 更新指标
            self._update_metrics(tool_name, False, latency, error_type)
            
            # 尝试降级
            try:
                fallback_result = self.fallback_manager.execute_fallback(
                    error_type, fallback_context, **parameters
                )
                used_fallback = True
                return ToolExecutionResult(
                    tool_name=tool_name,
                    success=True,
                    result=fallback_result,
                    latency=latency,
                    retry_count=retry_count,
                    used_fallback=used_fallback
                )
            except FallbackError:
                pass
            
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=e,
                error_type=error_type,
                latency=latency,
                retry_count=retry_count,
                used_fallback=used_fallback
            )
    
    def _update_metrics(
        self,
        tool_name: str,
        success: bool,
        latency: float,
        error_type: Optional[ErrorType] = None
    ):
        """更新工具指标"""
        with self._lock:
            if tool_name not in self._tools:
                return
            
            metrics = self._tools[tool_name].metrics
            metrics.total_calls += 1
            metrics.total_latency += latency
            metrics.avg_latency = metrics.total_latency / metrics.total_calls
            metrics.min_latency = min(metrics.min_latency, latency)
            metrics.max_latency = max(metrics.max_latency, latency)
            metrics.last_called = time.time()
            
            if success:
                metrics.success_count += 1
                metrics.last_success = time.time()
            else:
                metrics.failure_count += 1
                metrics.last_failure = time.time()
                if error_type:
                    metrics.error_counts[error_type] = metrics.error_counts.get(error_type, 0) + 1
    
    # -------------------------------------------------------------------------
    # 工具指标和统计
    # -------------------------------------------------------------------------
    
    def get_tool_metrics(self, tool_name: str) -> Optional[ToolMetrics]:
        """
        获取工具指标
        
        Args:
            tool_name: 工具名称
        
        Returns:
            工具指标
        """
        with self._lock:
            registration = self._tools.get(tool_name)
            return registration.metrics if registration else None
    
    def get_all_metrics(self) -> Dict[str, ToolMetrics]:
        """
        获取所有工具指标
        
        Returns:
            工具名称到指标的映射
        """
        with self._lock:
            return {name: reg.metrics for name, reg in self._tools.items()}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取管理器统计信息
        
        Returns:
            统计信息字典
        """
        with self._lock:
            total_tools = len(self._tools)
            active_tools = sum(1 for reg in self._tools.values() 
                              if reg.status == ToolStatus.ACTIVE)
            total_calls = sum(reg.metrics.total_calls for reg in self._tools.values())
            total_success = sum(reg.metrics.success_count for reg in self._tools.values())
            total_failure = sum(reg.metrics.failure_count for reg in self._tools.values())
            
            return {
                "total_tools": total_tools,
                "active_tools": active_tools,
                "total_calls": total_calls,
                "total_success": total_success,
                "total_failure": total_failure,
                "success_rate": (total_success / total_calls * 100) if total_calls > 0 else 0,
                "tools": {
                    name: {
                        "status": reg.status.value,
                        "version": reg.schema.version,
                        "category": reg.schema.category,
                        "metrics": {
                            "total_calls": reg.metrics.total_calls,
                            "success_count": reg.metrics.success_count,
                            "failure_count": reg.metrics.failure_count,
                            "avg_latency": reg.metrics.avg_latency
                        }
                    }
                    for name, reg in self._tools.items()
                }
            }
    
    def reset_metrics(self, tool_name: Optional[str] = None):
        """
        重置指标
        
        Args:
            tool_name: 工具名称，如果为None则重置所有工具
        """
        with self._lock:
            if tool_name:
                if tool_name in self._tools:
                    self._tools[tool_name].metrics = ToolMetrics()
            else:
                for reg in self._tools.values():
                    reg.metrics = ToolMetrics()
    
    # -------------------------------------------------------------------------
    # 便捷装饰器
    # -------------------------------------------------------------------------
    
    def tool(
        self,
        name: str,
        description: str,
        parameters: List[ParameterSchema],
        returns: ParameterSchema,
        category: str = "general",
        tags: Optional[List[str]] = None,
        version: str = "1.0.0",
        author: str = "",
        use_retries: bool = True,
        use_circuit_breaker: bool = True,
        use_failover: bool = False,
        pool_name: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        工具注册装饰器
        
        Args:
            name: 工具名称
            description: 工具描述
            parameters: 参数模式列表
            returns: 返回值模式
            category: 工具类别
            tags: 标签列表
            version: 版本号
            author: 作者
            use_retries: 是否使用重试
            use_circuit_breaker: 是否使用熔断器
            use_failover: 是否使用故障转移
            pool_name: 故障转移池名称
            metadata: 额外元数据
        """
        def decorator(func: Callable):
            schema = ToolSchema(
                name=name,
                description=description,
                parameters=parameters,
                returns=returns,
                category=category,
                tags=tags or [],
                version=version,
                author=author
            )
            
            self.register_tool(
                schema=schema,
                func=func,
                use_retries=use_retries,
                use_circuit_breaker=use_circuit_breaker,
                use_failover=use_failover,
                pool_name=pool_name,
                metadata=metadata
            )
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        return decorator


# =============================================================================
# 便捷函数
# =============================================================================

def create_mcp_manager(
    retry_config: Optional[RetryConfig] = None,
    circuit_config: Optional[CircuitBreakerConfig] = None,
    health_config: Optional[HealthCheckConfig] = None
) -> MCPManager:
    """
    创建MCP管理器的便捷函数
    
    Args:
        retry_config: 重试配置
        circuit_config: 熔断器配置
        health_config: 健康检查配置
    
    Returns:
        MCP管理器实例
    """
    retrier = Retrier(retry_config) if retry_config else Retrier()
    circuit_breaker = CircuitBreaker(circuit_config, "mcp_tools") if circuit_config else CircuitBreaker(name="mcp_tools")
    health_checker = HealthChecker(health_config) if health_config else HealthChecker()
    failover_manager = FailoverManager(health_checker)
    fallback_manager = FallbackManager()
    
    smart_client = SmartClient(
        retrier=retrier,
        circuit_breaker=circuit_breaker,
        fallback_manager=fallback_manager,
        failover_manager=failover_manager
    )
    
    return MCPManager(smart_client=smart_client)


# =============================================================================
# 示例工具（用于演示）
# =============================================================================

def example_add(a: int, b: int) -> int:
    """示例加法工具"""
    return a + b


def example_uppercase(text: str) -> str:
    """示例大写转换工具"""
    return text.upper()


def example_slow_function(delay: float) -> str:
    """示例慢函数（用于测试超时和重试）"""
    time.sleep(delay)
    return f"完成，耗时 {delay} 秒"


# =============================================================================
# 主函数（示例）
# =============================================================================

def main():
    """示例用法"""
    print("=" * 60)
    print("MCP工具管理器 - 示例演示")
    print("=" * 60)
    
    # 1. 创建MCP管理器
    print("\n1. 创建MCP管理器...")
    mcp_manager = create_mcp_manager()
    print("   - MCP管理器已创建")
    
    # 2. 注册工具
    print("\n2. 注册示例工具...")
    
    # 工具1: 加法
    add_schema = ToolSchema(
        name="add",
        description="计算两个数的和",
        parameters=[
            ParameterSchema(
                name="a",
                type=ParameterType.INTEGER,
                required=True,
                description="第一个数",
                minimum=0,
                maximum=1000
            ),
            ParameterSchema(
                name="b",
                type=ParameterType.INTEGER,
                required=True,
                description="第二个数",
                minimum=0,
                maximum=1000
            )
        ],
        returns=ParameterSchema(
            name="result",
            type=ParameterType.INTEGER,
            description="两数之和"
        ),
        category="math",
        tags=["calculation", "basic"]
    )
    
    mcp_manager.register_tool(add_schema, example_add)
    print("   - 已注册工具: add")
    
    # 工具2: 大写转换
    uppercase_schema = ToolSchema(
        name="uppercase",
        description="将文本转换为大写",
        parameters=[
            ParameterSchema(
                name="text",
                type=ParameterType.STRING,
                required=True,
                description="输入文本",
                min_length=1,
                max_length=1000
            )
        ],
        returns=ParameterSchema(
            name="result",
            type=ParameterType.STRING,
            description="大写文本"
        ),
        category="text",
        tags=["string", "transform"]
    )
    
    mcp_manager.register_tool(uppercase_schema, example_uppercase)
    print("   - 已注册工具: uppercase")
    
    # 工具3: 慢函数
    slow_schema = ToolSchema(
        name="slow_function",
        description="延迟执行的函数（用于测试）",
        parameters=[
            ParameterSchema(
                name="delay",
                type=ParameterType.NUMBER,
                required=True,
                description="延迟秒数",
                minimum=0.1,
                maximum=10.0
            )
        ],
        returns=ParameterSchema(
            name="result",
            type=ParameterType.STRING,
            description="执行结果"
        ),
        category="test",
        tags=["demo", "timeout"]
    )
    
    mcp_manager.register_tool(slow_schema, example_slow_function, use_retries=False)
    print("   - 已注册工具: slow_function")
    
    # 3. 列出工具
    print("\n3. 列出所有工具:")
    tools = mcp_manager.list_tools()
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")
    
    # 4. 执行工具
    print("\n4. 执行工具测试:")
    
    # 测试加法
    print("\n   测试 add(5, 3):")
    result = mcp_manager.execute_tool("add", {"a": 5, "b": 3})
    print(f"      成功: {result.success}")
    if result.success:
        print(f"      结果: {result.result}")
    print(f"      耗时: {result.latency:.3f}秒")
    
    # 测试大写转换
    print("\n   测试 uppercase('hello world'):")
    result = mcp_manager.execute_tool("uppercase", {"text": "hello world"})
    print(f"      成功: {result.success}")
    if result.success:
        print(f"      结果: {result.result}")
    print(f"      耗时: {result.latency:.3f}秒")
    
    # 测试参数验证错误
    print("\n   测试参数验证错误 (add('not a number', 3)):")
    result = mcp_manager.execute_tool("add", {"a": "not a number", "b": 3})
    print(f"      成功: {result.success}")
    if not result.success:
        print(f"      错误: {result.error}")
    
    # 测试不存在的工具
    print("\n   测试不存在的工具 (unknown_tool):")
    result = mcp_manager.execute_tool("unknown_tool", {})
    print(f"      成功: {result.success}")
    if not result.success:
        print(f"      错误: {result.error}")
    
    # 5. 显示统计
    print("\n5. 统计信息:")
    stats = mcp_manager.get_stats()
    print(f"   - 总工具数: {stats['total_tools']}")
    print(f"   - 活跃工具数: {stats['active_tools']}")
    print(f"   - 总调用次数: {stats['total_calls']}")
    print(f"   - 成功次数: {stats['total_success']}")
    print(f"   - 失败次数: {stats['total_failure']}")
    print(f"   - 成功率: {stats['success_rate']:.1f}%")
    
    print("\n6. 工具详细统计:")
    for tool_name, tool_info in stats['tools'].items():
        print(f"   - {tool_name}:")
        print(f"     状态: {tool_info['status']}")
        print(f"     版本: {tool_info['version']}")
        print(f"     类别: {tool_info['category']}")
        print(f"     调用次数: {tool_info['metrics']['total_calls']}")
    
    print("\n" + "=" * 60)
    print("示例演示完成！")
    print("=" * 60)