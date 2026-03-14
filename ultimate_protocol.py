#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极标准化多模型协作协议 - v1.4.0
Ultimate Standardized Multi-Model Collaboration Protocol

核心功能：
1. 规范灌输
2. 记忆同步
3. 工具验证
4. 任务编排
5. 模型能力智能匹配
6. 替补模型调度
7. 我指定哪个模型干什么活！（新增！）
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field


# =============================================================================
# 协议常量
# =============================================================================

PROTOCOL_VERSION = "1.4.0"
PROTOCOL_NAME = "Ultimate Standardized Symphony Protocol"
OUTPUT_FORMAT = "JSON"


# =============================================================================
# 节省tokens标记语法
# =============================================================================

SHORT_MARKERS = {
    "S": "success",
    "W": "warning",
    "E": "error",
    "I": "info",
    "T": "tool_call",
    "R": "result",
    "C": "conclusion",
    "V": "verify",
    "A": "accept",
    "F": "fallback",
    "B": "backup",
    "D": "direct"  # 我直接指定的
}

MARKER_SEP = "|"


# =============================================================================
# 标记解析器
# =============================================================================

class MarkerParser:
    """标记解析器 - 节省tokens！"""
    
    @staticmethod
    def parse_markers(marker_string: str) -> Dict[str, Any]:
        """解析标记字符串"""
        markers = []
        parts = marker_string.split(MARKER_SEP)
        
        for part in parts:
            part = part.strip()
            if part in SHORT_MARKERS:
                markers.append(SHORT_MARKERS[part])
            elif part in SHORT_MARKERS.values():
                markers.append(part)
        
        return {
            "markers": markers,
            "has_success": "success" in markers,
            "has_error": "error" in markers,
            "has_fallback": "fallback" in markers,
            "has_direct": "direct" in markers,
            "has_tool_call": "tool_call" in markers
        }
    
    @staticmethod
    def create_markers(
        status: str, 
        has_tool: bool = False, 
        has_verify: bool = False,
        is_fallback: bool = False,
        is_direct: bool = False
    ) -> str:
        """创建标记字符串"""
        markers = []
        if status == "success":
            markers.append("S")
        elif status == "warning":
            markers.append("W")
        elif status == "error":
            markers.append("E")
        else:
            markers.append("I")
        
        if has_tool:
            markers.append("T")
        if has_verify:
            markers.append("V")
        if is_fallback:
            markers.append("F")
        if is_direct:
            markers.append("D")
        
        markers.append("R")
        return MARKER_SEP.join(markers)


# =============================================================================
# 模型能力详细描述
# =============================================================================

@dataclass
class ModelCapabilityDetail:
    """模型能力详细描述"""
    model_id: str
    provider: str
    alias: str
    
    # 能力评分（0-10）
    analysis_score: int = 5
    coding_score: int = 5
    research_score: int = 5
    writing_score: int = 5
    reasoning_score: int = 5
    debugging_score: int = 5
    design_score: int = 5
    
    # 任务类型偏好
    task_type_scores: Dict[str, int] = field(default_factory=dict)
    
    # 工具使用能力
    allowed_tools: List[str] = field(default_factory=list)
    
    # 可靠性指标
    reliability_score: float = 0.8
    average_latency: float = 10.0
    success_rate: float = 0.9
    
    # 替补模型
    backup_models: List[str] = field(default_factory=list)
    
    def get_capability_score(self, capability: str) -> int:
        """获取能力分数"""
        mapping = {
            "analysis": self.analysis_score,
            "coding": self.coding_score,
            "research": self.research_score,
            "writing": self.writing_score,
            "reasoning": self.reasoning_score,
            "debugging": self.debugging_score,
            "design": self.design_score
        }
        return mapping.get(capability, 5)
    
    def get_task_type_score(self, task_type: str) -> int:
        """获取任务类型分数"""
        return self.task_type_scores.get(task_type, 5)
    
    def get_overall_score(self, required_capabilities: List[str], task_type: str) -> float:
        """获取综合分数"""
        scores = []
        for cap in required_capabilities:
            scores.append(self.get_capability_score(cap))
        scores.append(self.get_task_type_score(task_type))
        scores.append(int(self.reliability_score * 10))
        scores.append(int(self.success_rate * 10))
        latency_score = max(0, 10 - int(self.average_latency / 5))
        scores.append(latency_score)
        return sum(scores) / len(scores) if scores else 5.0
    
    def to_dict(self) -> Dict:
        return {
            "model_id": self.model_id,
            "provider": self.provider,
            "alias": self.alias,
            "analysis_score": self.analysis_score,
            "coding_score": self.coding_score,
            "research_score": self.research_score,
            "writing_score": self.writing_score,
            "reasoning_score": self.reasoning_score,
            "debugging_score": self.debugging_score,
            "design_score": self.design_score,
            "task_type_scores": self.task_type_scores,
            "allowed_tools": self.allowed_tools,
            "reliability_score": self.reliability_score,
            "average_latency": self.average_latency,
            "success_rate": self.success_rate,
            "backup_models": self.backup_models
        }


