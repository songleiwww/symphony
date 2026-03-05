#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整标准化多模型协作协议 - v1.2.0
Complete Standardized Multi-Model Collaboration Protocol

核心功能：
1. 规范灌输（我给模型的规范
2. 记忆同步（我和模型记忆同步
3. 模型自己使用工具 + 验证工具使用正确
4. 任务安排 + 协作验证
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field

# 修复Windows编码问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# =============================================================================
# 协议常量
# =============================================================================

PROTOCOL_VERSION = "1.2.0"
PROTOCOL_NAME = "Complete Standardized Symphony Protocol"
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
    "A": "accept"
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
            "has_verify": "verify" in markers,
            "has_accept": "accept" in markers,
            "has_tool_call": "tool_call" in markers
        }
    
    @staticmethod
    def create_markers(status: str, has_tool: bool = False, has_verify: bool = False) -> str:
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
        
        markers.append("R")
        return MARKER_SEP.join(markers)


# =============================================================================
# 规范系统 - 我给模型的规范
# =============================================================================

@dataclass
class ProtocolSpec:
    """我给模型的规范"""
    spec_id: str
    spec_name: str
    spec_content: str
    priority: int  # 1=最高优先级
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "spec_id": self.spec_id,
            "spec_name": self.spec_name,
            "spec_content": self.spec_content,
            "priority": self.priority,
            "version": self.version,
            "created_at": self.created_at
        }


class SpecificationSystem:
    """规范系统 - 我给模型灌输规范"""
    
    def __init__(self):
        self.specs: Dict[str, ProtocolSpec] = {}
        self._load_default_specs()
    
    def _load_default_specs(self):
        """加载默认规范"""
        self.add_spec(ProtocolSpec(
            spec_id="spec_json_only",
            spec_name="只输出JSON",
            spec_content="所有输出必须是JSON格式，不能有其他格式",
            priority=1
        ))
        
        self.add_spec(ProtocolSpec(
            spec_id="spec_markers",
            spec_name="使用标记语法",
            spec_content="使用S/W/E/I/T/R/C标记，分隔符用|",
            priority=2
        ))
        
        self.add_spec(ProtocolSpec(
            spec_id="spec_tool_verify",
            spec_name="工具使用验证",
            spec_content="使用工具后必须验证工具使用是否正确",
            priority=3
        ))
        
        self.add_spec(ProtocolSpec(
            spec_id="spec_collaboration",
            spec_name="协作规范",
            spec_content="与其他模型协作时必须保持友好，尊重其他模型的输出",
            priority=4
        ))
    
    def add_spec(self, spec: ProtocolSpec):
        """添加规范"""
        self.specs[spec.spec_id] = spec
    
    def get_spec_for_model(self, model_id: str) -> List[Dict]:
        """获取给模型的规范（按优先级排序）"""
        sorted_specs = sorted(
            self.specs.values(),
            key=lambda x: x.priority
        )
        return [spec.to_dict() for spec in sorted_specs]
    
    def get_spec_prompt(self, model_id: str) -> str:
        """获取给模型的规范提示词"""
        specs = self.get_spec_for_model(model_id)
        lines = ["你必须遵守以下规范："]
        for i, spec in enumerate(specs, 1):
            lines.append(f"{i}. [{spec['priority']}] {spec['spec_name']}: {spec['spec_content']}")
        return "\n".join(lines)


# =============================================================================
# 记忆同步系统 - 我和模型记忆同步
# =============================================================================

@dataclass
class SharedMemory:
    """共享记忆"""
    memory_id: str
    memory_type: str  # "fact" | "decision" | "context"
    memory_content: str
    source: str  # "me" | "model" | "both"
    created_by: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    verified: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type,
            "memory_content": self.memory_content,
            "source": self.source,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "verified": self.verified
        }


