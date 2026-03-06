#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强型多模型对话协议与协作系统
Enhanced Multi-Model Communication Protocol & Collaboration System

功能：
1. 完整对话约定 - 定义我与专家模型的对话规则
2. 信息审计系统 - 审计其他模型提供的信息
3. 工具协作框架 - 定义如何协作使用工具
4. 模型自主工具使用 - 模型可以请求使用工具
5. 智能协作调度 - 根据任务复杂度自动调度模型
6. 交互能力提升 - 完整的通信协议
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field


# =============================================================================
# 协议版本与常量
# =============================================================================

PROTOCOL_VERSION = "2.0.0"
PROTOCOL_NAME = "Enhanced Symphony Multi-Model Protocol"


# =============================================================================
# 对话角色定义
# =============================================================================

class DialogRole(Enum):
    """对话角色"""
    USER = "user"                    # 用户
    ORCHESTRATOR = "orchestrator"    # 编排器（我）
    EXPERT = "expert"                # 专家模型
    TOOL = "tool"                   # 工具
    AUDITOR = "auditor"             # 审计员
    VALIDATOR = "validator"          # 验证员
    COORDINATOR = "coordinator"      # 协调员


# =============================================================================
# 消息类型定义
# =============================================================================

class MessageType(Enum):
    """消息类型"""
    REQUEST = "request"              # 请求
    RESPONSE = "response"            # 响应
    QUERY = "query"                  # 查询
    ANSWER = "answer"                # 回答
    AUDIT = "audit"                  # 审计
    TOOL_REQUEST = "tool_request"    # 工具请求
    TOOL_CALL = "tool_call"          # 工具调用
    TOOL_RESULT = "tool_result"      # 工具结果
    COLLABORATION = "collaboration"  # 协作
    VALIDATION = "validation"        # 验证
    COORDINATION = "coordination"    # 协调
    ERROR = "error"                  # 错误
    ACK = "ack"                      # 确认


# =============================================================================
# 任务复杂度定义
# =============================================================================

class TaskComplexity(Enum):
    """任务复杂度"""
    TRIVIAL = "trivial"              # 非常简单
    SIMPLE = "simple"                # 简单
    MEDIUM = "medium"                # 中等
    COMPLEX = "complex"              # 复杂
    VERY_COMPLEX = "very_complex"   # 非常复杂


# =============================================================================
# 审计级别定义
# =============================================================================

class AuditLevel(Enum):
    """审计级别"""
    PASS = "pass"                    # 通过
    WARNING = "warning"              # 警告
    FAIL = "fail"                   # 失败
    REVIEW = "review"                # 需要审核


# =============================================================================
# 数据结构定义
# =============================================================================

@dataclass
class ProtocolMessage:
    """协议消息"""
    message_id: str
    role: str
    message_type: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    audit_result: Optional[Dict[str, Any]] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


@dataclass
class AuditResult:
    """审计结果"""
    level: str
    score: float = 0.0
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    verified_by: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ModelCapability:
    """模型能力"""
    model_id: str
    provider: str
    alias: str
    capabilities: List[str]
    trust_level: float
    tools_allowed: List[str]
    priority: int
    rate_limit_safe: bool
    max_concurrent: int = 1
    preferred_tasks: List[str] = field(default_factory=list)


@dataclass
class Task:
    """任务"""
    task_id: str
    description: str
    complexity: str
    required_capabilities: List[str]
    tools_needed: List[str]
    estimated_time: int
    phases: List[Dict[str, Any]] = field(default_factory=list)


# =============================================================================
# 审计系统
# =============================================================================

