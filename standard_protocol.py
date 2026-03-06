#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标准化多模型协作协议
Standardized Multi-Model Collaboration Protocol

核心原则：
- 我只负责调度模型和分析结果
- 模型自己使用工具
- 统一的输入/输出格式
- 没有不同的处理逻辑
- 标准化协议，单一逻辑
- 节省tokens标识语法！模型给我标记我就能理解！
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field


# =============================================================================
# 协议常量
# =============================================================================

PROTOCOL_VERSION = "1.1.0"
PROTOCOL_NAME = "Standardized Symphony Protocol"
OUTPUT_FORMAT = "JSON"  # 单一格式，没有不同处理逻辑

# =============================================================================
# 节省tokens标识语法 - 模型标记我就能理解！
# =============================================================================

# 单字符标记（最省tokens！）
MARKER_SUCCESS = "✅"          # 成功
MARKER_WARNING = "⚠️"          # 警告
MARKER_ERROR = "❌"            # 错误
MARKER_INFO = "ℹ️"             # 信息
MARKER_TOOL_CALL = "🔧"        # 工具调用
MARKER_RESULT = "📝"            # 结果
MARKER_CONCLUSION = "🎯"        # 结论

# 简短标记语法（节省tokens！）
SHORT_MARKERS = {
    "S": "success",            # 成功
    "W": "warning",            # 警告
    "E": "error",              # 错误
    "I": "info",               # 信息
    "T": "tool_call",          # 工具调用
    "R": "result",             # 结果
    "C": "conclusion"          # 结论
}

# 压缩标记（更省tokens！）
COMPACT_MARKERS = {
    "✅": "S",
    "⚠️": "W", 
    "❌": "E",
    "ℹ️": "I",
    "🔧": "T",
    "📝": "R",
    "🎯": "C"
}

# 标记分隔符（最小化tokens！）
MARKER_SEP = "|"
MARKER_END = "\n"


# =============================================================================
# 标记解析器 - 模型给我标记我就能理解！
# =============================================================================

class MarkerParser:
    """
    标记解析器 - 节省tokens！
    
    功能：
    1. 模型用简单标记，我就能理解
    2. 多种标记格式（单字符/表情/压缩）
    3. 最小化tokens消耗
    """
    
    @staticmethod
    def parse_markers(marker_string: str) -> Dict[str, Any]:
        """
        解析标记字符串 - 模型给我标记我就能理解！
        
        支持的格式：
        - "S|R|C" - 简短标记
        - "✅|📝|🎯" - 表情标记
        - "success|result|conclusion" - 完整标记
        """
        markers = []
        parts = marker_string.split(MARKER_SEP)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 1. 检查压缩标记
            if part in COMPACT_MARKERS:
                markers.append(SHORT_MARKERS[COMPACT_MARKERS[part]])
            # 2. 检查简短标记
            elif part in SHORT_MARKERS:
                markers.append(SHORT_MARKERS[part])
            # 3. 检查完整标记
            elif part in SHORT_MARKERS.values():
                markers.append(part)
            # 4. 检查表情标记（反向查找）
            else:
                for emoji, short in COMPACT_MARKERS.items():
                    if part == emoji:
                        markers.append(SHORT_MARKERS[short])
                        break
        
        return {
            "markers": markers,
            "has_success": "success" in markers,
            "has_warning": "warning" in markers,
            "has_error": "error" in markers,
            "has_tool_call": "tool_call" in markers,
            "has_result": "result" in markers,
            "has_conclusion": "conclusion" in markers
        }
    
    @staticmethod
    def create_markers(status: str, has_tool: bool = False) -> str:
        """
        创建标记字符串 - 节省tokens！
        
        返回最短的可能标记！
        """
        markers = []
        
        # 状态标记（用最短的！）
        if status == "success":
            markers.append("S")  # 比"✅"更省tokens！
        elif status == "warning":
            markers.append("W")
        elif status == "error":
            markers.append("E")
        else:
            markers.append("I")
        
        # 工具调用标记
        if has_tool:
            markers.append("T")
        
        # 结果标记
        markers.append("R")
        
        return MARKER_SEP.join(markers)
    
    @staticmethod
    def get_marker_guide() -> str:
        """获取标记指南（给模型看的！）"""
        return """
标记指南（节省tokens！）
----------------------
简短标记（推荐！最省tokens！）:
  S = success（成功）
  W = warning（警告）
  E = error（错误）
  I = info（信息）
  T = tool_call（工具调用）
  R = result（结果）
  C = conclusion（结论）

表情标记（可选，更直观）:
  ✅ = S = success
  ⚠️ = W = warning
  ❌ = E = error
  ℹ️ = I = info
  🔧 = T = tool_call
  📝 = R = result
  🎯 = C = conclusion

分隔符: | (竖线)

示例:
  "S|R" - 成功 + 结果
  "W|T|R" - 警告 + 工具调用 + 结果
  "E" - 错误
"""


