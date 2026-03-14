#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
OpenClaw SubAgent 协作接口
============================================================================
功能：
1. 与OpenClaw SubAgent通信
2. 任务分发与结果回收
3. 协作状态管理
============================================================================
"""

import json
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# ==================== 协作协议 ====================

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRole(Enum):
    """Agent角色"""
    ORCHESTRATOR = "orchestrator"      # 主编排器
    EXECUTOR = "executor"              # 执行器
    EVALUATOR = "evaluator"             # 评估器
    OPTIMIZER = "optimizer"             # 优化器


@dataclass
class SubAgentTask:
    """子任务"""
    task_id: str
    role: AgentRole
    description: str
    input_data: Dict = field(default_factory=dict)
    callback: Optional[Callable] = None
    timeout: int = 300
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: TaskStatus = TaskStatus.PENDING


@dataclass
class AgentMessage:
    """Agent消息"""
    message_id: str
    sender: str
    receiver: str
    content: Dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ==================== SubAgent管理器 ====================

class SubAgentManager:
    """SubAgent管理器"""
    
    def __init__(self, agent_id: str = "symphony"):
        self.agent_id = agent_id
        self.registered_agents: Dict[str, Dict] = {}
        self.task_queue: List[SubAgentTask] = []
        self.message_handlers: Dict[str, Callable] = {}
        self.collaboration_history: List[Dict] = []
    
    def register_agent(self, agent_id: str, capabilities: List[str], endpoint: str = ""):
        """注册Agent"""
        self.registered_agents[agent_id] = {
            'id': agent_id,
            'capabilities': capabilities,
            'endpoint': endpoint,
            'registered_at': datetime.now().isoformat(),
            'status': 'online'
        }
        print(f"[SubAgent] Registered: {agent_id} with capabilities: {capabilities}")
    
    def unregister_agent(self, agent_id: str):
        """注销Agent"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            print(f"[SubAgent] Unregistered: {agent_id}")
    
    def find_agents_by_capability(self, capability: str) -> List[str]:
        """按能力查找Agent"""
        return [
            agent_id for agent_id, info in self.registered_agents.items()
            if capability in info['capabilities']
        ]
    
    def dispatch_task(self, task: SubAgentTask) -> str:
        """分发任务"""
        task.status = TaskStatus.RUNNING
        self.task_queue.append(task)
        
        # 记录协作历史
        self.collaboration_history.append({
            'task_id': task.task_id,
            'role': task.role.value,
            'description': task.description,
            'dispatched_at': datetime.now().isoformat()
        })
        
        print(f"[SubAgent] Task dispatched: {task.task_id} to {task.role.value}")
        return task.task_id
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
    
    def handle_message(self, message: AgentMessage):
        """处理消息"""
        handler = self.message_handlers.get(message.content.get('type'))
        if handler:
            handler(message)
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'agent_id': self.agent_id,
            'registered_agents': len(self.registered_agents),
            'pending_tasks': len(self.task_queue),
            'collaboration_count': len(self.collaboration_history)
        }


# ==================== 交响协作器 ====================

class SymphonyCollaborator:
    """交响协作器 - 与OpenClaw SubAgent协作"""
    
    def __init__(self):
        self.agent_manager = SubAgentManager("symphony-orchestrator")
        self.evolution_results: Dict = {}
        self._init_default_agents()
    
    def _init_default_agents(self):
        """初始化默认Agent"""
        # 注册各种角色的Agent
        self.agent_manager.register_agent(
            "code-executor",
            ["python", "javascript", "execute"],
            "subagent:code"
        )
        self.agent_manager.register_agent(
            "file-manager", 
            ["read", "write", "edit"],
            "subagent:file"
        )
        self.agent_manager.register_agent(
            "researcher",
            ["search", "web_fetch", "browser"],
            "subagent:research"
        )
        self.agent_manager.register_agent(
            "tester",
            ["test", "verify", "validate"],
            "subagent:test"
        )
        self.agent_manager.register_agent(
            "communicator",
            ["message", "send", "notify"],
            "subagent:message"
        )
    
    def collaborate_with_subagent(self, capability: str, task: Dict) -> Dict:
        """与SubAgent协作"""
        # 查找具有所需能力的Agent
        agents = self.agent_manager.find_agents_by_capability(capability)
        
        if not agents:
            return {
                'success': False,
                'error': f'No agent found with capability: {capability}'
            }
        
        # 创建任务
        sub_task = SubAgentTask(
            task_id=f"collab_{int(time.time())}",
            role=AgentRole.EXECUTOR,
            description=task.get('description', ''),
            input_data=task
        )
        
        # 分发任务
        task_id = self.agent_manager.dispatch_task(sub_task)
        
        return {
            'success': True,
            'task_id': task_id,
            'agent': agents[0],
            'capability': capability,
            'message': f'Task dispatched to {agents[0]}'
        }
    
    def execute_evolution_with_agents(self, evolution_result: Dict) -> Dict:
        """使用多个Agent执行进化任务"""
        steps = []
        
        # 1. 代码执行Agent优化代码
        code_result = self.collaborate_with_subagent("python", {
            'description': 'Optimize evolution code',
            'data': evolution_result
        })
        steps.append(code_result)
        
        # 2. 测试Agent验证
        test_result = self.collaborate_with_subagent("test", {
            'description': 'Verify evolution result',
            'data': evolution_result
        })
        steps.append(test_result)
        
        # 3. 消息Agent通知结果
        notify_result = self.collaborate_with_subagent("message", {
            'description': 'Notify evolution completed',
            'data': evolution_result
        })
        steps.append(notify_result)
        
        return {
            'success': all(s.get('success', False) for s in steps),
            'steps': steps,
            'summary': f'Executed {len(steps)} collaboration steps'
        }
    
    def get_collaboration_status(self) -> Dict:
        """获取协作状态"""
        return {
            'manager': self.agent_manager.get_status(),
            'evolution_results': len(self.evolution_results)
        }


# ==================== 导出接口 ====================

def create_collaborator() -> SymphonyCollaborator:
    """创建协作器"""
    return SymphonyCollaborator()


# ==================== 测试 ====================

if __name__ == "__main__":
    print("="*60)
    print("OpenClaw SubAgent Collaboration Test")
    print("="*60)
    
    # 创建协作器
    collab = create_collaborator()
    
    # 查看注册的Agent
    print("\n--- Registered Agents ---")
    status = collab.get_collaboration_status()
    print(f"Manager Status: {status['manager']}")
    
    # 测试协作
    print("\n--- Collaboration Test ---")
    result = collab.collaborate_with_subagent("python", {
        'description': 'Test task',
        'code': 'print("Hello")'
    })
    print(f"Result: {result}")
    
    # 多Agent协作
    print("\n--- Multi-Agent Collaboration ---")
    evolution_result = {
        'algorithm': 'EvoPrompt',
        'score': 0.75,
        'iterations': 10
    }
    multi_result = collab.execute_evolution_with_agents(evolution_result)
    print(f"Multi-result: {multi_result}")
