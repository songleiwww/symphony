#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘v4.0进化引擎 - 安全控制模块
QingQiu Evolution Engine v4.0 - Safety Control Module

安全专家: 陈浩然
设计目标: 实现三层安全控制架构，保障系统运行的安全性、可靠性和可追溯性
"""

import asyncio
import json
import time
import hashlib
import hmac
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set, Callable, Union
import uuid
import logging
import re
from collections import defaultdict
import traceback

# 导入核心类型
from qinqiu_evolution_engine import ExecutionResult, ExecutionStatus

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """安全级别枚举"""
    LOW = "low"           # 低安全级别，仅基础检查
    MEDIUM = "medium"     # 中等安全级别，常规检查
    HIGH = "high"         # 高安全级别，严格检查
    CRITICAL = "critical" # 关键安全级别，最严格检查


class RiskLevel(Enum):
    """风险级别枚举"""
    NEGLIGIBLE = "negligible"  # 可忽略，无影响
    LOW = "low"                # 低风险，轻微影响
    MEDIUM = "medium"          # 中风险，需要关注
    HIGH = "high"              # 高风险，需要处理
    CRITICAL = "critical"      # 严重风险，必须立即处理


class CircuitBreakerState(Enum):
    """熔断器状态枚举"""
    CLOSED = "closed"      # 关闭状态：正常运行
    OPEN = "open"          # 打开状态：熔断触发，拒绝请求
    HALF_OPEN = "half_open" # 半开状态：尝试恢复服务


@dataclass
class SecurityPolicy:
    """安全策略数据类"""
    policy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    rules: List[Dict[str, Any]] = field(default_factory=list)
    action: str = "block"  # block, warn, log
    enabled: bool = True
    priority: int = 100
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    created_by: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'policy_id': self.policy_id,
            'name': self.name,
            'description': self.description,
            'security_level': self.security_level.value,
            'rules': self.rules,
            'action': self.action,
            'enabled': self.enabled,
            'priority': self.priority,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by
        }


@dataclass
class SecurityEvent:
    """安全事件数据类"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    description: str = ""
    source: str = ""
    resource: str = ""
    user: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    handled: bool = False
    handling_result: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'risk_level': self.risk_level.value,
            'description': self.description,
            'source': self.source,
            'resource': self.resource,
            'user': self.user,
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'handled': self.handled,
            'handling_result': self.handling_result
        }


@dataclass
class AuditLog:
    """审计日志数据类"""
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation: str = ""
    operator: str = ""
    resource_type: str = ""
    resource_id: str = ""
    action: str = ""
    status: str = ""
    request: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    ip_address: str = ""
    user_agent: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration: Optional[float] = None
    
    def complete(self, status: str, response: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> None:
        """完成审计日志记录"""
        self.status = status
        self.response = response
        self.error = error
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'log_id': self.log_id,
            'operation': self.operation,
            'operator': self.operator,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'action': self.action,
            'status': self.status,
            'request': self.request,
            'response': self.response,
            'error': self.error,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration
        }


@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5  # 失败次数阈值
    recovery_timeout: int = 30  # 恢复超时时间（秒）
    half_open_max_calls: int = 3  # 半开状态允许的最大请求数
    failure_window: int = 60  # 失败统计窗口（秒）