# =============================================================================
# 任务类型枚举
# =============================================================================

class TaskType(Enum):
    """任务类型"""
    RESEARCH = "research"          # 研究/搜索
    ANALYSIS = "analysis"          # 分析
    CODING = "coding"              # 代码
    WRITING = "writing"            # 写作
    DESIGN = "design"              # 设计
    DEBUG = "debug"                # 调试
    OPTIMIZATION = "optimization"  # 优化
    REVIEW = "review"              # 评审


# =============================================================================
# 输出格式枚举
# =============================================================================

class OutputFormat(Enum):
    """输出格式（统一！只有一种！）"""
    JSON = "json"  # 只有JSON，没有其他格式！


# =============================================================================
# 数据结构 - 统一输入
# =============================================================================

@dataclass
class StandardizedInput:
    """标准化输入 - 所有模型使用相同格式"""
    task_id: str
    task_type: str
    task_description: str
    required_capabilities: List[str]
    expected_output: Dict[str, Any]  # 期望输出格式
    constraints: List[str] = field(default_factory=list)
    tools_allowed: List[str] = field(default_factory=list)
    max_iterations: int = 3
    
    def to_dict(self) -> Dict:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "task_id": self.task_id,
            "task_type": self.task_type,
            "task_description": self.task_description,
            "required_capabilities": self.required_capabilities,
            "expected_output": self.expected_output,
            "constraints": self.constraints,
            "tools_allowed": self.tools_allowed,
            "max_iterations": self.max_iterations
        }


# =============================================================================
# 数据结构 - 统一输出
# =============================================================================

@dataclass
class StandardizedOutput:
    """标准化输出 - 所有模型产生相同格式"""
    task_id: str
    model_id: str
    status: str  # "success" | "partial" | "failed"
    markers: str  # 节省tokens标记！模型给我标记我就能理解！
    result: Dict[str, Any]  # 统一结果格式
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_time: float = 0.0
    token_usage: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """自动生成标记（如果还没有的话！）"""
        if not self.markers:
            self.markers = MarkerParser.create_markers(
                self.status,
                len(self.tool_calls) > 0
            )
    
    def to_dict(self) -> Dict:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "task_id": self.task_id,
            "model_id": self.model_id,
            "status": self.status,
            "markers": self.markers,  # 节省tokens标记！
            "result": self.result,
            "tool_calls": self.tool_calls,
            "issues": self.issues,
            "timestamp": self.timestamp,
            "execution_time": self.execution_time,
            "token_usage": self.token_usage
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StandardizedOutput':
        """从JSON读取（我分析时用！）"""
        return cls(
            task_id=data["task_id"],
            model_id=data["model_id"],
            status=data["status"],
            markers=data.get("markers", ""),  # 解析标记！
            result=data["result"],
            tool_calls=data.get("tool_calls", []),
            issues=data.get("issues", []),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            execution_time=data.get("execution_time", 0.0),
            token_usage=data.get("token_usage", {})
        )
    
    def get_parsed_markers(self) -> Dict[str, Any]:
        """解析标记 - 我就能理解！"""
        return MarkerParser.parse_markers(self.markers)