# =============================================================================
# 我指定的任务 - DirectAssignment
# =============================================================================

@dataclass
class DirectAssignment:
    """我直接指定的任务 - 指定哪个模型干什么活！"""
    assignment_id: str
    task_description: str
    assigned_model: str  # 我指定的模型！
    task_type: str
    required_capabilities: List[str] = field(default_factory=list)
    expected_output: Dict[str, Any] = field(default_factory=dict)
    priority: int = 3
    deadline: Optional[str] = None
    notes: str = ""  # 我的备注
    
    def to_dict(self) -> Dict:
        return {
            "assignment_id": self.assignment_id,
            "task_description": self.task_description,
            "assigned_model": self.assigned_model,
            "task_type": self.task_type,
            "required_capabilities": self.required_capabilities,
            "expected_output": self.expected_output,
            "priority": self.priority,
            "deadline": self.deadline,
            "notes": self.notes,
            "is_direct": True
        }


# =============================================================================
# 模型能力智能匹配系统
# =============================================================================

class ModelCapabilityMatcher:
    """模型能力智能匹配系统"""
    
    def __init__(self):
        self.models: Dict[str, ModelCapabilityDetail] = {}
        self._load_default_models()
    
    def _load_default_models(self):
        """加载默认模型"""
        self.add_model(ModelCapabilityDetail(
            model_id="MiniMax-M2.5",
            provider="cherry-minimax",
            alias="MiniMax",
            analysis_score=9,
            coding_score=6,
            research_score=10,
            writing_score=8,
            reasoning_score=9,
            debugging_score=5,
            design_score=6,
            task_type_scores={"research": 10, "analysis": 9, "review": 8},
            allowed_tools=["read", "write", "web_search"],
            reliability_score=0.92,
            average_latency=8.5,
            success_rate=0.95,
            backup_models=["glm-4.7", "kimi-k2.5"]
        ))
        
        self.add_model(ModelCapabilityDetail(
            model_id="ark-code-latest",
            provider="cherry-doubao",
            alias="Doubao Ark",
            analysis_score=8,
            coding_score=10,
            research_score=7,
            writing_score=7,
            reasoning_score=9,
            debugging_score=9,
            design_score=9,
            task_type_scores={"coding": 10, "design": 9, "debug": 9},
            allowed_tools=["read", "write", "web_search", "web_fetch", "exec"],
            reliability_score=0.88,
            average_latency=12.0,
            success_rate=0.90,
            backup_models=["doubao-seed-2.0-code", "deepseek-v3.2"]
        ))
        
        self.add_model(ModelCapabilityDetail(
            model_id="deepseek-v3.2",
            provider="cherry-doubao",
            alias="DeepSeek",
            analysis_score=8,
            coding_score=8,
            research_score=9,
            writing_score=10,
            reasoning_score=8,
            debugging_score=7,
            design_score=7,
            task_type_scores={"research": 9, "writing": 10, "analysis": 8},
            allowed_tools=["read", "web_search", "web_fetch"],
            reliability_score=0.85,
            average_latency=10.5,
            success_rate=0.88,
            backup_models=["glm-4.7", "MiniMax-M2.5"]
        ))
        
        self.add_model(ModelCapabilityDetail(
            model_id="doubao-seed-2.0-code",
            provider="cherry-doubao",
            alias="Doubao Seed",
            analysis_score=7,
            coding_score=10,
            research_score=6,
            writing_score=6,
            reasoning_score=8,
            debugging_score=10,
            design_score=7,
            task_type_scores={"coding": 10, "debug": 10, "optimization": 8},
            allowed_tools=["read", "write", "exec"],
            reliability_score=0.90,
            average_latency=9.0,
            success_rate=0.92,
            backup_models=["ark-code-latest", "deepseek-v3.2"]
        ))
        
        self.add_model(ModelCapabilityDetail(
            model_id="glm-4.7",
            provider="cherry-doubao",
            alias="GLM 4.7",
            analysis_score=10,
            coding_score=7,
            research_score=8,
            writing_score=9,
            reasoning_score=10,
            debugging_score=6,
            design_score=7,
            task_type_scores={"analysis": 10, "writing": 9, "review": 9},
            allowed_tools=["read", "web_search"],
            reliability_score=0.87,
            average_latency=11.0,
            success_rate=0.89,
            backup_models=["kimi-k2.5", "MiniMax-M2.5"]
        ))
        
        self.add_model(ModelCapabilityDetail(
            model_id="kimi-k2.5",
            provider="cherry-doubao",
            alias="Kimi K2.5",
            analysis_score=9,
            coding_score=6,
            research_score=7,
            writing_score=8,
            reasoning_score=8,
            debugging_score=5,
            design_score=6,
            task_type_scores={"analysis": 9, "review": 10, "writing": 8},
            allowed_tools=["read", "web_fetch"],
            reliability_score=0.86,
            average_latency=10.0,
            success_rate=0.88,
            backup_models=["glm-4.7", "deepseek-v3.2"]
        ))
    
    def add_model(self, model: ModelCapabilityDetail):
        """添加模型"""
        self.models[model.model_id] = model
    
    def get_model(self, model_id: str) -> Optional[ModelCapabilityDetail]:
        """获取指定模型"""
        return self.models.get(model_id)
    
    def list_models(self) -> List[Dict]:
        """列出所有模型"""
        return [model.to_dict() for model in self.models.values()]
    
    def select_best_model(
        self,
        required_capabilities: List[str],
        task_type: str,
        exclude_models: Optional[List[str]] = None
    ) -> Optional[ModelCapabilityDetail]:
        """选择最佳模型"""
        exclude = exclude_models or []
        candidates = [m for m in self.models.values() if m.model_id not in exclude]
        
        if not candidates:
            return None
        
        candidates.sort(
            key=lambda m: m.get_overall_score(required_capabilities, task_type),
            reverse=True
        )
        
        # 不同provider优先
        provider_groups: Dict[str, List[ModelCapabilityDetail]] = {}
        for model in candidates:
            if model.provider not in provider_groups:
                provider_groups[model.provider] = []
            provider_groups[model.provider].append(model)
        
        reordered = []
        providers = list(provider_groups.keys())
        idx = 0
        while len(reordered) < len(candidates):
            provider = providers[idx % len(providers)]
            if provider_groups[provider]:
                reordered.append(provider_groups[provider].pop(0))
            idx += 1
        
        return reordered[0] if reordered else None
    
    def get_backup_model(self, failed_model: str) -> Optional[ModelCapabilityDetail]:
        """获取替补模型"""
        if failed_model not in self.models:
            return None
        
        original = self.models[failed_model]
        for backup_id in original.backup_models:
            if backup_id in self.models:
                return self.models[backup_id]
        
        return self.select_best_model(
            required_capabilities=["analysis"],
            task_type="analysis",
            exclude_models=[failed_model]
        )
    
    def explain_selection(self, model: ModelCapabilityDetail, required_capabilities: List[str], task_type: str) -> str:
        """解释选择原因"""
        parts = [f"选择模型: {model.alias} ({model.model_id})"]
        parts.append("选择理由:")
        for cap in required_capabilities:
            score = model.get_capability_score(cap)
            parts.append(f"  - {cap}能力: {score}/10分")
        task_score = model.get_task_type_score(task_type)
        parts.append(f"  - {task_type}任务偏好: {task_score}/10分")
        parts.append(f"  - 可靠性: {model.reliability_score:.0%}")
        parts.append(f"  - 成功率: {model.success_rate:.0%}")
        parts.append(f"  - 平均延迟: {model.average_latency:.1f}秒")
        return "\n".join(parts)