class EnhancedAuditSystem:
    """增强型审计系统"""
    
    def __init__(self):
        self.audit_rules = self._load_audit_rules()
        self.audit_history: List[AuditResult] = []
    
    def _load_audit_rules(self) -> Dict[str, Any]:
        """加载审计规则"""
        return {
            "accuracy_check": {
                "weight": 0.3,
                "description": "信息准确性检查",
                "checks": ["事实核查", "数据一致性", "逻辑正确性", "来源验证"]
            },
            "safety_check": {
                "weight": 0.3,
                "description": "安全性检查",
                "checks": ["有害内容检测", "隐私保护", "合规性", "安全漏洞"]
            },
            "completeness_check": {
                "weight": 0.2,
                "description": "完整性检查",
                "checks": ["信息是否完整", "上下文是否清晰", "是否满足需求", "证据是否充分"]
            },
            "reliability_check": {
                "weight": 0.2,
                "description": "可靠性检查",
                "checks": ["来源可靠性", "证据充分性", "可验证性", "时效性"]
            }
        }
    
    def audit(
        self,
        content: str,
        source_model: str,
        context: Optional[Dict] = None
    ) -> AuditResult:
        """审计内容"""
        issues = []
        recommendations = []
        total_score = 0.0
        
        # 1. 准确性检查
        accuracy_score = self._check_accuracy(content, context)
        total_score += accuracy_score * 0.3
        if accuracy_score < 0.7:
            issues.append("信息准确性存疑")
            recommendations.append("请提供可靠的信息来源")
        
        # 2. 安全性检查
        safety_score = self._check_safety(content)
        total_score += safety_score * 0.3
        if safety_score < 0.8:
            issues.append("安全性检查未通过")
            recommendations.append("请检查内容是否包含敏感信息")
        
        # 3. 完整性检查
        completeness_score = self._check_completeness(content, context)
        total_score += completeness_score * 0.2
        if completeness_score < 0.6:
            issues.append("信息不完整")
            recommendations.append("请补充完整的上下文信息")
        
        # 4. 可靠性检查
        reliability_score = self._check_reliability(content, source_model)
        total_score += reliability_score * 0.2
        if reliability_score < 0.7:
            issues.append("信息来源可靠性不足")
            recommendations.append("请提供更可靠的证据来源")
        
        # 确定审计级别
        if total_score >= 0.8:
            level = AuditLevel.PASS.value
        elif total_score >= 0.6:
            level = AuditLevel.WARNING.value
        elif total_score >= 0.4:
            level = AuditLevel.REVIEW.value
        else:
            level = AuditLevel.FAIL.value
        
        result = AuditResult(
            level=level,
            score=total_score,
            issues=issues,
            recommendations=recommendations,
            verified_by="EnhancedAuditSystem"
        )
        
        self.audit_history.append(result)
        return result
    
    def _check_accuracy(self, content: str, context: Optional[Dict]) -> float:
        """检查准确性"""
        if not content or len(content.strip()) < 10:
            return 0.3
        if "不确定" in content or "不知道" in content or "不清楚" in content:
            return 0.5
        return 0.85
    
    def _check_safety(self, content: str) -> float:
        """检查安全性"""
        dangerous_keywords = ["hack", "攻击", "病毒", "恶意", "钓鱼"]
        for keyword in dangerous_keywords:
            if keyword in content.lower():
                return 0.3
        return 0.9
    
    def _check_completeness(self, content: str, context: Optional[Dict]) -> float:
        """检查完整性"""
        if not context:
            return 0.7
        required_keys = context.get("required_keys", [])
        if not required_keys:
            return 0.8
        return 0.75
    
    def _check_reliability(self, content: str, source_model: str) -> float:
        """检查可靠性"""
        model_scores = {
            "ark-code-latest": 0.9,
            "deepseek-v3.2": 0.85,
            "doubao-seed-2.0-code": 0.8,
            "glm-4.7": 0.8,
            "kimi-k2.5": 0.85,
            "MiniMax-M2.5": 0.8
        }
        return model_scores.get(source_model, 0.7)


# =============================================================================
# 工具协作框架
# =============================================================================

