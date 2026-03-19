#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统v3.2.0 - 协作模块升级
引入A2A协议支持
"""
import asyncio
import json
import uuid
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class MessageType(Enum):
    """消息类型"""
    REQUEST = "request"           # 请求
    RESPONSE = "response"        # 响应
    TASK_PROPOSAL = "proposal"    # 任务提议
    ACCEPT = "accept"            # 接受
    REJECT = "reject"            # 拒绝
    COMPLETE = "complete"        # 完成
    ERROR = "error"              # 错误

class AgentStatus(Enum):
    """Agent状态"""
    IDLE = "idle"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"

@dataclass
class Agent:
    """Agent"""
    id: str
    name: str
    capabilities: List[str]
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class A2AMessage:
    """A2A消息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.REQUEST
    sender: str = ""
    receiver: str = ""
    task_id: str = ""
    content: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

class A2AProtocol:
    """A2A通信协议"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.task_registry: Dict[str, Dict] = {}
    
    def register_agent(self, agent: Agent):
        """注册Agent"""
        self.agents[agent.id] = agent
        print(f"[A2A] Agent注册: {agent.name} (ID: {agent.id})")
    
    def discover_agents(self, capability: str) -> List[Agent]:
        """发现Agent"""
        available = [
            agent for agent in self.agents.values()
            if capability in agent.capabilities 
            and agent.status == AgentStatus.IDLE
        ]
        return available
    
    async def send_message(self, message: A2AMessage):
        """发送消息"""
        # 添加到队列
        await self.message_queue.put(message)
        
        # 模拟发送
        print(f"[A2A] 消息发送: {message.sender} -> {message.receiver}")
        print(f"       类型: {message.type.value}, 任务: {message.task_id}")
        
        # 如果是请求消息，模拟响应
        if message.type == MessageType.REQUEST:
            await self._handle_request(message)
    
    async def _handle_request(self, request: A2AMessage):
        """处理请求"""
        # 查找目标Agent
        target_agent = self.agents.get(request.receiver)
        if not target_agent:
            # 发送错误响应
            error_msg = A2AMessage(
                type=MessageType.ERROR,
                sender=request.receiver,
                receiver=request.sender,
                task_id=request.task_id,
                content={"error": "Agent不存在"}
            )
            await self.message_queue.put(error_msg)
            return
        
        # 检查Agent状态
        if target_agent.status == AgentStatus.BUSY:
            reject_msg = A2AMessage(
                type=MessageType.REJECT,
                sender=request.receiver,
                receiver=request.sender,
                task_id=request.task_id,
                content={"reason": "Agent忙"}
            )
            await self.message_queue.put(reject_msg)
            return
        
        # 接受任务
        target_agent.status = AgentStatus.BUSY
        target_agent.current_task = request.task_id
        
        accept_msg = A2AMessage(
            type=MessageType.ACCEPT,
            sender=request.receiver,
            receiver=request.sender,
            task_id=request.task_id,
            content={"estimated_time": 60}
        )
        await self.message_queue.put(accept_msg)
        
        # 模拟执行
        await asyncio.sleep(0.5)
        
        # 完成任务
        complete_msg = A2AMessage(
            type=MessageType.COMPLETE,
            sender=request.receiver,
            receiver=request.sender,
            task_id=request.task_id,
            content={"result": f"任务{request.task_id}已完成"}
        )
        await self.message_queue.put(complete_msg)
        
        # 恢复空闲
        target_agent.status = AgentStatus.IDLE
        target_agent.current_task = None
    
    async def request_task(self, sender_id: str, receiver_id: str, 
                          task_content: Dict) -> A2AMessage:
        """请求任务"""
        message = A2AMessage(
            type=MessageType.REQUEST,
            sender=sender_id,
            receiver=receiver_id,
            task_id=str(uuid.uuid4()),
            content=task_content
        )
        
        await self.send_message(message)
        return message
    
    async def propose_task(self, sender_id: str, task_proposal: Dict) -> List[A2AMessage]:
        """提议任务给多个Agent"""
        # 发现可用的Agent
        capability = task_proposal.get("required_capability", "")
        available_agents = self.discover_agents(capability)
        
        # 发送提议
        proposals = []
        for agent in available_agents[:3]:  # 最多提议给3个
            message = A2AMessage(
                type=MessageType.TASK_PROPOSAL,
                sender=sender_id,
                receiver=agent.id,
                task_id=str(uuid.uuid4()),
                content=task_proposal
            )
            await self.send_message(message)
            proposals.append(message)
        
        return proposals
    
    async def get_messages(self, agent_id: str, timeout: float = 1.0) -> List[A2AMessage]:
        """获取Agent的消息"""
        messages = []
        
        # 收集发给指定Agent的消息
        temp_messages = []
        while not self.message_queue.empty():
            try:
                msg = self.message_queue.get_nowait()
                if msg.receiver == agent_id or msg.receiver == "all":
                    messages.append(msg)
                else:
                    temp_messages.append(msg)
            except asyncio.QueueEmpty:
                break
        
        # 放回其他消息
        for msg in temp_messages:
            await self.message_queue.put(msg)
        
        return messages

class TaskNegotiator:
    """任务协商器"""
    
    def __init__(self, protocol: A2AProtocol):
        self.protocol = protocol
    
    async def negotiate(self, task_requirements: Dict) -> Optional[Agent]:
        """
        协商分配任务
        
        Args:
            task_requirements: 任务需求
        
        Returns:
            分配的Agent
        """
        required_capability = task_requirements.get("capability", "")
        
        # 发现可用Agent
        available = self.protocol.discover_agents(required_capability)
        
        if not available:
            print(f"[协商] 没有找到具备{required_capability}能力的Agent")
            return None
        
        # 选择最优Agent (简单策略: 随机)
        selected = available[0]
        
        # 发送任务请求
        await self.protocol.request_task(
            sender_id="coordinator",
            receiver_id=selected.id,
            task_content=task_requirements
        )
        
        # 等待响应
        await asyncio.sleep(0.6)
        
        messages = await self.protocol.get_messages("coordinator")
        
        # 检查是否接受
        for msg in messages:
            if msg.type == MessageType.ACCEPT:
                print(f"[协商] Agent {selected.name} 接受任务")
                return selected
        
        print(f"[协商] Agent {selected.name} 拒绝任务")
        return None

class CollaborationManager:
    """协作管理器"""
    
    def __init__(self):
        self.protocol = A2AProtocol()
        self.negotiator = TaskNegotiator(self.protocol)
        self.task_history: List[Dict] = []
    
    def setup_agents(self, agents: List[Dict]):
        """设置Agent"""
        for agent_data in agents:
            agent = Agent(
                id=agent_data["id"],
                name=agent_data["name"],
                capabilities=agent_data["capabilities"]
            )
            self.protocol.register_agent(agent)
    
    async def execute_collaborative_task(self, task: Dict) -> Dict:
        """
        执行协作任务
        
        Args:
            task: 任务描述
        
        Returns:
            执行结果
        """
        task_id = str(uuid.uuid4())
        print(f"\n=== 开始协作任务: {task_id} ===")
        
        # 分析任务需求
        requirements = self._analyze_task(task)
        
        # 协商分配
        agent = await self.negotiator.negotiate(requirements)
        
        if not agent:
            return {
                "task_id": task_id,
                "status": "failed",
                "error": "无法分配任务"
            }
        
        # 等待完成
        await asyncio.sleep(0.3)
        
        # 获取结果
        messages = await self.protocol.get_messages("coordinator")
        result_msg = next(
            (m for m in messages if m.type == MessageType.COMPLETE),
            None
        )
        
        # 记录历史
        self.task_history.append({
            "task_id": task_id,
            "assigned_agent": agent.name,
            "status": "completed" if result_msg else "pending",
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "task_id": task_id,
            "status": "completed",
            "assigned_agent": agent.name,
            "result": result_msg.content if result_msg else {}
        }
    
    def _analyze_task(self, task: Dict) -> Dict:
        """分析任务"""
        return {
            "capability": task.get("capability", "general"),
            "priority": task.get("priority", "normal"),
            "estimated_time": task.get("estimated_time", 60)
        }
    
    async def execute_multi_agent_task(self, task: Dict) -> Dict:
        """
        执行多Agent协作任务
        
        Args:
            task: 任务描述
        
        Returns:
            执行结果
        """
        task_id = str(uuid.uuid4())
        subtasks = task.get("subtasks", [])
        
        print(f"\n=== 开始多Agent协作: {task_id} ===")
        
        # 为每个子任务分配Agent
        results = []
        for subtask in subtasks:
            result = await self.execute_collaborative_task(subtask)
            results.append(result)
        
        # 汇总结果
        success_count = len([r for r in results if r.get("status") == "completed"])
        
        return {
            "task_id": task_id,
            "total_subtasks": len(subtasks),
            "completed": success_count,
            "results": results
        }


# 测试代码
if __name__ == "__main__":
    async def main():
        # 创建协作管理器
        manager = CollaborationManager()
        
        # 设置Agent
        agents = [
            {"id": "agent_1", "name": "陆念昭", "capabilities": ["reasoning", "planning"]},
            {"id": "agent_2", "name": "徐浩", "capabilities": ["coding", "development"]},
            {"id": "agent_3", "name": "郭熙", "capabilities": ["analysis", "research"]},
        ]
        manager.setup_agents(agents)
        
        # 执行协作任务
        result = await manager.execute_collaborative_task({
            "capability": "reasoning",
            "priority": "high"
        })
        
        print("\n=== 执行结果 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 执行多Agent任务
        multi_result = await manager.execute_multi_agent_task({
            "subtasks": [
                {"capability": "coding"},
                {"capability": "analysis"},
                {"capability": "reasoning"}
            ]
        })
        
        print("\n=== 多Agent结果 ===")
        print(json.dumps(multi_result, ensure_ascii=False, indent=2))
    
    asyncio.run(main())