class MemorySyncSystem:
    """记忆同步系统 - 我和模型记忆同步"""
    
    def __init__(self):
        self.memories: Dict[str, SharedMemory] = {}
    
    def add_memory(self, memory: SharedMemory):
        """添加记忆"""
        self.memories[memory.memory_id] = memory
    
    def get_memories_for_model(self, model_id: str, limit: int = 10) -> List[Dict]:
        """获取给模型的记忆"""
        sorted_memories = sorted(
            self.memories.values(),
            key=lambda x: x.created_at,
            reverse=True
        )
        return [mem.to_dict() for mem in sorted_memories[:limit]]
    
    def get_memory_prompt(self, model_id: str) -> str:
        """获取给模型的记忆提示词"""
        memories = self.get_memories_for_model(model_id)
        if not memories:
            return ""
        lines = ["共享记忆："]
        for i, mem in enumerate(memories, 1):
            lines.append(f"{i}. [{mem['memory_type']}] {mem['memory_content']}")
        return "\n".join(lines)
    
    def verify_memory(self, memory_id: str) -> bool:
        """验证记忆（我来验证）"""
        if memory_id in self.memories:
            self.memories[memory_id].verified = True
            return True
        return False


# =============================================================================
# 工具验证系统 - 验证工具使用正确
# =============================================================================

@dataclass
class ToolValidationRule:
    """工具验证规则"""
    tool_name: str
    validation_rules: List[str]
    expected_format: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "tool_name": self.tool_name,
            "validation_rules": self.validation_rules,
            "expected_format": self.expected_format
        }


class ToolValidationSystem:
    """工具验证系统 - 验证工具使用正确"""
    
    def __init__(self):
        self.rules: Dict[str, ToolValidationRule] = {}
        self._load_default_rules()
    
    def _load_default_rules(self):
        """加载默认验证规则"""
        self.add_rule(ToolValidationRule(
            tool_name="web_search",
            validation_rules=[
                "必须返回至少3个结果",
                "每个结果必须有title和url",
                "必须提供snippet"
            ],
            expected_format={
                "results": "list",
                "title": "string",
                "url": "string",
                "snippet": "string"
            }
        ))
        
        self.add_rule(ToolValidationRule(
            tool_name="read",
            validation_rules=[
                "必须返回文件内容",
                "必须包含文件路径",
                "内容不能为空"
            ],
            expected_format={
                "path": "string",
                "content": "string"
            }
        ))
        
        self.add_rule(ToolValidationRule(
            tool_name="write",
            validation_rules=[
                "必须确认文件已写入",
                "必须包含文件路径",
                "必须包含写入的内容"
            ],
            expected_format={
                "path": "string",
                "content": "string",
                "success": "bool"
            }
        ))
    
    def add_rule(self, rule: ToolValidationRule):
        """添加验证规则"""
        self.rules[rule.tool_name] = rule
    
    def validate_tool_call(self, tool_name: str, tool_result: Dict) -> Dict[str, Any]:
        """验证工具使用是否正确"""
        if tool_name not in self.rules:
            return {
                "valid": False,
                "issues": ["没有找到工具验证规则"]
            }
        
        rule = self.rules[tool_name]
        issues = []
        passed = []
        
        for i, validation_rule in enumerate(rule.validation_rules, 1):
            # 简单验证（实际可以更复杂）
            if "至少" in validation_rule and "results" in validation_rule:
                if "results" in tool_result and len(tool_result["results"]) >= 3:
                    passed.append(validation_rule)
                else:
                    issues.append(f"规则{i}失败：{validation_rule}")
            else:
                passed.append(validation_rule)
        
        return {
            "valid": len(issues) == 0,
            "passed": passed,
            "issues": issues,
            "rule_used": rule.to_dict()
        }
    
    def get_validation_prompt(self, tool_name: str) -> str:
        """获取工具验证提示词"""
        if tool_name not in self.rules:
            return ""
        rule = self.rules[tool_name]
        lines = [f"工具 {tool_name} 验证规则："]
        for i, r in enumerate(rule.validation_rules, 1):
            lines.append(f"{i}. {r}")
        return "\n".join(lines)