class EnhancedToolFramework:
    """增强型工具协作框架"""
    
    def __init__(self):
        self.tools = self._load_tools()
        self.collaboration_rules = self._load_collaboration_rules()
    
    def _load_tools(self) -> Dict[str, Dict]:
        """加载可用工具"""
        return {
            "read": {
                "name": "读取文件",
                "description": "读取文件内容",
                "permissions": ["file:read"],
                "async_enabled": False,
                "requires_approval": False,
                "timeout": 30
            },
            "write": {
                "name": "写入文件",
                "description": "写入或创建文件",
                "permissions": ["file:write"],
                "async_enabled": False,
                "requires_approval": True,
                "timeout": 30
            },
            "edit": {
                "name": "编辑文件",
                "description": "编辑现有文件",
                "permissions": ["file:edit"],
                "async_enabled": False,
                "requires_approval": True,
                "timeout": 30
            },
            "exec": {
                "name": "执行命令",
                "description": "执行shell命令",
                "permissions": ["system:exec"],
                "async_enabled": True,
                "requires_approval": True,
                "timeout": 120
            },
            "web_search": {
                "name": "网络搜索",
                "description": "搜索网络信息",
                "permissions": ["web:search"],
                "async_enabled": True,
                "requires_approval": False,
                "timeout": 60
            },
            "web_fetch": {
                "name": "网页抓取",
                "description": "抓取网页内容",
                "permissions": ["web:fetch"],
                "async_enabled": True,
                "requires_approval": False,
                "timeout": 60
            },
            "message": {
                "name": "发送消息",
                "description": "发送消息到渠道",
                "permissions": ["message:send"],
                "async_enabled": False,
                "requires_approval": True,
                "timeout": 30
            }
        }
    
    def _load_collaboration_rules(self) -> Dict[str, Any]:
        """加载协作规则"""
        return {
            "approval_required_tools": ["exec", "message", "write", "edit"],
            "async_enabled_tools": ["web_search", "web_fetch", "exec"],
            "timeout_rules": {
                "read": 30,
                "write": 30,
                "edit": 30,
                "exec": 120,
                "web_search": 60,
                "web_fetch": 60,
                "message": 30
            },
            "retry_rules": {
                "max_retries": 3,
                "backoff_factor": 2.0
            },
            "max_concurrent_tools": 3
        }
    
    def can_use_tool(self, tool_name: str, model_name: str, model_tools: List[str]) -> Dict[str, Any]:
        """检查模型是否可以使用工具"""
        if tool_name not in self.tools:
            return {
                "allowed": False,
                "reason": f"Tool '{tool_name}' not found"
            }
        
        # 检查模型是否有权限使用该工具
        if tool_name not in model_tools:
            return {
                "allowed": False,
                "reason": f"Model '{model_name}' not allowed to use tool '{tool_name}'"
            }
        
        tool = self.tools[tool_name]
        
        # 检查是否需要审批
        if tool.get("requires_approval", False):
            return {
                "allowed": True,
                "requires_approval": True,
                "message": f"Tool '{tool_name}' requires approval before use"
            }
        
        return {
            "allowed": True,
            "requires_approval": False
        }
    
    def plan_tool_collaboration(
        self,
        task: str,
        tools_needed: List[str],
        models: List[ModelCapability]
    ) -> Dict[str, Any]:
        """计划工具协作"""
        plan = {
            "task": task,
            "tool_phases": [],
            "models_assigned": {}
        }
        
        for i, tool_name in enumerate(tools_needed):
            # 找一个可以使用该工具的模型
            suitable_model = None
            for model in models:
                if tool_name in model.tools_allowed:
                    suitable_model = model
                    break
            
            if suitable_model:
                plan["tool_phases"].append({
                    "phase": i + 1,
                    "tool": tool_name,
                    "model": suitable_model.model_id,
                    "provider": suitable_model.provider,
                    "async": self.tools[tool_name].get("async_enabled", False)
                })
                plan["models_assigned"][suitable_model.model_id] = suitable_model.alias
        
        return plan


# =============================================================================
# 智能协作调度器
# =============================================================================

