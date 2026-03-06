#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终标准化多模型协作协议 - v1.3.0
Final Standardized Multi-Model Collaboration Protocol

核心功能：
1. 规范灌输
2. 记忆同步
3. 工具验证
4. 任务编排
5. 替补模型调度（模型异常时自动调度）
6. 模型能力智能匹配（了解模型擅长什么，智能选择）
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field


# =============================================================================
# 协议常量
# =============================================================================

PROTOCOL_VERSION = "1.3.0"
PROTOCOL_NAME = "Final Standardized Symphony Protocol"
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
    "B": "backup"
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
            "has_backup": "backup" in markers,
            "has_tool_call": "tool_call" in markers
        }
    
    @staticmethod
    def create_markers(
        status: str, 
        has_tool: bool = False, 
        has_verify: bool = False,
        is_fallback: bool = False
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
        
        markers.append("R")
        return MARKER_SEP.join(markers)


# =============================================================================
# 模型能力描述 - 详细！
# =============================================================================

@dataclass
class ModelCapabilityDetail:
    """模型能力详细描述"""
    model_id: str
    provider: str
    alias: str
    
    # 能力评分（0-10）
    analysis_score: int = 5  # 分析能力
    coding_score: int = 5    # 编码能力
    research_score: int = 5  # 研究能力
    writing_score: int = 5   # 写作能力
    reasoning_score: int = 5 # 推理能力
    debugging_score: int = 5 # 调试能力
    design_score: int = 5    # 设计能力
    
    # 任务类型偏好（0-10）
    task_type_scores: Dict[str, int] = field(default_factory=dict)
    
    # 工具使用能力
    allowed_tools: List[str] = field(default_factory=list)
    
    # 可靠性指标
    reliability_score: float = 0.8  # 可靠性（0-1）
    average_latency: float = 10.0   # 平均延迟（秒）
    success_rate: float = 0.9       # 成功率（0-1）
    
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
        """获取综合分数（用于智能选择）"""
        scores = []
        
        # 能力分数
        for cap in required_capabilities:
            scores.append(self.get_capability_score(cap))
        
        # 任务类型分数
        scores.append(self.get_task_type_score(task_type))
        
        # 可靠性
        scores.append(int(self.reliability_score * 10))
        scores.append(int(self.success_rate * 10))
        
        # 延迟（反向，越快越好）
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
# 模型能力智能匹配系统
# =============================================================================

class ModelCapabilityMatcher:
    """模型能力智能匹配系统 - 了解模型擅长什么！"""
    
    def __init__(self):
        self.models: Dict[str, ModelCapabilityDetail] = {}
        self._load_default_models()
    
    def _load_default_models(self):
        """加载默认模型能力（详细！）"""
        # MiniMax-M2.5 - 研究、分析强
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
            task_type_scores={
                "research": 10,
                "analysis": 9,
                "review": 8
            },
            allowed_tools=["read", "write", "web_search"],
            reliability_score=0.92,
            average_latency=8.5,
            success_rate=0.95,
            backup_models=["glm-4.7", "kimi-k2.5"]
        ))
        
        # ark-code-latest - 代码、架构强
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
            task_type_scores={
                "coding": 10,
                "design": 9,
                "debug": 9
            },
            allowed_tools=["read", "write", "web_search", "web_fetch", "exec"],
            reliability_score=0.88,
            average_latency=12.0,
            success_rate=0.90,
            backup_models=["doubao-seed-2.0-code", "deepseek-v3.2"]
        ))
        
        # deepseek-v3.2 - 研究、写作强
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
            task_type_scores={
                "research": 9,
                "writing": 10,
                "analysis": 8
            },
            allowed_tools=["read", "web_search", "web_fetch"],
            reliability_score=0.85,
            average_latency=10.5,
            success_rate=0.88,
            backup_models=["glm-4.7", "MiniMax-M2.5"]
        ))
        
        # doubao-seed-2.0-code - 代码、调试强
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
            task_type_scores={
                "coding": 10,
                "debug": 10,
                "optimization": 8
            },
            allowed_tools=["read", "write", "exec"],
            reliability_score=0.90,
            average_latency=9.0,
            success_rate=0.92,
            backup_models=["ark-code-latest", "deepseek-v3.2"]
        ))
        
        # glm-4.7 - 分析、推理强
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
            task_type_scores={
                "analysis": 10,
                "writing": 9,
                "review": 9
            },
            allowed_tools=["read", "web_search"],
            reliability_score=0.87,
            average_latency=11.0,
            success_rate=0.89,
            backup_models=["kimi-k2.5", "MiniMax-M2.5"]
        ))
        
        # kimi-k2.5 - 分析、阅读强
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
            task_type_scores={
                "analysis": 9,
                "review": 10,
                "writing": 8
            },
            allowed_tools=["read", "web_fetch"],
            reliability_score=0.86,
            average_latency=10.0,
            success_rate=0.88,
            backup_models=["glm-4.7", "deepseek-v3.2"]
        ))
    
    def add_model(self, model: ModelCapabilityDetail):
        """添加模型"""
        self.models[model.model_id] = model
    
    def select_best_model(
        self,
        required_capabilities: List[str],
        task_type: str,
        exclude_models: Optional[List[str]] = None
    ) -> Optional[ModelCapabilityDetail]:
        """
        选择最佳模型 - 智能匹配！
        
        考虑因素：
        1. 能力匹配度
        2. 任务类型偏好
        3. 可靠性
        4. 成功率
        5. 延迟
        6. 不同provider优先（防限流）
        """
        exclude = exclude_models or []
        candidates = []
        
        # 筛选候选模型
        for model in self.models.values():
            if model.model_id in exclude:
                continue
            candidates.append(model)
        
        if not candidates:
            return None
        
        # 按综合分数排序
        candidates.sort(
            key=lambda m: m.get_overall_score(required_capabilities, task_type),
            reverse=True
        )
        
        # 不同provider优先（调整排序）
        provider_groups: Dict[str, List[ModelCapabilityDetail]] = {}
        for model in candidates:
            if model.provider not in provider_groups:
                provider_groups[model.provider] = []
            provider_groups[model.provider].append(model)
        
        # 重新排序：不同provider轮流
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
        
        # 如果没有预设替补，选一个相似的
        return self.select_best_model(
            required_capabilities=["analysis"],
            task_type="analysis",
            exclude_models=[failed_model]
        )
    
    def explain_selection(self, model: ModelCapabilityDetail, required_capabilities: List[str], task_type: str) -> str:
        """解释为什么选择这个模型"""
        parts = [f"选择模型: {model.alias} ({model.model_id})"]
        parts.append("选择理由:")
        
        # 能力说明
        for cap in required_capabilities:
            score = model.get_capability_score(cap)
            parts.append(f"  - {cap}能力: {score}/10分")
        
        # 任务类型说明
        task_score = model.get_task_type_score(task_type)
        parts.append(f"  - {task_type}任务偏好: {task_score}/10分")
        
        # 可靠性说明
        parts.append(f"  - 可靠性: {model.reliability_score:.0%}")
        parts.append(f"  - 成功率: {model.success_rate:.0%}")
        parts.append(f"  - 平均延迟: {model.average_latency:.1f}秒")
        
        return "\n".join(parts)