class BoundaryControlLayer:
    """
    第一层：边界控制层
    Boundary Control Layer
    
    负责所有输入输出的安全校验、过滤和 sanitization，是系统的第一道防线
    """
    
    def __init__(self, safety_system: 'SafetyControlSystem'):
        self.safety_system = safety_system
        self.policies: Dict[str, SecurityPolicy] = {}  # 安全策略
        self.input_filters: List[Callable] = []  # 输入过滤器列表
        self.output_filters: List[Callable] = []  # 输出过滤器列表
        self.allowed_patterns: List[re.Pattern] = []  # 允许的输入模式
        self.blocked_patterns: List[re.Pattern] = []  # 禁止的输入模式
        
        # 初始化默认规则
        self._init_default_policies()
        self._init_default_patterns()
        
        logger.info("边界控制层已初始化")
    
    def _init_default_policies(self) -> None:
        """初始化默认安全策略"""
        # 输入验证策略
        input_policy = SecurityPolicy(
            name="输入验证策略",
            description="对所有输入数据进行格式和内容验证",
            security_level=SecurityLevel.MEDIUM,
            action="block",
            priority=100,
            rules=[
                {'type': 'length_check', 'max_length': 100000},
                {'type': 'format_check', 'allowed_formats': ['json', 'text', 'markdown']},
                {'type': 'content_check', 'blocked_content': ['恶意代码', '攻击指令', '敏感信息']}
            ]
        )
        self.add_policy(input_policy)
        
        # 输出过滤策略
        output_policy = SecurityPolicy(
            name="输出过滤策略",
            description="对所有输出数据进行敏感信息过滤",
            security_level=SecurityLevel.HIGH,
            action="filter",
            priority=90,
            rules=[
                {'type': 'sensitive_data_filter', 'filters': ['api_key', 'password', 'token', 'private_key']},
                {'type': 'content_moderation', 'blocked_content': ['暴力', '色情', '违法内容']}
            ]
        )
        self.add_policy(output_policy)
    
    def _init_default_patterns(self) -> None:
        """初始化默认的匹配模式"""
        # 禁止的模式
        blocked_patterns = [
            r'(?i)(rm\s+-rf|del\s+/f/s/q|format\s+[a-z]:)',  # 危险系统命令
            r'(?i)(eval\(|exec\(|system\(|passthru\(|shell_exec\()',  # 代码执行函数
            r'(?i)(<script|javascript:|vbscript:)',  # 脚本注入
            r'(?i)(select|insert|update|delete|drop|truncate).*from',  # SQL注入
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # 邮箱地址
            r'1[3-9]\d{9}',  # 手机号码
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # 邮箱模式
        ]
        
        for pattern in blocked_patterns:
            self.blocked_patterns.append(re.compile(pattern))
    
    def add_policy(self, policy: SecurityPolicy) -> None:
        """添加安全策略"""
        self.policies[policy.policy_id] = policy
        # 按优先级排序
        self.policies = dict(sorted(
            self.policies.items(),
            key=lambda x: x[1].priority,
            reverse=True
        ))
        logger.info(f"已添加安全策略: {policy.name} (ID: {policy.policy_id})")
    
    def remove_policy(self, policy_id: str) -> bool:
        """移除安全策略"""
        if policy_id in self.policies:
            del self.policies[policy_id]
            logger.info(f"已移除安全策略: {policy_id}")
            return True
        return False
    
    def add_input_filter(self, filter_func: Callable) -> None:
        """添加输入过滤器"""
        self.input_filters.append(filter_func)
        logger.info(f"已添加输入过滤器: {filter_func.__name__}")
    
    def add_output_filter(self, filter_func: Callable) -> None:
        """添加输出过滤器"""
        self.output_filters.append(filter_func)
        logger.info(f"已添加输出过滤器: {filter_func.__name__}")
    
    async def validate_input(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        验证输入数据
        :return: (是否通过, 结果详情)
        """
        context = context or {}
        input_str = str(input_data)
        
        # 1. 应用所有输入过滤器
        for filter_func in self.input_filters:
            try:
                input_data = await filter_func(input_data, context)
            except Exception as e:
                logger.error(f"输入过滤器执行失败 {filter_func.__name__}: {str(e)}")
                return False, {
                    'error': f"输入过滤失败: {str(e)}",
                    'filter': filter_func.__name__
                }
        
        # 2. 检查禁止模式
        for pattern in self.blocked_patterns:
            if pattern.search(input_str):
                event = SecurityEvent(
                    event_type="malicious_input_detected",
                    risk_level=RiskLevel.HIGH,
                    description=f"检测到恶意输入模式: {pattern.pattern}",
                    source="boundary_control",
                    resource="input_validation",
                    metadata={
                        'input': input_str[:1000],  # 截断避免过大
                        'pattern': pattern.pattern,
                        'context': context
                    }
                )
                await self.safety_system.audit_layer.log_security_event(event)
                
                return False, {
                    'error': "输入包含禁止内容",
                    'pattern': pattern.pattern,
                    'risk_level': RiskLevel.HIGH.value
                }
        
        # 3. 应用所有安全策略
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            
            policy_passed, policy_result = await self._apply_policy(policy, input_data, context, is_input=True)
            if not policy_passed:
                if policy.action == "block":
                    event = SecurityEvent(
                        event_type="policy_violation",
                        risk_level=self._get_risk_level(policy.security_level),
                        description=f"违反安全策略: {policy.name}",
                        source="boundary_control",
                        resource="input_validation",
                        metadata={
                            'policy_id': policy.policy_id,
                            'policy_name': policy.name,
                            'input': input_str[:1000],
                            'result': policy_result,
                            'context': context
                        }
                    )
                    await self.safety_system.audit_layer.log_security_event(event)
                    
                    return False, {
                        'error': f"违反安全策略: {policy.name}",
                        'policy_id': policy.policy_id,
                        'policy_result': policy_result
                    }
                elif policy.action == "warn":
                    logger.warning(f"安全策略警告: {policy.name} - {policy_result}")
        
        # 所有检查通过
        return True, {
            'filtered_data': input_data,
            'message': "输入验证通过"
        }
    
    async def validate_output(self, output_data: Any, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        验证输出数据
        :return: (是否通过, 结果详情)
        """
        context = context or {}
        original_output = output_data
        
        # 1. 应用所有输出过滤器
        for filter_func in self.output_filters:
            try:
                output_data = await filter_func(output_data, context)
            except Exception as e:
                logger.error(f"输出过滤器执行失败 {filter_func.__name__}: {str(e)}")
                return False, {
                    'error': f"输出过滤失败: {str(e)}",
                    'filter': filter_func.__name__
                }
        
        # 2. 敏感信息过滤
        output_data = await self._filter_sensitive_data(output_data)
        
        # 3. 应用输出相关的安全策略
        for policy in self.policies.values():
            if not policy.enabled or policy.security_level.value < SecurityLevel.MEDIUM.value:
                continue
            
            policy_passed, policy_result = await self._apply_policy(policy, output_data, context, is_input=False)
            if not policy_passed:
                if policy.action == "block":
                    event = SecurityEvent(
                        event_type="output_policy_violation",
                        risk_level=self._get_risk_level(policy.security_level),
                        description=f"输出违反安全策略: {policy.name}",
                        source="boundary_control",
                        resource="output_validation",
                        metadata={
                            'policy_id': policy.policy_id,
                            'policy_name': policy.name,
                            'result': policy_result,
                            'context': context
                        }
                    )
                    await self.safety_system.audit_layer.log_security_event(event)
                    
                    return False, {
                        'error': f"输出违反安全策略: {policy.name}",
                        'policy_id': policy.policy_id,
                        'policy_result': policy_result
                    }
        
        return True, {
            'filtered_data': output_data,
            'original_length': len(str(original_output)),
            'filtered_length': len(str(output_data)),
            'message': "输出验证通过"
        }
    
    async def _apply_policy(self, policy: SecurityPolicy, data: Any, context: Dict[str, Any], is_input: bool) -> Tuple[bool, Dict[str, Any]]:
        """应用安全策略"""
        data_str = str(data)
        
        for rule in policy.rules:
            rule_type = rule.get('type', '')
            
            if rule_type == 'length_check':
                max_length = rule.get('max_length', 100000)
                if len(data_str) > max_length:
                    return False, {
                        'rule': rule,
                        'error': f"内容长度超过限制: {len(data_str)} > {max_length}"
                    }
            
            elif rule_type == 'format_check':
                allowed_formats = rule.get('allowed_formats', [])
                # 简化的格式检查
                if allowed_formats and not any(fmt in data_str[:100].lower() for fmt in allowed_formats):
                    return False, {
                        'rule': rule,
                        'error': "内容格式不被允许"
                    }
            
            elif rule_type == 'content_check':
                blocked_content = rule.get('blocked_content', [])
                for blocked in blocked_content:
                    if blocked.lower() in data_str.lower():
                        return False, {
                            'rule': rule,
                            'error': f"包含禁止内容: {blocked}"
                        }
            
            elif rule_type == 'sensitive_data_filter' and not is_input:
                # 输出时过滤敏感数据
                pass
        
        return True, {'message': "策略检查通过"}
    
    async def _filter_sensitive_data(self, data: Any) -> Any:
        """过滤敏感数据"""
        if isinstance(data, str):
            # 过滤API密钥
            data = re.sub(r'(?i)(sk_|api_key|apikey|secret|token)[\s=:]+[a-zA-Z0-9_\-]+', r'\1=***FILTERED***', data)
            
            # 过滤密码
            data = re.sub(r'(?i)(password|passwd|pwd)[\s=:]+[^\s]+', r'\1=***FILTERED***', data)
            
            # 过滤私钥
            data = re.sub(r'-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----.*?-----END (RSA|EC|OPENSSH) PRIVATE KEY-----', 
                         '-----BEGIN PRIVATE KEY-----\n***FILTERED***\n-----END PRIVATE KEY-----', 
                         data, flags=re.DOTALL)
            
            # 过滤手机号
            data = re.sub(r'1[3-9]\d{9}', lambda m: m.group(0)[:3] + '****' + m.group(0)[7:], data)
            
            # 过滤邮箱
            data = re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'\1***@\2', data)
        
        elif isinstance(data, dict):
            # 递归过滤字典
            filtered = {}
            for key, value in data.items():
                if key.lower() in ['api_key', 'apikey', 'secret', 'token', 'password', 'passwd', 'pwd', 'private_key']:
                    filtered[key] = '***FILTERED***'
                else:
                    filtered[key] = await self._filter_sensitive_data(value)
            return filtered
        
        elif isinstance(data, list):
            # 递归过滤列表
            return [await self._filter_sensitive_data(item) for item in data]
        
        return data
    
    def _get_risk_level(self, security_level: SecurityLevel) -> RiskLevel:
        """根据安全级别获取对应的风险级别"""
        mapping = {
            SecurityLevel.LOW: RiskLevel.LOW,
            SecurityLevel.MEDIUM: RiskLevel.MEDIUM,
            SecurityLevel.HIGH: RiskLevel.HIGH,
            SecurityLevel.CRITICAL: RiskLevel.CRITICAL
        }
        return mapping.get(security_level, RiskLevel.MEDIUM)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'policies_count': len(self.policies),
            'input_filters_count': len(self.input_filters),
            'output_filters_count': len(self.output_filters),
            'blocked_patterns_count': len(self.blocked_patterns)
        }