class SmartCollaborationScheduler:
    """智能协作调度器"""
    
    def __init__(self, tool_framework: EnhancedToolFramework):
        self.tool_framework = tool_framework
        self.provider_usage: Dict[str, int] = {}  # 追踪每个provider的使用次数
    
    def analyze_complexity(self, task: str) -> TaskComplexity:
        """分析任务复杂度"""
        task_lower = task.lower()
        
        # 非常复杂
        very_complex_keywords = ["开发一个完整的", "实现一个系统", "设计架构", "大规模", "企业级"]
        for keyword in very_complex_keywords:
            if keyword in task_lower:
                return TaskComplexity.VERY_COMPLEX
        
        # 复杂
        complex_keywords = ["开发", "创建", "实现", "设计", "构建系统", "综合分析"]
        for keyword in complex_keywords:
            if keyword in task_lower:
                return TaskComplexity.COMPLEX
        
        # 中等
        medium_keywords = ["分析", "比较", "评估", "检查", "审查", "优化"]
        for keyword in medium_keywords:
            if keyword in task_lower:
                return TaskComplexity.MEDIUM
        
        # 简单
        simple_keywords = ["查询", "搜索", "获取", "告诉我", "什么是", "查找"]
        for keyword in simple_keywords:
            if keyword in task_lower:
                return TaskComplexity.SIMPLE
        
        return TaskComplexity.TRIVIAL
    
    def calculate_models_needed(self, complexity: TaskComplexity) -> int:
        """计算需要的模型数量"""
        mapping = {
            TaskComplexity.TRIVIAL: 1,
            TaskComplexity.SIMPLE: 1,
            TaskComplexity.MEDIUM: 2,
            TaskComplexity.COMPLEX: 3,
            TaskComplexity.VERY_COMPLEX: 4
        }
        return mapping.get(complexity, 1)
    
    def select_models(
        self,
        models: List[ModelCapability],
        count: int,
        required_capabilities: List[str]
    ) -> List[ModelCapability]:
        """
        选择模型
        
        策略：
        1. 不同provider优先（防止限流）
        2. 匹配所需能力
        3. 按信任级别排序
        """
        # 先按provider分组
        provider_groups: Dict[str, List[ModelCapability]] = {}
        for model in models:
            if model.provider not in provider_groups:
                provider_groups[model.provider] = []
            provider_groups[model.provider].append(model)
        
        # 轮流选择不同provider的模型
        selected = []
        providers = list(provider_groups.keys())
        
        while len(selected) < count and len(selected) < len(models):
            for provider in providers:
                if len(selected) >= count:
                    break
                provider_models = provider_groups[provider]
                # 选择该provider中信任级别最高的
                available = [m for m in provider_models if m not in selected]
                if available:
                    best = max(available, key=lambda x: x.trust_level)
                    selected.append(best)
        
        # 如果数量还不够，添加其他模型
        if len(selected) < count:
            remaining = [m for m in models if m not in selected]
            selected.extend(remaining[:count - len(selected)])
        
        return selected[:count]
    
    def create_collaboration_plan(
        self,
        task: str,
        models: List[ModelCapability],
        tools_needed: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """创建协作计划"""
        # 1. 分析复杂度
        complexity = self.analyze_complexity(task)
        
        # 2. 计算需要的模型数量
        models_count = self.calculate_models_needed(complexity)
        
        # 3. 确定所需能力
        required_capabilities = self._infer_capabilities(task)
        
        # 4. 选择模型
        selected_models = self.select_models(models, models_count, required_capabilities)
        
        # 5. 创建阶段计划
        phases = self._create_phases(task, complexity, selected_models, tools_needed or [])
        
        return {
            "task": task,
            "complexity": complexity.value,
            "models_needed": models_count,
            "required_capabilities": required_capabilities,
            "selected_models": [
                {
                    "model_id": m.model_id,
                    "provider": m.provider,
                    "alias": m.alias,
                    "capabilities": m.capabilities
                }
                for m in selected_models
            ],
            "phases": phases,
            "strategy": "different_provider_first"  # 防止限流策略
        }
    
    def _infer_capabilities(self, task: str) -> List[str]:
        """推断所需能力"""
        task_lower = task.lower()
        capabilities = []
        
        capability_keywords = {
            "analysis": ["分析", "评估", "比较", "审查"],
            "code": ["代码", "编程", "开发", "调试"],
            "writing": ["写作", "撰写", "编写", "文档"],
            "research": ["搜索", "查询", "研究", "调研"],
            "architecture": ["架构", "设计", "系统", "结构"],
            "reasoning": ["推理", "逻辑", "思考", "分析"]
        }
        
        for cap, keywords in capability_keywords.items():
            for keyword in keywords:
                if keyword in task_lower:
                    if cap not in capabilities:
                        capabilities.append(cap)
                    break
        
        return capabilities if capabilities else ["analysis"]
    
    def _create_phases(
        self,
        task: str,
        complexity: TaskComplexity,
        models: List[ModelCapability],
        tools_needed: List[str]
    ) -> List[Dict[str, Any]]:
        """创建协作阶段"""
        phases = []
        
        if complexity == TaskComplexity.TRIVIAL or complexity == TaskComplexity.SIMPLE:
            phases.append({
                "phase": 1,
                "action": "direct_execution",
                "model": models[0].model_id,
                "provider": models[0].provider,
                "description": "直接执行任务"
            })
        
        elif complexity == TaskComplexity.MEDIUM:
            phases.append({
                "phase": 1,
                "action": "research",
                "model": models[0].model_id,
                "provider": models[0].provider,
                "description": "收集信息和研究"
            })
            phases.append({
                "phase": 2,
                "action": "execution",
                "model": models[1].model_id,
                "provider": models[1].provider,
                "description": "执行任务"
            })
        
        elif complexity == TaskComplexity.COMPLEX:
            phases.append({
                "phase": 1,
                "action": "research",
                "model": models[0].model_id,
                "provider": models[0].provider,
                "description": "收集信息和研究"
            })
            phases.append({
                "phase": 2,
                "action": "analysis",
                "model": models[1].model_id,
                "provider": models[1].provider,
                "description": "分析和设计"
            })
            phases.append({
                "phase": 3,
                "action": "execution",
                "model": models[2].model_id,
                "provider": models[2].provider,
                "description": "执行和验证"
            })
        
        else:  # VERY_COMPLEX
            phases.append({
                "phase": 1,
                "action": "research",
                "model": models[0].model_id,
                "provider": models[0].provider,
                "description": "第一轮研究"
            })
            phases.append({
                "phase": 2,
                "action": "analysis",
                "model": models[1].model_id,
                "provider": models[1].provider,
                "description": "深度分析"
            })
            phases.append({
                "phase": 3,
                "action": "design",
                "model": models[2].model_id,
                "provider": models[2].provider,
                "description": "设计方案"
            })
            phases.append({
                "phase": 4,
                "action": "execution",
                "model": models[3].model_id,
                "provider": models[3].provider,
                "description": "执行和验证"
            })
        
        return phases


# =============================================================================
# 增强型多模型通信协议
# =============================================================================

class EnhancedMultiModelProtocol:
    """增强型多模型通信协议"""
    
    def __init__(
        self,
        audit_system: EnhancedAuditSystem,
        tool_framework: EnhancedToolFramework,
        scheduler: SmartCollaborationScheduler
    ):
        self.audit_system = audit_system
        self.tool_framework = tool_framework
        self.scheduler = scheduler
        self.conversation_history: List[ProtocolMessage] = []
        self.model_registry: Dict[str, ModelCapability] = {}
        self.pending_tool_requests: List[Dict] = []
    
    def register_model(self, model_info: Dict) -> str:
        """注册模型"""
        model_id = model_info.get("model_id", f"model_{len(self.model_registry)}")
        capability = ModelCapability(
            model_id=model_id,
            provider=model_info.get("provider", "unknown"),
            alias=model_info.get("alias", model_id),
            capabilities=model_info.get("capabilities", []),
            trust_level=model_info.get("trust_level", 0.5),
            tools_allowed=model_info.get("tools_allowed", []),
            priority=model_info.get("priority", 999),
            rate_limit_safe=model_info.get("rate_limit_safe", True),
            max_concurrent=model_info.get("max_concurrent", 1),
            preferred_tasks=model_info.get("preferred_tasks", [])
        )
        self.model_registry[model_id] = capability
        return model_id
    
    def send_message(
        self,
        from_model: str,
        to_model: str,
        content: str,
        message_type: str = MessageType.REQUEST.value,
        metadata: Optional[Dict] = None
    ) -> ProtocolMessage:
        """发送消息"""
        message = ProtocolMessage(
            message_id=f"msg_{len(self.conversation_history)}",
            role=from_model,
            message_type=message_type,
            content=content,
            metadata=metadata or {"from": from_model, "to": to_model}
        )
        
        # 审计消息
        audit_result = self.audit_system.audit(content, from_model)
        message.audit_result = {
            "level": audit_result.level,
            "score": audit_result.score,
            "issues": audit_result.issues
 self.conversation_history        }
        
       .append(message)
        return message
    
    def request_tool(
        self,
        model_name: str,
        tool_name: str,
        tool_params: Dict,
        reason: str
    ) -> Dict[str, Any]:
        """模型请求使用工具"""
        if model_name not in self.model_registry:
            return {
                "approved": False,
                "reason": f"Model '{model_name}' not registered"
            }
        
        model = self.model_registry[model_name]
        
        # 检查工具权限
        permission = self.tool_framework.can_use_tool(
            tool_name,
            model_name,
            model.tools_allowed
        )
        
        if not permission["allowed"]:
            return {
                "approved": False,
                "reason": permission.get("reason", "Unknown reason")
            }
        
        # 创建工具请求
        request = {
            "request_id": f"tool_req_{len(self.pending_tool_requests)}",
            "model_name": model_name,
            "tool_name": tool_name,
            "params": tool_params,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "requires_approval": permission.get("requires_approval", False),
            "status": "pending"
        }
        
        self.pending_tool_requests.append(request)
        
        if permission.get("requires_approval", False):
            return {
                "approved": True,
                "requires_user_approval": True,
                "request_id": request["request_id"],
                "message": f"Tool '{tool_name}' requires approval"
            }
        
        return {
            "approved": True,
            "requires_user_approval": False,
            "request_id": request["request_id"],
            "tool": tool_name,
            "params": tool_params
        }
    
    def approve_tool_request(self, request_id: str) -> Dict[str, Any]:
        """批准工具请求"""
        for request in self.pending_tool_requests:
            if request["request_id"] == request_id:
                request["status"] = "approved"
                return {
                    "success": True,
                    "request": request
                }
        return {"success": False, "reason": "Request not found"}
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要"""
        return {
            "total_messages": len(self.conversation_history),
            "registered_models": len(self.model_registry),
            "pending_tool_requests": len(self.pending_tool_requests),
            "providers": list(set(m.provider for m in self.model_registry.values()))
        }


# =============================================================================
# 主编排器
# =============================================================================

class EnhancedOrchestrator:
    """增强型主编排器"""
    
    def __init__(self):
        self.audit_system = EnhancedAuditSystem()
        self.tool_framework = EnhancedToolFramework()
        self.scheduler = SmartCollaborationScheduler(self.tool_framework)
        self.protocol = EnhancedMultiModelProtocol(
            self.audit_system,
            self.tool_framework,
            self.scheduler
        )
        self.models = self._load_models()
        
        # 注册所有模型
        for model in self.models:
            self.protocol.register_model({
                "model_id": model.model_id,
                "provider": model.provider,
                "alias": model.alias,
                "capabilities": model.capabilities,
                "trust_level": model.trust_level,
                "tools_allowed": model.tools_allowed,
                "priority": model.priority,
                "rate_limit_safe": model.rate_limit_safe
            })
    
    def _load_models(self) -> List[ModelCapability]:
        """加载模型"""
        # 不同provider优先（防止限流）
        return [
            # 不同provider优先
            ModelCapability(
                model_id="MiniMax-M2.5",
                provider="cherry-minimax",
                alias="MiniMax",
                capabilities=["analysis", "multimodal", "writing"],
                trust_level=0.8,
                tools_allowed=["read", "write"],
                priority=1,
                rate_limit_safe=True
            ),
            # 同provider模型
            ModelCapability(
                model_id="ark-code-latest",
                provider="cherry-doubao",
                alias="Doubao Ark",
                capabilities=["analysis", "architecture", "code", "reasoning"],
                trust_level=0.9,
                tools_allowed=["read", "write", "web_search", "web_fetch"],
                priority=11,
                rate_limit_safe=False
            ),
            ModelCapability(
                model_id="deepseek-v3.2",
                provider="cherry-doubao",
                alias="DeepSeek",
                capabilities=["research", "analysis", "writing"],
                trust_level=0.85,
                tools_allowed=["read", "web_search"],
                priority=12,
                rate_limit_safe=False
            ),
            ModelCapability(
                model_id="doubao-seed-2.0-code",
                provider="cherry-doubao",
                alias="Doubao Seed",
                capabilities=["code", "debug", "optimization", "analysis"],
                trust_level=0.8,
                tools_allowed=["read", "write", "exec"],
                priority=13,
                rate_limit_safe=False
            ),
            ModelCapability(
                model_id="glm-4.7",
                provider="cherry-doubao",
                alias="GLM 4.7",
                capabilities=["analysis", "reasoning", "writing"],
                trust_level=0.8,
                tools_allowed=["read", "web_search"],
                priority=14,
                rate_limit_safe=False
            ),
            ModelCapability(
                model_id="kimi-k2.5",
                provider="cherry-doubao",
                alias="Kimi K2.5",
                capabilities=["analysis", "long_context", "reading", "reasoning"],
                trust_level=0.85,
                tools_allowed=["read", "web_fetch"],
                priority=15,
                rate_limit_safe=False
            )
        ]
    
    def process_request(self, user_request: str) -> Dict[str, Any]:
        """处理用户请求"""
        # 创建协作计划
        plan = self.scheduler.create_collaboration_plan(
            user_request,
            self.models
        )
        
        # 模拟执行
        results = []
        for phase in plan["phases"]:
            result = {
                "phase": phase["phase"],
                "action": phase["action"],
                "model": phase["model"],
                "provider": phase["provider"],
                "status": "completed"
            }
            results.append(result)
        
        return {
            "request": user_request,
            "plan": plan,
            "results": results,
            "summary": self.protocol.get_conversation_summary()
        }
    
    def audit_response(self, model_name: str, response: str) -> AuditResult:
        """审计模型响应"""
        return self.audit_system.audit(response, model_name)
    
    def request_tool(
        self,
        model_name: str,
        tool_name: str,
        params: Dict,
        reason: str
    ) -> Dict[str, Any]:
        """模型请求使用工具"""
        return self.protocol.request_tool(model_name, tool_name, params, reason)


# =============================================================================
# 主程序 - 测试
# =============================================================================

def main():
    """主程序"""
    print("=" * 80)
    print("Enhanced Multi-Model Protocol & Collaboration System")
    print("=" * 80)
    
    # 创建编排器
    orchestrator = EnhancedOrchestrator()
    
    # 测试1: 处理不同复杂度任务
    print("\n[测试1] 任务复杂度分析")
    test_tasks = [
        ("告诉我今天的天气", TaskComplexity.SIMPLE),
        ("分析这个Python项目的代码结构", TaskComplexity.MEDIUM),
        ("开发一个完整的Web应用系统", TaskComplexity.VERY_COMPLEX)
    ]
    
    for task, expected in test_tasks:
        complexity = orchestrator.scheduler.analyze_complexity(task)
        models_needed = orchestrator.scheduler.calculate_models_needed(complexity)
        print(f"  任务: {task}")
        print(f"    复杂度: {complexity.value} (预期: {expected.value})")
        print(f"    需要模型: {models_needed}")
    
    # 测试2: 协作计划
    print("\n[测试2] 创建协作计划")
    result = orchestrator.process_request("分析这个项目的代码结构并生成报告")
    print(f"  任务: {result['request']}")
    print(f"  复杂度: {result['plan']['complexity']}")
    print(f"  需要模型: {result['plan']['models_needed']}")
    print(f"  选择策略: {result['plan']['strategy']}")
    print(f"  阶段:")
    for phase in result['plan']['phases']:
        print(f"    阶段{phase['phase']}: {phase['action']} - {phase['model']} ({phase['provider']})")
    
    # 测试3: 审计
    print("\n[测试3] 审计模型响应")
    audit = orchestrator.audit_response(
        "ark-code-latest",
        "根据分析，这个项目使用了模块化架构..."
    )
    print(f"  审计级别: {audit.level}")
    print(f"  审计分数: {audit.score:.2f}")
    
    # 测试4: 工具请求
    print("\n[测试4] 模型请求使用工具")
    tool_result = orchestrator.request_tool(
        "deepseek-v3.2",
        "web_search",
        {"query": "Python best practices"},
        "需要搜索相关信息"
    )
    print(f"  工具: web_search")
    print(f"  批准: {tool_result['approved']}")
    print(f"  需要审批: {tool_result.get('requires_user_approval', False)}")
    
    # 测试5: 对话摘要
    print("\n[测试5] 系统摘要")
    summary = orchestrator.protocol.get_conversation_summary()
    print(f"  注册模型: {summary['registered_models']}")
    print(f"  消息数: {summary['total_messages']}")
    print(f"  提供商: {summary['providers']}")
    
    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