# =============================================================================
# 工具调用 - 模型自己使用
# =============================================================================

@dataclass
class ToolCallRequest:
    """工具调用请求 - 模型自己请求工具"""
    tool_name: str
    parameters: Dict[str, Any]
    purpose: str  # 为什么要使用这个工具
    
    def to_dict(self) -> Dict:
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "purpose": self.purpose
        }


@dataclass
class ToolCallResult:
    """工具调用结果 - 工具返回给模型"""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "result": self.result,
            "error": self.error
        }


# =============================================================================
# 模型能力描述 - 标准化
# =============================================================================

@dataclass
class ModelCapability:
    """模型能力 - 标准化描述"""
    model_id: str
    provider: str
    alias: str
    capabilities: List[str]  # 标准化能力列表
    tools_allowed: List[str]  # 允许使用的工具
    preferred_task_types: List[str]  # 偏好的任务类型
    max_concurrent: int = 1
    
    def to_dict(self) -> Dict:
        return {
            "model_id": self.model_id,
            "provider": self.provider,
            "alias": self.alias,
            "capabilities": self.capabilities,
            "tools_allowed": self.tools_allowed,
            "preferred_task_types": self.preferred_task_types,
            "max_concurrent": self.max_concurrent
        }


# =============================================================================
# 标准化协议 - 核心！
# =============================================================================