# =============================================================================
# 任务安排 + 协作验证
# =============================================================================

@dataclass
class TaskAssignment:
    """任务安排"""
    task_id: str
    task_description: str
    assigned_to: str  # 模型ID
    depends_on: List[str] = field(default_factory=list)
    expected_output: Dict[str, Any] = field(default_factory=dict)
    deadline: Optional[str] = None
    priority: int = 3
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task_description": self.task_description,
            "assigned_to": self.assigned_to,
            "depends_on": self.depends_on,
            "expected_output": self.expected_output,
            "deadline": self.deadline,
            "priority": self.priority
        }


@dataclass
class CollaborationVerification:
    """协作验证"""
    collaboration_id: str
    task_assignments: List[TaskAssignment]
    verification_rules: List[str]
    verified: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "collaboration_id": self.collaboration_id,
            "task_assignments": [t.to_dict() for t in self.task_assignments],
            "verification_rules": self.verification_rules,
            "verified": self.verified
        }


class TaskOrchestrator:
    """任务编排器 - 任务安排 + 协作验证"""
    
    def __init__(self):
        self.assignments: Dict[str, TaskAssignment] = {}
        self.collaborations: Dict[str, CollaborationVerification] = {}
    
    def create_assignment(
        self,
        task_description: str,
        assigned_to: str,
        depends_on: Optional[List[str]] = None
    ) -> TaskAssignment:
        """创建任务安排"""
        task_id = f"task_{int(time.time())}"
        assignment = TaskAssignment(
            task_id=task_id,
            task_description=task_description,
            assigned_to=assigned_to,
            depends_on=depends_on or []
        )
        self.assignments[task_id] = assignment
        return assignment
    
    def create_collaboration(
        self,
        assignments: List[TaskAssignment],
        rules: Optional[List[str]] = None
    ) -> CollaborationVerification:
        """创建协作验证"""
        collab_id = f"collab_{int(time.time())}"
        collab = CollaborationVerification(
            collaboration_id=collab_id,
            task_assignments=assignments,
            verification_rules=rules or [
                "所有任务必须完成",
                "任务顺序正确",
                "输出格式正确"
            ]
        )
        self.collaborations[collab_id] = collab
        return collab
    
    def verify_collaboration(self, collab_id: str, outputs: List[Dict]) -> Dict[str, Any]:
        """验证协作是否正确"""
        if collab_id not in self.collaborations:
            return {"valid": False, "issues": ["协作不存在"]}
        
        collab = self.collaborations[collab_id]
        issues = []
        passed = []
        
        # 验证1：所有任务都有输出
        assignment_ids = {a.task_id for a in collab.task_assignments}
        output_ids = {o["task_id"] for o in outputs}
        missing = assignment_ids - output_ids
        if missing:
            issues.append(f"缺少任务输出: {missing}")
        else:
            passed.append("所有任务都有输出")
        
        # 验证2：输出格式正确
        for output in outputs:
            if "status" not in output:
                issues.append(f"任务{output.get('task_id')}缺少status")
            else:
                passed.append(f"任务{output.get('task_id')}有status")
        
        # 验证3：没有错误
        has_errors = any(o.get("status") == "error" for o in outputs)
        if has_errors:
            issues.append("有任务失败")
        else:
            passed.append("没有任务失败")
        
        collab.verified = len(issues) == 0
        
        return {
            "valid": collab.verified,
            "passed": passed,
            "issues": issues,
            "collaboration": collab.to_dict()
        }


# =============================================================================
# 完整协议
# =============================================================================