# =============================================================================
# 替补模型调度系统
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
    
    def to_dict(self) -> Dict:
        return {
            "model_id": self.model_id,
            "task_id": self.task_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "used_backup": self.used_backup,
            "original_model": self.original_model
        }


class FallbackScheduler:
    """替补模型调度系统 - 模型异常时自动调度替补！"""
    
    def __init__(self, matcher: ModelCapabilityMatcher):
        self.matcher = matcher
        self.execution_history: List[ModelExecutionResult] = []
        self.max_retries: int = 2  # 最大重试次数
    
    def execute_with_fallback(
        self,
        task_id: str,
        required_capabilities: List[str],
        task_type: str,
        execute_fn  # 执行函数：model_id -> (success, output, error, time)
    ) -> ModelExecutionResult:
        """
        执行任务，带替补调度！
        
        流程：
        1. 选择最佳模型
        2. 尝试执行
        3. 如果失败，调度替补
        4. 继续直到成功或达到最大重试
        """
        tried_models = []
        result = None
        
        for attempt in range(self.max_retries + 1):
            # 选择模型
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
            
            # 尝试执行
            tried_models.append(model.model_id)
            print(f"[尝试{attempt+1}] 模型: {model.alias}")
            
            try:
                start_time = time.time()
                success, output, error = execute_fn(model.model_id)
                exec_time = time.time() - start_time
                
                result = ModelExecutionResult(
                    model_id=model.model_id,
                    task_id=task_id,
                    success=success,
                    output=output,
                    error=error,
                    execution_time=exec_time,
                    used_backup=attempt > 0,
                    original_model=original_model
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
                    original_model=original_model
                )
                self.execution_history.append(result)
        
        # 所有尝试都失败了
        return result or ModelExecutionResult(
            model_id="unknown",
            task_id=task_id,
            success=False,
            error="所有模型尝试都失败"
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取调度统计"""
        if not self.execution_history:
            return {"total": 0}
        
        total = len(self.execution_history)
        success_count = sum(1 for r in self.execution_history if r.success)
        fallback_count = sum(1 for r in self.execution_history if r.used_backup)
        
        return {
            "total": total,
            "success": success_count,
            "success_rate": success_count / total,
            "fallback_used": fallback_count,
            "fallback_rate": fallback_count / total
        }


# =============================================================================
# 最终协议
# =============================================================================

class FinalProtocol:
    """最终标准化协议 - v1.3.0"""
    
    def __init__(self):
        self.matcher = ModelCapabilityMatcher()
        self.scheduler = FallbackScheduler(self.matcher)
    
    def select_and_explain(self, required_capabilities: List[str], task_type: str) -> Optional[Dict]:
        """选择模型并解释原因"""
        model = self.matcher.select_best_model(required_capabilities, task_type)
        if not model:
            return None
        
        return {
            "model": model.to_dict(),
            "explanation": self.matcher.explain_selection(model, required_capabilities, task_type)
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """获取摘要"""
        return {
            "version": PROTOCOL_VERSION,
            "models": len(self.matcher.models),
            "scheduler_stats": self.scheduler.get_statistics()
        }


# =============================================================================
# 使用示例
# =============================================================================

def main():
    """主程序"""
    print("=" * 80)
    print("Final Standardized Symphony Protocol v1.3.0")
    print("=" * 80)
    
    # 修复Windows编码
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 创建最终协议
    protocol = FinalProtocol()
    print(f"\n✅ 协议已加载")
    print(f"   - 版本: {protocol.get_summary()['version']}")
    print(f"   - 模型数: {protocol.get_summary()['models']}")
    
    # 1. 模型能力智能匹配
    print("\n[1] 模型能力智能匹配")
    required_caps = ["research", "analysis"]
    task_type = "research"
    selection = protocol.select_and_explain(required_caps, task_type)
    if selection:
        print(f"\n{selection['explanation']}")
    
    # 2. 替补模型调度（模拟）
    print("\n[2] 替补模型调度（模拟）")
    
    def mock_execute(model_id: str):
        """模拟执行：第一个失败，第二个成功"""
        if model_id == "MiniMax-M2.5":
            return (False, None, "模拟失败")
        return (True, {"result": "模拟成功"}, None)
    
    result = protocol.scheduler.execute_with_fallback(
        task_id="task_001",
        required_capabilities=required_caps,
        task_type=task_type,
        execute_fn=mock_execute
    )
    print(f"\n执行结果:")
    print(f"  模型: {result.model_id}")
    print(f"  成功: {result.success}")
    print(f"  使用替补: {result.used_backup}")
    if result.original_model:
        print(f"  原模型: {result.original_model}")
    
    # 3. 统计
    print("\n[3] 调度统计")
    stats = protocol.scheduler.get_statistics()
    print(f"  总执行: {stats['total']}")
    print(f"  成功率: {stats.get('success_rate', 0):.0%}")
    print(f"  替补使用率: {stats.get('fallback_rate', 0):.0%}")
    
    print("\n" + "=" * 80)
    print("✅ 最终协议演示完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
