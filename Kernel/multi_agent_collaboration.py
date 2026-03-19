# -*- coding: utf-8 -*-
"""
多智能体协作框架 - Multi-Agent Collaboration Framework

功能：
- Agent注册与发现
- 任务分发与协调
- 消息传递
- 协作策略
- 状态同步
"""
import asyncio
import uuid
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import json


class AgentStatus(Enum):
    """Agent状态"""
    IDLE = "idle"
    BUSY = "busy"
    THINKING = "thinking"
    ERROR = "error"
    OFFLINE = "offline"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentInfo:
    """Agent信息"""
    id: str
    name: str
    role: str
    capabilities: List[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    current_task: str = ""
    load: float = 0.0  # 0-1
    metadata: Dict = field(default_factory=dict)


@dataclass
class Task:
    """任务"""
    id: str
    name: str
    description: str
    required_capabilities: List[str] = field(default_factory=list)
    priority: int = 5  # 1-10
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: str = ""
    result: Any = None
    error: str = ""
    created_at: float = field(default_factory=time.time)
    started_at: float = 0
    completed_at: float = 0
    metadata: Dict = field(default_factory=dict)


@dataclass
class Message:
    """Agent间消息"""
    id: str
    from_agent: str
    to_agent: str
    content: Any
    message_type: str = "text"
    timestamp: float = field(default_factory=time.time)


class MultiAgentSystem:
    """
    多智能体协作系统
    
    使用：
        mas = MultiAgentSystem()
        
        # 注册Agent
        mas.register_agent("agent1", "研究员", ["search", "analyze"])
        
        # 分发任务
        task = mas.create_task("搜索", "搜索AI最新进展", ["search"])
        mas.dispatch_task(task)
        
        # 获取结果
        result = mas.wait_task(task.id)
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.tasks: Dict[str, Task] = {}
        self.messages: Dict[str, List[Message]] = defaultdict(list)
        self.task_queue: List[Task] = []
        
        # 事件回调
        self.on_task_start: Optional[Callable] = None
        self.on_task_complete: Optional[Callable] = None
        self.on_agent_status_change: Optional[Callable] = None
        
        # 统计
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_messages": 0
        }
        
        # 协作策略
        self.strategy = "load_balance"  # load_balance/round_robin/priority
    
    def register_agent(
        self,
        agent_id: str,
        name: str,
        role: str,
        capabilities: List[str] = None,
        metadata: Dict = None
    ):
        """
        注册Agent
        
        参数:
            agent_id: Agent ID
            name: 名称
            role: 角色
            capabilities: 能力列表
            metadata: 额外信息
        """
        self.agents[agent_id] = AgentInfo(
            id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities or [],
            status=AgentStatus.IDLE,
            metadata=metadata or {}
        )
        
        print(f"[MAS] Agent registered: {name} ({role})")
    
    def unregister_agent(self, agent_id: str):
        """注销Agent"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.status = AgentStatus.OFFLINE
            print(f"[MAS] Agent unregistered: {agent.name}")
    
    def get_available_agents(
        self,
        required_capabilities: List[str] = None
    ) -> List[AgentInfo]:
        """
        获取可用Agent
        
        参数:
            required_capabilities: 所需能力
        
        返回:
            可用Agent列表（按负载排序）
        """
        available = [
            a for a in self.agents.values()
            if a.status == AgentStatus.IDLE
        ]
        
        # 过滤能力
        if required_capabilities:
            available = [
                a for a in available
                if any(cap in a.capabilities for cap in required_capabilities)
            ]
        
        # 根据策略排序
        if self.strategy == "load_balance":
            available.sort(key=lambda a: a.load)
        elif self.strategy == "priority":
            available.sort(key=lambda a: -len(a.capabilities))
        
        return available
    
    def create_task(
        self,
        name: str,
        description: str,
        required_capabilities: List[str] = None,
        priority: int = 5,
        metadata: Dict = None
    ) -> Task:
        """
        创建任务
        
        参数:
            name: 任务名称
            description: 任务描述
            required_capabilities: 所需能力
            priority: 优先级
            metadata: 额外信息
        """
        task = Task(
            id=str(uuid.uuid4())[:8],
            name=name,
            description=description,
            required_capabilities=required_capabilities or [],
            priority=priority,
            metadata=metadata or {}
        )
        
        self.tasks[task.id] = task
        self.task_queue.append(task)
        self.stats["total_tasks"] += 1
        
        # 按优先级排序
        self.task_queue.sort(key=lambda t: -t.priority)
        
        print(f"[MAS] Task created: {name} (priority={priority})")
        
        return task
    
    def dispatch_task(self, task_id: str = None) -> bool:
        """
        分发任务
        
        参数:
            task_id: 任务ID，为None则分发队列中最高优先级任务
        
        返回:
            是否成功分发
        """
        # 获取任务
        if task_id:
            task = self.tasks.get(task_id)
            if not task:
                print(f"[MAS] Task not found: {task_id}")
                return False
        else:
            if not self.task_queue:
                print("[MAS] No tasks in queue")
                return False
            task = self.task_queue.pop(0)
        
        # 查找可用Agent
        agents = self.get_available_agents(task.required_capabilities)
        
        if not agents:
            # 没有可用Agent，放回队列
            self.task_queue.insert(0, task)
            print(f"[MAS] No available agents for task: {task.name}")
            return False
        
        # 选择最佳Agent
        agent = agents[0]
        
        # 分配任务
        task.status = TaskStatus.RUNNING
        task.assigned_agent = agent.id
        task.started_at = time.time()
        
        # 更新Agent状态
        agent.status = AgentStatus.BUSY
        agent.current_task = task.id
        agent.load = min(1.0, agent.load + 0.3)
        
        print(f"[MAS] Task dispatched: {task.name} -> {agent.name}")
        
        # 触发回调
        if self.on_task_start:
            self.on_task_start(task, agent)
        
        return True
    
    def complete_task(
        self,
        task_id: str,
        result: Any = None,
        error: str = ""
    ):
        """
        完成任务
        
        参数:
            task_id: 任务ID
            result: 任务结果
            error: 错误信息
        """
        task = self.tasks.get(task_id)
        if not task:
            return
        
        task.completed_at = time.time()
        
        if error:
            task.status = TaskStatus.FAILED
            task.error = error
            self.stats["failed_tasks"] += 1
        else:
            task.status = TaskStatus.COMPLETED
            task.result = result
            self.stats["completed_tasks"] += 1
        
        # 释放Agent
        if task.assigned_agent:
            agent = self.agents.get(task.assigned_agent)
            if agent:
                agent.status = AgentStatus.IDLE
                agent.current_task = ""
                agent.load = max(0, agent.load - 0.3)
        
        print(f"[MAS] Task completed: {task.name} ({task.status.value})")
        
        # 触发回调
        if self.on_task_complete:
            self.on_task_complete(task)
    
    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: Any,
        message_type: str = "text"
    ) -> Message:
        """
        发送消息
        
        参数:
            from_agent: 发送方ID
            to_agent: 接收方ID
            content: 消息内容
            message_type: 消息类型
        
        返回:
            消息对象
        """
        message = Message(
            id=str(uuid.uuid4())[:8],
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            message_type=message_type
        )
        
        self.messages[to_agent].append(message)
        self.stats["total_messages"] += 1
        
        print(f"[MAS] Message: {from_agent} -> {to_agent}")
        
        return message
    
    def get_messages(self, agent_id: str) -> List[Message]:
        """获取Agent的消息"""
        messages = self.messages.get(agent_id, [])
        self.messages[agent_id] = []  # 清空
        return messages
    
    def wait_task(self, task_id: str, timeout: float = 30) -> Task:
        """
        等待任务完成
        
        参数:
            task_id: 任务ID
            timeout: 超时时间（秒）
        
        返回:
            任务对象
        """
        start = time.time()
        
        while time.time() - start < timeout:
            task = self.tasks.get(task_id)
            if task and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return task
            time.sleep(0.1)
        
        return self.tasks.get(task_id)
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        return {
            "total_agents": len(self.agents),
            "available_agents": len([
                a for a in self.agents.values()
                if a.status == AgentStatus.IDLE
            ]),
            "total_tasks": self.stats["total_tasks"],
            "completed_tasks": self.stats["completed_tasks"],
            "failed_tasks": self.stats["failed_tasks"],
            "pending_tasks": len(self.task_queue),
            "total_messages": self.stats["total_messages"],
            "agents": [
                {
                    "name": a.name,
                    "role": a.role,
                    "status": a.status.value,
                    "load": a.load
                }
                for a in self.agents.values()
            ]
        }
    
    def set_strategy(self, strategy: str):
        """设置协作策略"""
        self.strategy = strategy
        print(f"[MAS] Strategy set to: {strategy}")