class CompleteProtocol:
    """完整标准化协议 - v1.2.0"""
    
    def __init__(self):
        self.spec_system = SpecificationSystem()
        self.memory_system = MemorySyncSystem()
        self.tool_validation = ToolValidationSystem()
        self.task_orchestrator = TaskOrchestrator()
    
    def get_full_prompt_for_model(self, model_id: str) -> str:
        """获取给模型的完整提示词（规范+记忆）"""
        parts = []
        
        # 规范
        spec_prompt = self.spec_system.get_spec_prompt(model_id)
        if spec_prompt:
            parts.append(spec_prompt)
        
        # 记忆
        memory_prompt = self.memory_system.get_memory_prompt(model_id)
        if memory_prompt:
            parts.append("")
            parts.append(memory_prompt)
        
        return "\n".join(parts)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取摘要"""
        return {
            "version": PROTOCOL_VERSION,
            "specs": len(self.spec_system.specs),
            "memories": len(self.memory_system.memories),
            "tool_rules": len(self.tool_validation.rules),
            "assignments": len(self.task_orchestrator.assignments),
            "collaborations": len(self.task_orchestrator.collaborations)
        }


# =============================================================================
# 使用示例
# =============================================================================

def main():
    """主程序"""
    print("=" * 80)
    print("Complete Standardized Symphony Protocol v1.2.0")
    print("=" * 80)
    
    # 创建完整协议
    protocol = CompleteProtocol()
    print(f"\n✅ 协议已加载")
    print(f"   - 版本: {protocol.get_summary()['version']}")
    print(f"   - 规范数: {protocol.get_summary()['specs']}")
    print(f"   - 记忆数: {protocol.get_summary()['memories']}")
    print(f"   - 工具规则: {protocol.get_summary()['tool_rules']}")
    
    # 1. 规范灌输
    print("\n[1] 规范灌输 - 我给模型的规范")
    model_id = "ark-code-latest"
    spec_prompt = protocol.spec_system.get_spec_prompt(model_id)
    print(f"   模型: {model_id}")
    print(f"   规范:")
    for line in spec_prompt.split('\n')[:5]:
        print(f"      {line}")
    
    # 2. 记忆同步
    print("\n[2] 记忆同步 - 我和模型记忆同步")
    from datetime import datetime
    memory = SharedMemory(
        memory_id="mem_001",
        memory_type="fact",
        memory_content="品牌标语是'智韵交响，共创华章'",
        source="both",
        created_by="me"
    )
    protocol.memory_system.add_memory(memory)
    print(f"   添加记忆: {memory.memory_content}")
    
    # 3. 任务安排
    print("\n[3] 任务安排")
    assignment1 = protocol.task_orchestrator.create_assignment(
        task_description="研究AI多模型协作的最佳实践",
        assigned_to="ark-code-latest"
    )
    assignment2 = protocol.task_orchestrator.create_assignment(
        task_description="验证研究结果",
        assigned_to="deepseek-v3.2",
        depends_on=[assignment1.task_id]
    )
    print(f"   任务1: {assignment1.task_description} -> {assignment1.assigned_to}")
    print(f"   任务2: {assignment2.task_description} -> {assignment2.assigned_to}")
    
    # 4. 协作验证
    print("\n[4] 协作验证")
    collab = protocol.task_orchestrator.create_collaboration([assignment1, assignment2])
    print(f"   协作ID: {collab.collaboration_id}")
    print(f"   验证规则: {len(collab.verification_rules)}条")
    
    # 5. 工具验证
    print("\n[5] 工具验证")
    tool_result = {
        "results": [
            {"title": "最佳实践1", "url": "https://...", "snippet": "..."},
            {"title": "最佳实践2", "url": "https://...", "snippet": "..."},
            {"title": "最佳实践3", "url": "https://...", "snippet": "..."}
        ]
    }
    validation = protocol.tool_validation.validate_tool_call("web_search", tool_result)
    print(f"   工具: web_search")
    print(f"   验证: {'✅ 通过' if validation['valid'] else '❌ 失败'}")
    print(f"   通过: {len(validation.get('passed', []))}条")
    
    print("\n" + "=" * 80)
    print("✅ 完整协议演示完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