class StandardizedProtocol:
    """
    标准化协议 - 单一逻辑，没有不同处理逻辑！
    
    核心原则：
    1. 我只负责：调度模型 + 分析结果
    2. 模型自己负责：使用工具
    3. 统一的输入/输出格式
    4. 单一处理逻辑（JSON）
    5. 没有不同的处理方式
    6. 节省tokens标记语法！模型给我标记我就能理解！
    """
    
    def __init__(self):
        self.models = self._load_standard_models()
        self.task_history: List[Dict] = []
    
    def _load_standard_models(self) -> List[ModelCapability]:
        """加载标准化模型能力"""
        return [
            ModelCapability(
                model_id="MiniMax-M2.5",
                provider="cherry-minimax",
                alias="MiniMax",
                capabilities=["analysis", "multimodal", "research"],
                tools_allowed=["read", "write", "web_search"],
                preferred_task_types=["research", "analysis", "review"],
                max_concurrent=1
            ),
            ModelCapability(
                model_id="ark-code-latest",
                provider="cherry-doubao",
                alias="Doubao Ark",
                capabilities=["analysis", "architecture", "code", "reasoning"],
                tools_allowed=["read", "write", "web_search", "web_fetch", "exec"],
                preferred_task_types=["coding", "design", "debug"],
                max_concurrent=1
            ),
            ModelCapability(
                model_id="deepseek-v3.2",
                provider="cherry-doubao",
                alias="DeepSeek",
                capabilities=["research", "analysis", "writing"],
                tools_allowed=["read", "web_search", "web_fetch"],
                preferred_task_types=["research", "analysis", "writing"],
                max_concurrent=1
            ),
            ModelCapability(
                model_id="doubao-seed-2.0-code",
                provider="cherry-doubao",
                alias="Doubao Seed",
                capabilities=["code", "debug", "optimization", "analysis"],
                tools_allowed=["read", "write", "exec"],
                preferred_task_types=["coding", "debug", "optimization"],
                max_concurrent=1
            ),
            ModelCapability(
                model_id="glm-4.7",
                provider="cherry-doubao",
                alias="GLM 4.7",
                capabilities=["analysis", "reasoning", "writing"],
                tools_allowed=["read", "web_search"],
                preferred_task_types=["analysis", "writing", "review"],
                max_concurrent=1
            ),
            ModelCapability(
                model_id="kimi-k2.5",
                provider="cherry-doubao",
                alias="Kimi K2.5",
                capabilities=["analysis", "long_context", "reading", "reasoning"],
                tools_allowed=["read", "web_fetch"],
                preferred_task_types=["analysis", "review", "writing"],
                max_concurrent=1
            )
        ]
    
    def create_standardized_input(
        self,
        task_type: str,
        description: str,
        required_capabilities: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None
    ) -> StandardizedInput:
        """创建标准化输入 - 所有模型用相同格式！"""
        task_id = f"task_{int(time.time())}"
        
        # 标准化期望输出格式（只有JSON！）
        expected_output = self._get_expected_output_format(task_type)
        
        # 标准化能力
        if required_capabilities is None:
            required_capabilities = self._get_required_capabilities(task_type)
        
        # 标准化工具
        tools_allowed = self._get_tools_allowed(task_type)
        
        return StandardizedInput(
            task_id=task_id,
            task_type=task_type,
            task_description=description,
            required_capabilities=required_capabilities,
            expected_output=expected_output,
            constraints=constraints or [],
            tools_allowed=tools_allowed
        )
    
    def _get_expected_output_format(self, task_type: str) -> Dict:
        """标准化期望输出格式 - 只有JSON！"""
        base_format = {
            "format": "JSON",
            "encoding": "UTF-8",
            "structure": {
                "summary": "string",
                "details": "dict",
                "conclusion": "string"
            }
        }
        
        # 任务类型特定的结构（仍然是JSON！）
        if task_type == TaskType.RESEARCH.value:
            base_format["structure"]["sources"] = "list"
            base_format["structure"]["findings"] = "list"
        elif task_type == TaskType.CODING.value:
            base_format["structure"]["code"] = "string"
            base_format["structure"]["language"] = "string"
            base_format["structure"]["files"] = "list"
        
        return base_format
    
    def _get_required_capabilities(self, task_type: str) -> List[str]:
        """标准化需要的能力"""
        mapping = {
            TaskType.RESEARCH.value: ["research", "analysis"],
            TaskType.ANALYSIS.value: ["analysis", "reasoning"],
            TaskType.CODING.value: ["code", "debug"],
            TaskType.WRITING.value: ["writing", "analysis"],
            TaskType.DESIGN.value: ["analysis", "architecture"],
            TaskType.DEBUG.value: ["debug", "analysis"],
            TaskType.OPTIMIZATION.value: ["optimization", "analysis"],
            TaskType.REVIEW.value: ["review", "analysis"]
        }
        return mapping.get(task_type, ["analysis"])
    
    def _get_tools_allowed(self, task_type: str) -> List[str]:
        """标准化允许的工具"""
        mapping = {
            TaskType.RESEARCH.value: ["read", "web_search", "web_fetch"],
            TaskType.ANALYSIS.value: ["read", "web_search"],
            TaskType.CODING.value: ["read", "write", "exec"],
            TaskType.WRITING.value: ["read", "web_search"],
            TaskType.DESIGN.value: ["read", "write"],
            TaskType.DEBUG.value: ["read", "exec"],
            TaskType.OPTIMIZATION.value: ["read", "write", "exec"],
            TaskType.REVIEW.value: ["read"]
        }
        return mapping.get(task_type, ["read"])
    
    def select_model(self, task_input: StandardizedInput) -> Optional[ModelCapability]:
        """
        选择模型 - 单一逻辑！
        1. 不同provider优先（防限流）
        2. 匹配任务类型
        3. 匹配能力
        """
        # 不同provider优先
        provider_groups: Dict[str, List[ModelCapability]] = {}
        for model in self.models:
            if model.provider not in provider_groups:
                provider_groups[model.provider] = []
            provider_groups[model.provider].append(model)
        
        # 轮流选择不同provider的模型
        providers = list(provider_groups.keys())
        for provider in providers:
            for model in provider_groups[provider]:
                # 匹配任务类型
                if task_input.task_type in model.preferred_task_types:
                    # 匹配能力
                    has_all_capabilities = True
                    for cap in task_input.required_capabilities:
                        if cap not in model.capabilities:
                            has_all_capabilities = False
                            break
                    if has_all_capabilities:
                        return model
        
        # 如果没有完美匹配，返回第一个不同provider的
        return self.models[0] if self.models else None
    
    def analyze_result(
        self,
        output_file: Path,
        task_input: StandardizedInput
    ) -> Dict[str, Any]:
        """
        分析结果 - 我只做这个！
        
        单一逻辑：
        1. 读取JSON文件（只有一种格式！）
        2. 解析标准化输出
        3. 分析结果（包括标记！模型给我标记我就能理解！）
        4. 返回分析
        """
        # 1. 读取JSON（单一格式！）
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read output file: {e}",
                "analysis": "Output file could not be read"
            }
        
        # 2. 解析标准化输出（只有一种结构！）
        try:
            output = StandardizedOutput.from_dict(data)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse output: {e}",
                "analysis": "Output format is not standardized"
            }
        
        # 3. 分析结果（单一逻辑！包括标记！）
        analysis = self._analyze_standardized_output(output, task_input)
        
        # 4. 返回（单一格式！）
        return {
            "success": output.status == "success" or output.get_parsed_markers()["has_success"],
            "model": output.model_id,
            "status": output.status,
            "markers": output.markers,
            "parsed_markers": output.get_parsed_markers(),
            "result_summary": output.result.get("summary", ""),
            "tool_calls": len(output.tool_calls),
            "execution_time": output.execution_time,
            "token_usage": output.token_usage,
            "analysis": analysis,
            "raw_output": output.to_dict()
        }
    
    def _analyze_standardized_output(
        self,
        output: StandardizedOutput,
        task_input: StandardizedInput
    ) -> str:
        """分析标准化输出 - 单一逻辑！"""
        parts = []
        
        # 1. 标记分析（模型给我标记我就能理解！）
        parsed_markers = output.get_parsed_markers()
        if parsed_markers["markers"]:
            marker_summary = "标记: " + ", ".join(parsed_markers["markers"])
            parts.append(f"🏷️  {marker_summary}")
        
        # 2. 状态分析（也可以用标记！）
        if parsed_markers["has_success"]:
            parts.append("✅ 任务成功完成")
        elif parsed_markers["has_warning"]:
            parts.append("⚠️ 任务部分完成")
        elif parsed_markers["has_error"]:
            parts.append("❌ 任务失败")
        else:
            # 备用：用status字段
            if output.status == "success":
                parts.append("✅ 任务成功完成")
            elif output.status == "partial":
                parts.append("⚠️ 任务部分完成")
            else:
                parts.append("❌ 任务失败")
        
        # 3. 结果分析
        if "summary" in output.result:
            parts.append(f"📝 结果摘要: {output.result['summary'][:100]}...")
        
        # 4. 工具使用分析（也可以用标记！）
        if parsed_markers["has_tool_call"] or output.tool_calls:
            parts.append(f"🔧 使用了 {len(output.tool_calls)} 个工具")
            for call in output.tool_calls[:3]:
                parts.append(f"   - {call.get('tool_name', 'unknown')}")
        
        # 5. 问题分析
        if output.issues:
            parts.append("⚠️ 发现问题:")
            for issue in output.issues[:3]:
                parts.append(f"   - {issue}")
        
        # 6. 性能分析
        parts.append(f"⏱️ 执行时间: {output.execution_time:.2f}秒")
        
        return "\n".join(parts)
    
    def save_input(self, task_input: StandardizedInput, directory: Path) -> Path:
        """保存标准化输入 - 只有JSON！"""
        filepath = directory / f"{task_input.task_id}_input.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(task_input.to_dict(), f, ensure_ascii=False, indent=2)
        return filepath
    
    def get_output_path(self, task_input: StandardizedInput, directory: Path) -> Path:
        """获取标准化输出路径 - 只有JSON！"""
        return directory / f"{task_input.task_id}_output.json"
    
    def get_summary(self) -> Dict[str, Any]:
        """获取协议摘要 - 单一格式！"""
        return {
            "protocol_version": PROTOCOL_VERSION,
            "protocol_name": PROTOCOL_NAME,
            "output_format": OUTPUT_FORMAT,
            "principles": [
                "我只负责：调度模型 + 分析结果",
                "模型自己负责：使用工具",
                "统一的输入/输出格式（只有JSON！）",
                "单一处理逻辑，没有不同方式",
                "节省tokens标记语法！模型给我标记我就能理解！"
            ],
            "registered_models": len(self.models),
            "task_types": [t.value for t in TaskType],
            "task_history_count": len(self.task_history),
            "marker_syntax": "支持"
        }