class CircuitBreakerLayer:
    """
    第二层：熔断控制层
    Circuit Breaker Layer
    
    实现熔断机制，防止系统过载和雪崩效应，保障系统稳定性
    """
    
    def __init__(self, safety_system: 'SafetyControlSystem'):
        self.safety_system = safety_system
        self.breakers: Dict[str, Dict[str, Any]] = {}  # 熔断器实例
        self.default_config = CircuitBreakerConfig()
        self.failure_counts: Dict[str, List[float]] = defaultdict(list)  # 失败次数统计
        self.half_open_calls: Dict[str, int] = defaultdict(int)  # 半开状态调用计数
        
        logger.info("熔断控制层已初始化")
    
    def create_circuit_breaker(self, resource: str, config: Optional[CircuitBreakerConfig] = None) -> None:
        """为指定资源创建熔断器"""
        config = config or self.default_config
        self.breakers[resource] = {
            'state': CircuitBreakerState.CLOSED,
            'config': config,
            'open_time': None,
            'success_count': 0,
            'failure_count': 0
        }
        logger.info(f"已为资源 {resource} 创建熔断器")
    
    def remove_circuit_breaker(self, resource: str) -> bool:
        """移除熔断器"""
        if resource in self.breakers:
            del self.breakers[resource]
            if resource in self.failure_counts:
                del self.failure_counts[resource]
            if resource in self.half_open_calls:
                del self.half_open_calls[resource]
            logger.info(f"已移除资源 {resource} 的熔断器")
            return True
        return False
    
    async def allow_request(self, resource: str) -> Tuple[bool, Dict[str, Any]]:
        """
        检查是否允许请求通过
        :return: (是否允许, 详情)
        """
        if resource not in self.breakers:
            # 默认创建熔断器
            self.create_circuit_breaker(resource)
        
        breaker = self.breakers[resource]
        config = breaker['config']
        current_state = breaker['state']
        current_time = time.time()
        
        if current_state == CircuitBreakerState.CLOSED:
            # 关闭状态：允许请求
            return True, {
                'state': current_state.value,
                'message': "请求允许通过"
            }
        
        elif current_state == CircuitBreakerState.OPEN:
            # 打开状态：检查是否超时可以进入半开状态
            if current_time - breaker['open_time'] >= config.recovery_timeout:
                # 切换到半开状态
                breaker['state'] = CircuitBreakerState.HALF_OPEN
                self.half_open_calls[resource] = 0
                logger.info(f"熔断器 {resource} 从 OPEN 切换到 HALF_OPEN 状态")
                
                return True, {
                    'state': current_state.value,
                    'new_state': CircuitBreakerState.HALF_OPEN.value,
                    'message': "进入半开状态，允许尝试请求"
                }
            else:
                # 仍然熔断
                retry_after = config.recovery_timeout - (current_time - breaker['open_time'])
                return False, {
                    'state': current_state.value,
                    'retry_after': retry_after,
                    'error': "服务熔断中，请稍后重试"
                }
        
        elif current_state == CircuitBreakerState.HALF_OPEN:
            # 半开状态：限制请求数量
            if self.half_open_calls[resource] < config.half_open_max_calls:
                self.half_open_calls[resource] += 1
                return True, {
                    'state': current_state.value,
                    'call_number': self.half_open_calls[resource],
                    'max_calls': config.half_open_max_calls,
                    'message': "半开状态，允许尝试请求"
                }
            else:
                return False, {
                    'state': current_state.value,
                    'error': "半开状态请求数已达上限，请稍后重试"
                }
        
        return False, {'error': "未知熔断器状态"}
    
    async def record_success(self, resource: str) -> None:
        """记录请求成功"""
        if resource not in self.breakers:
            return
        
        breaker = self.breakers[resource]
        config = breaker['config']
        
        if breaker['state'] == CircuitBreakerState.CLOSED:
            # 关闭状态：重置失败计数
            breaker['success_count'] += 1
            # 定期清理过期的失败记录
            await self._cleanup_expired_failures(resource, config.failure_window)
        
        elif breaker['state'] == CircuitBreakerState.HALF_OPEN:
            # 半开状态：成功计数增加，如果达到阈值则关闭熔断器
            breaker['success_count'] += 1
            if breaker['success_count'] >= config.half_open_max_calls:
                # 恢复到关闭状态
                breaker['state'] = CircuitBreakerState.CLOSED
                breaker['open_time'] = None
                breaker['success_count'] = 0
                breaker['failure_count'] = 0
                self.failure_counts[resource].clear()
                self.half_open_calls[resource] = 0
                logger.info(f"熔断器 {resource} 从 HALF_OPEN 切换到 CLOSED 状态，服务恢复")
                
                event = SecurityEvent(
                    event_type="circuit_breaker_recovered",
                    risk_level=RiskLevel.LOW,
                    description=f"熔断器 {resource} 恢复正常",
                    source="circuit_breaker",
                    resource=resource,
                    metadata={
                        'previous_state': CircuitBreakerState.HALF_OPEN.value,
                        'new_state': CircuitBreakerState.CLOSED.value
                    }
                )
                await self.safety_system.audit_layer.log_security_event(event)
    
    async def record_failure(self, resource: str, error: Optional[str] = None) -> None:
        """记录请求失败"""
        if resource not in self.breakers:
            return
        
        breaker = self.breakers[resource]
        config = breaker['config']
        current_time = time.time()
        
        # 记录失败时间
        self.failure_counts[resource].append(current_time)
        breaker['failure_count'] += 1
        
        # 清理过期的失败记录
        await self._cleanup_expired_failures(resource, config.failure_window)
        
        # 检查是否达到熔断阈值
        recent_failures = len(self.failure_counts[resource])
        
        if breaker['state'] == CircuitBreakerState.CLOSED:
            if recent_failures >= config.failure_threshold:
                # 触发熔断，切换到打开状态
                breaker['state'] = CircuitBreakerState.OPEN
                breaker['open_time'] = current_time
                breaker['failure_count'] = 0
                
                logger.warning(f"熔断器 {resource} 触发熔断，切换到 OPEN 状态，失败次数: {recent_failures}")
                
                event = SecurityEvent(
                    event_type="circuit_breaker_opened",
                    risk_level=RiskLevel.HIGH,
                    description=f"熔断器 {resource} 触发熔断",
                    source="circuit_breaker",
                    resource=resource,
                    metadata={
                        'failure_count': recent_failures,
                        'failure_threshold': config.failure_threshold,
                        'error': error,
                        'recovery_timeout': config.recovery_timeout
                    }
                )
                await self.safety_system.audit_layer.log_security_event(event)
        
        elif breaker['state'] == CircuitBreakerState.HALF_OPEN:
            # 半开状态下失败，重新回到打开状态
            breaker['state'] = CircuitBreakerState.OPEN
            breaker['open_time'] = current_time
            self.half_open_calls[resource] = 0
            
            logger.warning(f"熔断器 {resource} 半开状态下请求失败，重新切换到 OPEN 状态")
            
            event = SecurityEvent(
                event_type="circuit_breaker_reopened",
                risk_level=RiskLevel.HIGH,
                description=f"熔断器 {resource} 半开状态下失败，重新熔断",
                source="circuit_breaker",
                resource=resource,
                metadata={
                    'error': error
                }
            )
            await self.safety_system.audit_layer.log_security_event(event)
    
    async def _cleanup_expired_failures(self, resource: str, window_seconds: int) -> None:
        """清理过期的失败记录"""
        if resource not in self.failure_counts:
            return
        
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # 保留时间窗口内的失败记录
        self.failure_counts[resource] = [
            t for t in self.failure_counts[resource]
            if t >= cutoff_time
        ]
    
    def get_breaker_state(self, resource: str) -> Optional[Dict[str, Any]]:
        """获取熔断器状态"""
        if resource not in self.breakers:
            return None
        
        breaker = self.breakers[resource]
        return {
            'resource': resource,
            'state': breaker['state'].value,
            'open_time': breaker['open_time'],
            'success_count': breaker['success_count'],
            'failure_count': breaker['failure_count'],
            'recent_failures': len(self.failure_counts.get(resource, [])),
            'config': {
                'failure_threshold': breaker['config'].failure_threshold,
                'recovery_timeout': breaker['config'].recovery_timeout,
                'half_open_max_calls': breaker['config'].half_open_max_calls,
                'failure_window': breaker['config'].failure_window
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        states_count = defaultdict(int)
        for breaker in self.breakers.values():
            states_count[breaker['state'].value] += 1
        
        return {
            'breakers_count': len(self.breakers),
            'states': dict(states_count),
            'total_failures': sum(len(failures) for failures in self.failure_counts.values())
        }


class AuditControlLayer:
    """
    第三层：审计控制层
    Audit Control Layer
    
    负责所有操作的审计日志记录、安全事件存储和合规性检查
    """
    
    def __init__(self, safety_system: 'SafetyControlSystem'):
        self.safety_system = safety_system
        self.audit_logs: List[AuditLog] = []
        self.security_events: List[SecurityEvent] = []
        self.log_queue: asyncio.Queue = asyncio.Queue()
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.persist_path: Path = Path("security/audit")
        self.max_logs: int = 100000  # 最大日志保留数量
        self.max_events: int = 10000  # 最大安全事件保留数量
        self._worker_task: Optional[asyncio.Task] = None
        self._persist_task: Optional[asyncio.Task] = None
        
        # 创建持久化目录
        self.persist_path.mkdir(parents=True, exist_ok=True)
        (self.persist_path / "logs").mkdir(exist_ok=True)
        (self.persist_path / "events").mkdir(exist_ok=True)
        
        logger.info("审计控制层已初始化")
    
    async def start(self) -> None:
        """启动审计工作线程和持久化任务"""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._audit_worker())
            logger.info("审计工作线程已启动")
        
        if self._persist_task is None or self._persist_task.done():
            self._persist_task = asyncio.create_task(self._periodic_persist())
            logger.info("持久化任务已启动")
    
    async def stop(self) -> None:
        """停止所有工作线程"""
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        if self._persist_task and not self._persist_task.done():
            self._persist_task.cancel()
            try:
                await self._persist_task
            except asyncio.CancelledError:
                pass
        
        # 停止前持久化所有数据
        await self._persist_all()
        logger.info("审计控制层已停止")
    
    async def log_operation(self, audit_log: AuditLog) -> str:
        """记录操作审计日志"""
        await self.log_queue.put(('log', audit_log))
        return audit_log.log_id
    
    async def log_security_event(self, event: SecurityEvent) -> str:
        """记录安全事件"""
        await self.log_queue.put(('event', event))
        return event.event_id
    
    async def create_audit_log(
        self,
        operation: str,
        operator: str = "system",
        resource_type: str = "",
        resource_id: str = "",
        action: str = "",
        request: Optional[Dict[str, Any]] = None,
        ip_address: str = "",
        user_agent: str = ""
    ) -> AuditLog:
        """创建审计日志实例"""
        return AuditLog(
            operation=operation,
            operator=operator,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            request=request,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def search_audit_logs(
        self,
        operator: Optional[str] = None,
        operation: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """搜索审计日志"""
        results = []
        
        for log in reversed(self.audit_logs):  # 从新到旧搜索
            if operator and log.operator != operator:
                continue
            if operation and log.operation != operation:
                continue
            if resource_type and log.resource_type != resource_type:
                continue
            if status and log.status != status:
                continue
            if start_time and log.start_time < start_time:
                continue
            if end_time and log.start_time > end_time:
                continue
            
            results.append(log)
            if len(results) >= limit:
                break
        
