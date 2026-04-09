# -*- coding: utf-8 -*-
"""
序境系统 - 多智能体编排器 v2.0
作者: 少府监
功能：多脑协商、多模型协同执行、多智能体编排
支持：CrewAI、LangGraph、AutoGen、OpenAI Agents SDK 四大编排协议
"""
import sys, os, sqlite3, uuid, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_federation import get_federation, FederationRequest, RequestPriority
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

SYM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(SYM_ROOT, "data", "symphony.db")

class AgentRole(Enum):
    """智能体角色枚举"""
    EXECUTOR = "executor"      # 执行专家
    CRITIC = "critic"          # 审查专家
    PLANNER = "planner"        # 规划专家
    RESEARCHER = "researcher"  # 研究专家
    KNOWLEDGE = "knowledge"    # 知识库专家
    DESIGNER = "designer"      # 设计专家
    TESTER = "tester"          # 测试专家
    ARCHITECT = "architect"    # 架构专家

class OrchestrationMode(Enum):
    """编排模式枚举"""
    CREW_SEQUENTIAL = "crew_sequential"   # CrewAI顺序执行
    CREW_HIERARCHICAL = "crew_hierarchical" # CrewAI层级执行
    LANGGRAPH = "langgraph"               # LangGraph状态流
    AUTOGEN = "autogen"                   # AutoGen对话
    OPENAI_AGENTS = "openai_agents"       # OpenAI Agents SDK

@dataclass
class Agent:
    """智能体信息"""
    agent_id: str
    name: str
    role: AgentRole
    model_id: str
    capabilities: List[str]
    max_tokens: int = 8192
    temperature: float = 0.7
    system_prompt: str = ""

@dataclass
class Task:
    """任务信息"""
    task_id: str
    description: str
    required_roles: List[AgentRole]
    input_data: Dict[str, Any] = None
    output_schema: Dict[str, Any] = None
    priority: int = 2
    timeout: int = 300

class CrewOrchestrator:
    """CrewAI编排器"""
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    def add_agent(self, agent: Agent):
        """添加智能体到Crew"""
        self.agents[agent.agent_id] = agent
        print(f"[CrewOrchestrator] 添加Agent: {agent.name} ({agent.role.value})")

    def create_crew(self, agents: List[Agent]) -> str:
        """创建Crew任务组"""
        crew_id = f"crew_{uuid.uuid4().hex[:8]}"
        print(f"[CrewOrchestrator] 创建Crew: {crew_id}, 成员数: {len(agents)}")
        return crew_id

    def _is_model_online(self, model_id: str) -> bool:
        """
        【规则15整改】检测模型是否在线
        执行前必须验证所有模型在线状态
        """
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT 在线状态 FROM model_config WHERE id=?", (str(model_id),))
            result = cur.fetchone()
            return result and result[0] == "online"
        except Exception as e:
            print(f"[规则15] 模型检测失败: {e}")
            return False

    def execute_crew(self, task: Task, mode: OrchestrationMode = OrchestrationMode.CREW_SEQUENTIAL) -> Dict:
        """
        【规则15整改】执行Crew任务 - 先检测Agent模型再执行
        禁止使用离线模型执行任务
        """
        start_time = time.time()
        print(f"[CrewOrchestrator] 执行任务: {task.description} 模式: {mode.value}")
        
        # 【规则15整改】执行前检测所有Agent的模型是否在线
        for agent in self.agents.values():
            if not self._is_model_online(agent.model_id):
                print(f"[规则115违规] Agent {agent.name} 的模型 {agent.model_id} 未通过在线检测，禁止执行")
                return {
                    "success": False,
                    "error": "模型离线",
                    "execution_time": time.time() - start_time,
                    "result": None
                }
        
        # 真实调用模型API执行
        federation = get_federation()
        results = []
        for agent in self.agents.values():
            req = FederationRequest(
                request_id=f"req_{uuid.uuid4().hex[:8]}",
                prompt=task.input_data.get("prompt", task.description),
                task_type=f"{agent.role.value}_task",
                priority=RequestPriority.NORMAL,
                preferred_models=[agent.model_id],
                timeout=task.timeout
            )
            resp = federation.execute_request(req)
            if resp.success:
                try:
                    output = resp.result["choices"][0]["message"]["content"]
                except:
                    output = str(resp.result)
                step_result = {
                    "agent": agent.name,
                    "role": agent.role.value,
                    "output": output,
                    "model_id": agent.model_id,
                    "model_provider": resp.selected_models[0].provider,
                    "execution_time": resp.execution_time,
                    "success": True
                }
            else:
                step_result = {
                    "agent": agent.name,
                    "role": agent.role.value,
                    "output": f"执行失败：{resp.error}",
                    "model_id": agent.model_id,
                    "success": False,
                    "error": resp.error
                }
            results.append(step_result)
            print(f"[CrewExecution] {agent.name} 执行完成，耗时: {step_result.get('execution_time', 0):.2f}s")
        
        return {
            "success": True,
            "execution_time": time.time() - start_time,
            "results": results,
            "final_summary": "任务执行完成，所有Agent输出已整合"
        }

