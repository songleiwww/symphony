#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统v3.2.0 - 推理模块升级
引入CoT/ToT/ReAct推理框架
"""
import json
from typing import List, Dict, Any, Optional
from enum import Enum

class ReasoningFramework(Enum):
    """推理框架类型"""
    COT = "chain_of_thought"      # 思维链
    TOT = "tree_of_thoughts"     # 思维树
    REACT = "reason_and_act"     # 推理+行动

class ThoughtStep:
    """推理步骤"""
    def __init__(self, thought: str, action: Optional[str] = None, 
                 observation: Optional[str] = None, score: float = 0.0):
        self.thought = thought
        self.action = action
        self.observation = observation
        self.score = score
        self.children: List[ThoughtStep] = []
    
    def to_dict(self) -> Dict:
        return {
            "thought": self.thought,
            "action": self.action,
            "observation": self.observation,
            "score": self.score,
            "children": [c.to_dict() for c in self.children]
        }

class CoTReasoner:
    """思维链推理器"""
    
    def __init__(self):
        self.steps: List[ThoughtStep] = []
    
    def reason(self, problem: str, context: Dict = None) -> str:
        """
        执行思维链推理
        1. 理解问题
        2. 分解问题
        3. 逐步推理
        4. 得出结论
        """
        self.steps = []
        
        # 步骤1: 理解问题
        step1 = ThoughtStep(
            thought=f"理解问题: {problem[:50]}...",
            score=0.9
        )
        self.steps.append(step1)
        
        # 步骤2: 分解问题
        sub_problems = self._decompose(problem)
        step2 = ThoughtStep(
            thought=f"分解为{len(sub_problems)}个子问题",
            score=0.85
        )
        self.steps.append(step2)
        
        # 步骤3: 逐步推理
        for i, sub in enumerate(sub_problems):
            step = ThoughtStep(
                thought=f"推理子问题{i+1}: {sub}",
                score=0.8 - i * 0.1
            )
            self.steps.append(step)
        
        # 步骤4: 得出结论
        conclusion = ThoughtStep(
            thought="综合所有推理得出结论",
            score=0.95
        )
        self.steps.append(conclusion)
        
        return self._format_result()
    
    def _decompose(self, problem: str) -> List[str]:
        """分解问题为子问题"""
        # 简单分解策略
        keywords = ["首先", "然后", "接着", "最后", "并且", "或者"]
        parts = [problem]
        for kw in keywords:
            new_parts = []
            for p in parts:
                new_parts.extend(p.split(kw))
            parts = new_parts
        return [p.strip() for p in parts if p.strip()][:5]
    
    def _format_result(self) -> str:
        """格式化推理结果"""
        result = "## 思维链推理过程\n\n"
        for i, step in enumerate(self.steps, 1):
            result += f"**步骤{i}**: {step.thought} (置信度: {step.score:.1%})\n"
        return result

class ToTReasoner:
    """思维树推理器"""
    
    def __init__(self, max_depth: int = 3, branching: int = 3):
        self.max_depth = max_depth
        self.branching = branching
        self.root: Optional[ThoughtStep] = None
    
    def reason(self, problem: str, context: Dict = None) -> str:
        """
        执行思维树推理
        1. 根节点: 问题理解
        2. 分支: 多种解决路径
        3. 评估: 选择最优路径
        """
        # 创建根节点
        self.root = ThoughtStep(
            thought=f"问题: {problem[:30]}...",
            score=1.0
        )
        
        # 探索多路径
        self._explore(self.root, 0, problem)
        
        # 选择最优路径
        best_path = self._select_best(self.root)
        
        return self._format_result(best_path)
    
    def _explore(self, node: ThoughtStep, depth: int, problem: str):
        """探索思维树"""
        if depth >= self.max_depth:
            return
        
        # 生成多个分支
        branches = self._generate_branches(problem, depth)
        
        for branch in branches:
            child = ThoughtStep(
                thought=branch["thought"],
                action=branch.get("action"),
                score=branch["score"]
            )
            node.children.append(child)
            self._explore(child, depth + 1, problem)
    
    def _generate_branches(self, problem: str, depth: int) -> List[Dict]:
        """生成思维分支"""
        strategies = [
            "直接推理",
            "分步分析",
            "类比推理",
            "反证法",
            "归纳法"
        ]
        
        branches = []
        for i in range(min(self.branching, len(strategies))):
            branches.append({
                "thought": f"策略{i+1}: {strategies[i]}",
                "action": strategies[i],
                "score": 0.9 - i * 0.15
            })
        return branches
    
    def _select_best(self, node: ThoughtStep) -> List[ThoughtStep]:
        """选择最优路径"""
        path = [node]
        
        while node.children:
            # 选择得分最高的子节点
            best_child = max(node.children, key=lambda x: x.score)
            path.append(best_child)
            node = best_child
        
        return path
    
    def _format_result(self, path: List[ThoughtStep]) -> str:
        """格式化推理结果"""
        result = "## 思维树推理过程\n\n"
        
        for i, node in enumerate(path):
            indent = "  " * i
            result += f"{indent}├─ **{node.thought}** (得分: {node.score:.2f})\n"
        
        result += f"\n**最终选择**: {path[-1].thought}\n"
        return result

class ReActReasoner:
    """ReAct推理器 (Reason + Act)"""
    
    def __init__(self):
        self.cycle: List[ThoughtStep] = []
        self.max_cycles = 5
    
    def reason(self, problem: str, tools: List[Dict] = None, context: Dict = None) -> str:
        """
        执行ReAct推理
        1. 推理(Reason): 理解当前状态
        2. 行动(Act): 执行工具调用
        3. 观察(Observation): 获取反馈
        4. 迭代直到完成任务
        """
        self.cycle = []
        state = problem
        tools = tools or []
        
        for i in range(self.max_cycles):
            # 推理阶段
            thought = ThoughtStep(
                thought=f"推理阶段: 分析当前状态",
                action="reasoning",
                score=0.9
            )
            self.cycle.append(thought)
            
            # 选择工具
            if tools:
                action = self._select_tool(state, tools)
                thought.action = action["name"]
                thought.observation = f"执行工具: {action['name']}"
                
                # 执行行动
                observation = self._execute_tool(action, state)
                thought.observation = observation
                
                # 更新状态
                state = observation
                
                # 检查是否完成
                if self._is_complete(state):
                    break
        
        return self._format_result()
    
    def _select_tool(self, state: str, tools: List[Dict]) -> Dict:
        """选择工具"""
        # 简单选择策略
        for tool in tools:
            if any(kw in state.lower() for kw in tool.get("keywords", [])):
                return tool
        return tools[0] if tools else {"name": "default", "description": "默认工具"}
    
    def _execute_tool(self, tool: Dict, state: str) -> str:
        """执行工具"""
        # 模拟工具执行
        return f"工具{tool['name']}执行结果: 已处理 '{state[:20]}...'"
    
    def _is_complete(self, state: str) -> bool:
        """检查是否完成"""
        completion_keywords = ["完成", "结束", "结果", "答案", "解决"]
        return any(kw in state for kw in completion_keywords)
    
    def _format_result(self) -> str:
        """格式化推理结果"""
        result = "## ReAct推理过程\n\n"
        
        for i, step in enumerate(self.cycle, 1):
            result += f"**循环{i}**: {step.thought}\n"
            result += f"  - 行动: {step.action}\n"
            if step.observation:
                result += f"  - 观察: {step.observation[:50]}...\n"
            result += "\n"
        
        return result

class ReasoningEngine:
    """统一推理引擎"""
    
    def __init__(self):
        self.cot = CoTReasoner()
        self.tot = ToTReasoner()
        self.react = ReActReasoner()
        self.current_framework = ReasoningFramework.COT
    
    def set_framework(self, framework: ReasoningFramework):
        """设置推理框架"""
        self.current_framework = framework
    
    def reason(self, problem: str, framework: str = "auto", 
               context: Dict = None, tools: List[Dict] = None) -> str:
        """
        统一推理接口
        
        Args:
            problem: 问题描述
            framework: 推理框架 (auto/cot/tot/react)
            context: 上下文
            tools: 可用工具列表 (ReAct用)
        
        Returns:
            推理结果
        """
        # 自动选择框架
        if framework == "auto":
            framework = self._auto_select(problem, context)
        
        if framework == "cot":
            return self.cot.reason(problem, context)
        elif framework == "tot":
            return self.tot.reason(problem, context)
        elif framework == "react":
            return self.react.reason(problem, tools, context)
        else:
            return self.cot.reason(problem, context)
    
    def _auto_select(self, problem: str, context: Dict = None) -> str:
        """自动选择推理框架"""
        problem_length = len(problem)
        
        if problem_length < 50:
            return "cot"  # 简单问题用思维链
        elif problem_length < 200:
            return "react"  # 中等复杂度用ReAct
        else:
            return "tot"  # 复杂问题用思维树


# 测试代码
if __name__ == "__main__":
    engine = ReasoningEngine()
    
    # 测试CoT
    print("=== CoT测试 ===")
    result = engine.reason("计算1+2+3+4+5的结果")
    print(result)
    
    # 测试ToT
    print("\n=== ToT测试 ===")
    result = engine.reason("如何优化序境系统的性能", framework="tot")
    print(result)
    
    # 测试ReAct
    print("\n=== ReAct测试 ===")
    tools = [
        {"name": "search", "keywords": ["搜索", "查找"], "description": "搜索信息"},
        {"name": "calculate", "keywords": ["计算", "数学"], "description": "计算"},
        {"name": "write", "keywords": ["写", "创建"], "description": "写入"}
    ]
    result = engine.reason("搜索序境系统的最新版本", framework="react", tools=tools)
    print(result)