# 测试
if __name__ == "__main__":
    print("=== 多智能体协作测试 ===")
    
    # 创建系统
    mas = MultiAgentSystem()
    
    # 注册Agent
    mas.register_agent("agent1", "研究员A", "searcher", ["search", "analyze"])
    mas.register_agent("agent2", "研究员B", "analyzer", ["analyze", "report"])
    mas.register_agent("agent3", "研究员C", "coder", ["code", "debug"])
    
    # 创建任务
    task1 = mas.create_task(
        "搜索AI进展",
        "搜索2026年AI最新进展",
        required_capabilities=["search"],
        priority=8
    )
    
    task2 = mas.create_task(
        "分析数据",
        "分析搜索结果",
        required_capabilities=["analyze"],
        priority=6
    )
    
    print()
    print(f"任务队列: {len(mas.task_queue)} tasks")
    
    # 分发任务
    mas.dispatch_task()
    mas.dispatch_task()
    
    print()
    print("系统状态:")
    status = mas.get_system_status()
    print(f"  Agents: {status['available_agents']}/{status['total_agents']}")
    print(f"  Tasks: {status['completed_tasks']}/{status['total_tasks']}")
    
    # 模拟完成任务
    mas.complete_task(task1.id, result={"data": "AI进展报告"})
    mas.complete_task(task2.id, result={"分析": "增长趋势"})
    
    print()
    print("多智能体协作测试通过!")