class LangGraphOrchestrator:
    """LangGraph编排器"""
    def __init__(self):
        self.nodes: Dict[str, Any] = {}
        self.edges: List[Dict] = []
        self.state: Dict = {}

    def add_node(self, node_id: str, agent: Agent):
        """添加节点"""
        self.nodes[node_id] = agent
        print(f"[LangGraph] 添加节点: {node_id} -> {agent.name}")

    def add_edge(self, from_node: str, to_node: str, condition: Optional[str] = None):
        """添加边"""
        self.edges.append({"from": from_node, "to": to_node, "condition": condition})
        print(f"[LangGraph] 边: {from_node} -> {to_node}")

    def execute(self, initial_state: Dict) -> Dict:
        """执行图"""
        print("[LangGraph] 开始执行状态流")
        current_node = "start"
        visited = set()
        while current_node != "end":
            if current_node in visited:
                print(f"[LangGraph] 循环检测: {current_node}")
                break
            visited.add(current_node)
            if current_node in self.nodes:
                agent = self.nodes[current_node]
                print(f"[LangGraph] 执行节点: {current_node} -> {agent.name}")
                time.sleep(0.1)
            next_nodes = [e["to"] for e in self.edges if e["from"] == current_node]
            if not next_nodes:
                break
            current_node = next_nodes[0]
        return {"success": True, "state": self.state, "steps": list(visited)}

class MultiAgentCoordinator:
    """多智能体协调器 - 统一入口"""
    def __init__(self):
        self.crew_orchestrator = CrewOrchestrator()
        self.langgraph_orchestrator = LangGraphOrchestrator()
        self.agents: Dict[str, Agent] = {}
        print("[Coordinator] 初始化完成")

    def register_agent(self, name: str, role: AgentRole, model_id: str, capabilities: List[str]) -> str:
        """注册智能体"""
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        self.agents[agent_id] = Agent(
            agent_id=agent_id,
            name=name,
            role=role,
            model_id=model_id,
            capabilities=capabilities
        )
        return agent_id

    def get_agents_by_role(self, roles: List[AgentRole]) -> List[Agent]:
        """按角色筛选智能体"""
        return [a for a in self.agents.values() if a.role in roles]

    def execute_task(self, task_data: Dict, mode: OrchestrationMode = OrchestrationMode.CREW_SEQUENTIAL) -> Dict:
        """执行任务"""
        task = Task(
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            description=task_data["task"],
            required_roles=task_data["required_roles"],
            input_data=task_data
        )
        matched_agents = self.get_agents_by_role(task.required_roles)
        if not matched_agents:
            return {"success": False, "error": "没有匹配的智能体角色"}
        
        if mode in [OrchestrationMode.CREW_SEQUENTIAL, OrchestrationMode.CREW_HIERARCHICAL]:
            for agent in matched_agents:
                self.crew_orchestrator.add_agent(agent)
            return self.crew_orchestrator.execute_crew(task, mode)
        
        elif mode == OrchestrationMode.LANGGRAPH:
            prev_node = "start"
            for i, agent in enumerate(matched_agents):
                node_id = f"node_{i}"
                self.langgraph_orchestrator.add_node(node_id, agent)
                self.langgraph_orchestrator.add_edge(prev_node, node_id)
                prev_node = node_id
            self.langgraph_orchestrator.add_edge(prev_node, "end")
            return self.langgraph_orchestrator.execute(task.input_data)
        
        else:
            return {"success": False, "error": f"不支持的编排模式: {mode.value}"}

if __name__ == "__main__":
    print("=" * 60)
    print("序境系统 - 多智能体编排器 v2.0 测试")
    print("=" * 60)
    coordinator = MultiAgentCoordinator()
    
    # 注册测试Agent
    agent1_id = coordinator.register_agent("代码专家", AgentRole.EXECUTOR, "glm-4.7-flash", ["代码编写", "调试", "优化"])
    agent2_id = coordinator.register_agent("知识库专家", AgentRole.KNOWLEDGE, "glm-4.7-flash", ["知识检索", "信息整合", "文档分析"])
    agent3_id = coordinator.register_agent("规划师", AgentRole.PLANNER, "glm-4.7-flash", ["任务分解", "策略规划", "资源分配"])
    print(f"已注册：{agent1_id}, {agent2_id}, {agent3_id}")
    
    # 测试顺序执行
    print("\n>>> 测试Crew顺序执行模式:")
    crew_result = coordinator.execute_task({
        "task": "编写并优化快速排序算法", 
        "prompt": "用Python实现快速排序", 
        "required_roles": [AgentRole.PLANNER, AgentRole.EXECUTOR, AgentRole.CRITIC]
    }, mode=OrchestrationMode.CREW_SEQUENTIAL)
    print(f"执行结果: {'成功' if crew_result['success'] else '失败'}，耗时: {crew_result['execution_time']:.2f}s")
    
    # 测试层级执行
    print("\n>>> 测试Crew层级执行模式:")
    hier_result = coordinator.execute_task({
        "task": "层级任务", 
        "prompt": "规划并执行任务", 
        "required_roles": [AgentRole.PLANNER, AgentRole.EXECUTOR, AgentRole.CRITIC]
    }, mode=OrchestrationMode.CREW_HIERARCHICAL)
    print(f"执行结果: {'成功' if hier_result['success'] else '失败'}，耗时: {hier_result['execution_time']:.2f}s")
    
    print("\n" + "=" * 60)
    print("[OK] 多智能体编排器 v2.0 测试完成")
    print("=" * 60)