# =============================================================================
# 使用示例
# =============================================================================

def main():
    """主程序 - 演示标准化协议"""
    print("=" * 80)
    print("Standardized Symphony Protocol v1.1.0")
    print("=" * 80)
    
    # 创建协议
    protocol = StandardizedProtocol()
    print(f"\n✅ 协议已加载")
    print(f"   - 版本: {protocol.get_summary()['protocol_version']}")
    print(f"   - 模型数: {protocol.get_summary()['registered_models']}")
    print(f"   - 输出格式: {protocol.get_summary()['output_format']}（单一格式！）")
    print(f"   - 标记语法: ✅ 支持")
    
    # 1. 创建标准化输入
    print("\n[步骤1] 创建标准化输入")
    task_input = protocol.create_standardized_input(
        task_type=TaskType.RESEARCH.value,
        description="研究AI多模型协作的最佳实践",
        required_capabilities=["research", "analysis"],
        constraints=["使用可靠来源", "提供证据"]
    )
    print(f"   任务ID: {task_input.task_id}")
    print(f"   任务类型: {task_input.task_type}")
    print(f"   期望格式: JSON（只有一种！）")
    
    # 2. 选择模型
    print("\n[步骤2] 选择模型")
    selected_model = protocol.select_model(task_input)
    if selected_model:
        print(f"   选择模型: {selected_model.alias} ({selected_model.model_id})")
        print(f"   提供商: {selected_model.provider}")
        print(f"   能力: {', '.join(selected_model.capabilities)}")
    
    # 3. 保存输入（给模型读取）
    print("\n[步骤3] 保存标准化输入")
    test_dir = Path("standard_protocol_test")
    test_dir.mkdir(exist_ok=True)
    input_path = protocol.save_input(task_input, test_dir)
    print(f"   输入文件: {input_path}")
    print(f"   格式: JSON（单一格式！）")
    
    # 4. 模型自己执行...（使用工具...）
    print("\n[步骤4] 模型自己执行并使用工具...")
    print("   (这部分由模型自己完成)")
    
    # 显示标记指南
    print("\n[标记指南 - 节省tokens！]")
    print(MarkerParser.get_marker_guide())
    
    # 5. 我分析结果（只有JSON！）
    print("\n[步骤5] 我分析结果")
    output_path = protocol.get_output_path(task_input, test_dir)
    
    # 模拟：创建一个示例输出（带标记！节省tokens！）
    sample_output = StandardizedOutput(
        task_id=task_input.task_id,
        model_id=selected_model.model_id if selected_model else "unknown",
        status="success",
        markers="S|T|R",  # 节省tokens标记！模型给我标记我就能理解！
        result={
            "summary": "研究完成，发现了3个最佳实践",
            "details": {
                "best_practices": ["分层架构", "标准化协议", "审计系统"]
            },
            "conclusion": "推荐使用标准化协议"
        },
        tool_calls=[
            {"tool_name": "web_search", "purpose": "查找相关文献"},
            {"tool_name": "read", "purpose": "读取参考资料"}
        ],
        execution_time=45.5
    )
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_output.to_dict(), f, ensure_ascii=False, indent=2)
    
    # 分析
    analysis = protocol.analyze_result(output_path, task_input)
    print(f"   成功: {analysis['success']}")
    print(f"   模型: {analysis['model']}")
    print(f"   标记: {analysis['markers']}")
    print(f"   工具调用: {analysis['tool_calls']}")
    print(f"   分析:")
    for line in analysis['analysis'].split('\n'):
        print(f"      {line}")
    
    print("\n" + "=" * 80)
    print("✅ 标准化协议演示完成！")
    print("=" * 80)
    print("\n核心原则:")
    for principle in protocol.get_summary()['principles']:
        print(f"  - {principle}")


if __name__ == "__main__":
    main()