# =============================================================================
# 任务执行结果
# =============================================================================

@dataclass
class ModelExecutionResult:
    """模型执行结果"""
    model_id: str
    task_id: str
    success: bool
    output: Optional[Dict] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    used_backup: bool = False
    original_model: Optional[str] = None
    is_direct_assignment: bool = False  # 是否是我直接指定的
    markers: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "model_id": self.model_id,
            "task_id": self.task_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "used_backup": self.used_backup,
            "original_model": self.original_model,
            "is_direct_assignment": self.is_direct_assignment,
            "markers": self.markers
        }


# =============================================================================
# 我指定哪个模型干什么活 - DirectTaskOrchestrator
# =============================================================================

class DirectTaskOrchestrator:
    """我指定哪个模型干什么活！"""
    
    def __init__(self, matcher: ModelCapabilityMatcher):
        self.matcher = matcher
        self.assignments: Dict[str, DirectAssignment] = {}
        self.execution_history: List[ModelExecutionResult] = []
    
    def create_direct_assignment(
        self,
        task_description: str,
        assigned_model: str,
        task_type: str,
        required_capabilities: Optional[List[str]] = None,
        notes: str = ""
    ) -> DirectAssignment:
        """
        我直接指定任务 - 指定哪个模型干什么活！
        
        参数：
        - task_description: 任务描述
        - assigned_model: 我指定的模型！
        - task_type: 任务类型
        - required_capabilities: 需要的能力
        - notes: 我的备注
        """
        assignment_id = f"direct_{int(time.time())}"
        
        # 验证模型是否存在
        model = self.matcher.get_model(assigned_model)
        if not model:
            raise ValueError(f"模型 {assigned_model} 不存在！")
        
        assignment = DirectAssignment(
            assignment_id=assignment_id,
            task_description=task_description,
            assigned_model=assigned_model,
            task_type=task_type,
            required_capabilities=required_capabilities or [],
            notes=notes
        )
        
        self.assignments[assignment_id] = assignment
        return assignment
    
    def execute_direct_assignment(
        self,
        assignment: DirectAssignment,
        execute_fn: Callable[[str], tuple[bool, Any, str]]
    ) -> ModelExecutionResult:
        """
        执行我直接指定的任务！
        
        参数：
        - assignment: 我指定的任务
        - execute_fn: 执行函数 (model_id) -> (success, output, error)
        """
        print(f"[直接指定] 模型: {assignment.assigned_model}")
        print(f"  任务: {assignment.task_description}")
        if assignment.notes:
            print(f"  备注: {assignment.notes}")
        
        # 获取模型
        model = self.matcher.get_model(assignment.assigned_model)
        if not model:
            return ModelExecutionResult(
                model_id=assignment.assigned_model,
                task_id=assignment.assignment_id,
                success=False,
                error="模型不存在",
                is_direct_assignment=True
            )
        
        # 执行
        try:
            start_time = time.time()
            success, output, error = execute_fn(assignment.assigned_model)
            exec_time = time.time() - start_time
            
            # 创建标记
            markers = MarkerParser.create_markers(
                status="success" if success else "error",
                has_tool=False,
                is_direct=True
            )
            
            result = ModelExecutionResult(
                model_id=assignment.assigned_model,
                task_id=assignment.assignment_id,
                success=success,
                output=output,
                error=error,
                execution_time=exec_time,
                is_direct_assignment=True,
                markers=markers
            )
            
            self.execution_history.append(result)
            
            if success:
                print(f"  ✅ 成功！")
            else:
                print(f"  ❌ 失败: {error}")
            
            return result
        
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            result = ModelExecutionResult(
                model_id=assignment.assigned_model,
                task_id=assignment.assignment_id,
                success=False,
                error=str(e),
                is_direct_assignment=True,
                markers=MarkerParser.create_markers("error", is_direct=True)
            )
            self.execution_history.append(result)
            return result
    
    def list_assignments(self) -> List[Dict]:
        """列出所有我指定的任务"""
        return [a.to_dict() for a in self.assignments.values()]
    
    def get_assignment(self, assignment_id: str) -> Optional[DirectAssignment]:
        """获取指定的任务"""
        return self.assignments.get(assignment_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计"""
        if not self.execution_history:
            return {"total": 0}
        
        total = len(self.execution_history)
        direct_count = sum(1 for r in self.execution_history if r.is_direct_assignment)
        success_count = sum(1 for r in self.execution_history if r.success)
        
        return {
            "total": total,
            "direct_assignments": direct_count,
            "success": success_count,
            "success_rate": success_count / total if total > 0 else 0
        }


# =============================================================================
# 替补模型调度系统
# =============================================================================

class FallbackScheduler:
    """替补模型调度系统"""
    
    def __init__(self, matcher: ModelCapabilityMatcher):
        self.matcher = matcher
        self.execution_history: List[ModelExecutionResult] = []
        self.max_retries: int = 2
    
    def execute_with_fallback(
        self,
        task_id: str,
        required_capabilities: List[str],
        task_type: str,
        execute_fn: Callable[[str], tuple[bool, Any, str]]
    ) -> ModelExecutionResult:
        """执行任务，带替补调度"""
        tried_models = []
        result = None
        
        for attempt in range(self.max_retries + 1):
            if attempt == 0:
                model = self.matcher.select_best_model(
                    required_capabilities,
                    task_type,
                    exclude_models=tried_models
                )
                original_model = None
            else:
                last_failed = tried_models[-1] if tried_models else None
                if last_failed:
                    model = self.matcher.get_backup_model(last_failed)
                    original_model = last_failed
                else:
                    model = None
            
            if not model:
                break
            
            tried_models.append(model.model_id)
            print(f"[尝试{attempt+1}] 模型: {model.alias}")
            
            try:
                start_time = time.time()
                success, output, error = execute_fn(model.model_id)
                exec_time = time.time() - start_time
                
                markers = MarkerParser.create_markers(
                    status="success" if success else "error",
                    has_tool=False,
                    is_fallback=attempt > 0
                )
                
                result = ModelExecutionResult(
                    model_id=model.model_id,
                    task_id=task_id,
                    success=success,
                    output=output,
                    error=error,
                    execution_time=exec_time,
                    used_backup=attempt > 0,
                    original_model=original_model,
                    markers=markers
                )
                
                self.execution_history.append(result)
                
                if success:
                    print(f"  ✅ 成功！")
                    return result
                else:
                    print(f"  ❌ 失败: {error}")
            
            except Exception as e:
                print(f"  ❌ 异常: {e}")
                result = ModelExecutionResult(
                    model_id=model.model_id,
                    task_id=task_id,
                    success=False,
                    error=str(e),
                    used_backup=attempt > 0,
                    original_model=original_model,
                    markers=MarkerParser.create_markers("error", is_fallback=attempt > 0)
                )
                self.execution_history.append(result)
        
        return result or ModelExecutionResult(
            model_id="unknown",
            task_id=task_id,
            success=False,
            error="所有模型尝试都失败"
        )


# =============================================================================
# 终极协议
# =============================================================================

class UltimateProtocol:
    """终极标准化协议 - v1.4.0"""
    
    def __init__(self):
        self.matcher = ModelCapabilityMatcher()
        self.direct_orchestrator = DirectTaskOrchestrator(self.matcher)
        self.fallback_scheduler = FallbackScheduler(self.matcher)
    
    def list_available_models(self) -> List[Dict]:
        """列出所有可用模型"""
        return self.matcher.list_models()
    
    def create_and_execute_direct(
        self,
        task_description: str,
        assigned_model: str,
        task_type: str,
        execute_fn: Callable[[str], tuple[bool, Any, str]],
        required_capabilities: Optional[List[str]] = None,
        notes: str = ""
    ) -> ModelExecutionResult:
        """
        我指定哪个模型干什么活 - 一键执行！
        
        参数：
        - task_description: 任务描述
        - assigned_model: 我指定的模型！
        - task_type: 任务类型
        - execute_fn: 执行函数
        - required_capabilities: 需要的能力
        - notes: 我的备注
        """
        assignment = self.direct_orchestrator.create_direct_assignment(
            task_description=task_description,
            assigned_model=assigned_model,
            task_type=task_type,
            required_capabilities=required_capabilities,
            notes=notes
        )
        
        return self.direct_orchestrator.execute_direct_assignment(
            assignment=assignment,
            execute_fn=execute_fn
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """获取摘要"""
        return {
            "version": PROTOCOL_VERSION,
            "models": len(self.matcher.models),
            "direct_assignments": len(self.direct_orchestrator.assignments),
            "direct_stats": self.direct_orchestrator.get_statistics()
        }


# =============================================================================
# 使用示例
# =============================================================================

def main():
    """主程序"""
    print("=" * 80)
    print("Ultimate Standardized Symphony Protocol v1.4.0")
    print("=" * 80)
    
    # 修复Windows编码
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 创建终极协议
    protocol = UltimateProtocol()
    print(f"\n✅ 协议已加载")
    print(f"   - 版本: {protocol.get_summary()['version']}")
    print(f"   - 模型数: {protocol.get_summary()['models']}")
    
    # 1. 列出所有可用模型
    print("\n[1] 列出所有可用模型")
    models = protocol.list_available_models()
    print(f"   共 {len(models)} 个模型:")
    for m in models:
        print(f"   - {m['alias']} ({m['model_id']})")
    
    # 2. 我指定哪个模型干什么活！
    print("\n[2] 我指定哪个模型干什么活！")
    
    def mock_direct_execute(model_id: str):
        """模拟执行"""
        return (True, {"result": f"由 {model_id} 完成的任务"}, None)
    
    result = protocol.create_and_execute_direct(
        task_description="写一篇关于AI的文章",
        assigned_model="deepseek-v3.2",  # 我指定！
        task_type="writing",
        execute_fn=mock_direct_execute,
        required_capabilities=["writing", "research"],
        notes="这是我直接指定的任务，要用中文写"
    )
    
    print(f"\n执行结果:")
    print(f"  模型: {result.model_id}")
    print(f"  成功: {result.success}")
    print(f"  直接指定: {result.is_direct_assignment}")
    print(f"  标记: {result.markers}")
    
    # 3. 另一个指定任务
    print("\n[3] 我指定另一个模型干另一个活！")
    
    result2 = protocol.create_and_execute_direct(
        task_description="写一段Python代码",
        assigned_model="ark-code-latest",  # 我指定！
        task_type="coding",
        execute_fn=mock_direct_execute,
        required_capabilities=["coding", "debugging"],
        notes="代码要简洁，要有注释"
    )
    
    print(f"\n执行结果:")
    print(f"  模型: {result2.model_id}")
    print(f"  成功: {result2.success}")
    print(f"  直接指定: {result2.is_direct_assignment}")
    
    # 4. 统计
    print("\n[4] 统计信息")
    stats = protocol.direct_orchestrator.get_statistics()
    print(f"  总执行: {stats['total']}")
    print(f"  直接指定: {stats['direct_assignments']}")
    print(f"  成功率: {stats['success_rate']:.0%}")
    
    print("\n" + "=" * 80)
    print("✅ 终极协议演示完成！")
    print("=" * 80)
    print("\n核心功能:")
    print("  1. 我指定哪个模型干什么活！")
    print("  2. 模型能力智能匹配")
    print("  3. 替补模型调度")
    print("  4. 节省tokens标记语法")


if __name__ == "__main__":
    main()
