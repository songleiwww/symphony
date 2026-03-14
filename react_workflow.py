#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
react_workflow.py - ReAct工作流
实现推理-行动循环，增强AI Agent能力
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum


class ReActStep(Enum):
    """ReAct步骤枚举"""
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"


class ReActWorkflow:
    """ReAct工作流 - 推理-行动循环"""
    
    def __init__(self, max_iterations: int = 5):
        """
        初始化ReAct工作流
        
        Args:
            max_iterations: 最大迭代次数
        """
        self.max_iterations = max_iterations
        self.history: List[Dict[str, Any]] = []
        self.current_iteration = 0
    
    def thought(self, content: str) -> Dict[str, Any]:
        """
        思考步骤
        
        Args:
            content: 思考内容
        
        Returns:
            思考结果
        """
        result = {
            "step": ReActStep.THOUGHT.value,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "iteration": self.current_iteration
        }
        self.history.append(result)
        return result
    
    def action(self, action_type: str, action_input: Any) -> Dict[str, Any]:
        """
        行动步骤
        
        Args:
            action_type: 行动类型
            action_input: 行动输入
        
        Returns:
            行动结果
        """
        result = {
            "step": ReActStep.ACTION.value,
            "action_type": action_type,
            "action_input": action_input,
            "timestamp": datetime.now().isoformat(),
            "iteration": self.current_iteration
        }
        self.history.append(result)
        return result
    
    def observation(self, content: str) -> Dict[str, Any]:
        """
        观察步骤
        
        Args:
            content: 观察内容
        
        Returns:
            观察结果
        """
        result = {
            "step": ReActStep.OBSERVATION.value,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "iteration": self.current_iteration
        }
        self.history.append(result)
        
        # 完成一次迭代
        self.current_iteration += 1
        return result
    
    def should_continue(self) -> bool:
        """
        是否应该继续
        
        Returns:
            是否继续
        """
        return self.current_iteration < self.max_iterations
    
    def get_context(self) -> str:
        """
        获取历史上下文
        
        Returns:
            上下文字符串
        """
        context_parts = []
        for h in self.history:
            if h["step"] == ReActStep.THOUGHT.value:
                context_parts.append(f"Thought: {h['content']}")
            elif h["step"] == ReActStep.ACTION.value:
                context_parts.append(f"Action: {h['action_type']}({h['action_input']})")
            elif h["step"] == ReActStep.OBSERVATION.value:
                context_parts.append(f"Observation: {h['content']}")
        
        return "\n".join(context_parts)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取工作流摘要
        
        Returns:
            摘要信息
        """
        thoughts = [h for h in self.history if h["step"] == ReActStep.THOUGHT.value]
        actions = [h for h in self.history if h["step"] == ReActStep.ACTION.value]
        observations = [h for h in self.history if h["step"] == ReActStep.OBSERVATION.value]
        
        return {
            "total_iterations": self.current_iteration,
            "total_thoughts": len(thoughts),
            "total_actions": len(actions),
            "total_observations": len(observations),
            "history_length": len(self.history)
        }


class ReActAgent:
    """ReAct智能体"""
    
    def __init__(
        self,
        name: str,
        max_iterations: int = 5
    ):
        """
        初始化ReAct智能体
        
        Args:
            name: 智能体名称
            max_iterations: 最大迭代次数
        """
        self.name = name
        self.workflow = ReActWorkflow(max_iterations=max_iterations)
        self.tools: Dict[str, Callable] = {}
    
    def register_tool(self, tool_name: str, tool_func: Callable) -> None:
        """
        注册工具
        
        Args:
            tool_name: 工具名称
            tool_func: 工具函数
        """
        self.tools[tool_name] = tool_func
    
    def think(self, thought_content: str) -> None:
        """思考"""
        self.workflow.thought(thought_content)
    
    def act(self, action_type: str, action_input: Any) -> Any:
        """
        执行行动
        
        Args:
            action_type: 行动类型
            action_input: 行动输入
        
        Returns:
            行动结果
        """
        self.workflow.action(action_type, action_input)
        
        # 如果有对应的工具，执行它
        if action_type in self.tools:
            result = self.tools[action_type](action_input)
            return result
        
        return None
    
    def observe(self, observation_content: str) -> None:
        """观察结果"""
        self.workflow.observation(observation_content)
    
    def run_iteration(
        self,
        thought: str,
        action_type: str,
        action_input: Any
    ) -> str:
        """
        执行一次完整迭代
        
        Args:
            thought: 思考内容
            action_type: 行动类型
            action_input: 行动输入
        
        Returns:
            观察结果
        """
        self.think(thought)
        result = self.act(action_type, action_input)
        observation = str(result) if result else "No result"
        self.observe(observation)
        
        return observation
    
    def get_report(self) -> Dict[str, Any]:
        """获取智能体报告"""
        return {
            "agent_name": self.name,
            "workflow_summary": self.workflow.get_summary(),
            "context": self.workflow.get_context()
        }


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("ReAct Workflow Test")
    print("=" * 60)
    
    # 创建ReAct智能体
    agent = ReActAgent(name="test_agent", max_iterations=3)
    
    # 注册工具
    def search_tool(query):
        return f"Search result for: {query}"
    
    def calculate_tool(expression):
        try:
            return eval(expression)
        except:
            return "Invalid expression"
    
    agent.register_tool("search", search_tool)
    agent.register_tool("calculate", calculate_tool)
    
    # 执行ReAct循环
    print("\nExecuting ReAct cycle...")
    
    # 第1次迭代
    agent.think("I need to find information about Python")
    result = agent.act("search", "Python programming")
    agent.observe(f"Got: {result}")
    
    # 第2次迭代
    agent.think("Let me calculate something")
    result = agent.act("calculate", "2 + 3")
    agent.observe(f"Result: {result}")
    
    # 获取报告
    print("\nAgent Report:")
    report = agent.get_report()
    print(f"  Total iterations: {report['workflow_summary']['total_iterations']}")
    print(f"  Total thoughts: {report['workflow_summary']['total_thoughts']}")
    print(f"  Total actions: {report['workflow_summary']['total_actions']}")
    
    print("\nContext:")
    print(report['context'])
    
    print("\nTest completed!")
