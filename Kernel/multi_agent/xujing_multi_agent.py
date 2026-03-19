# -*- coding: utf-8 -*-
"""
序境系统 - 多模型合作系统 (Agent协作架构)
基于评估推荐的Agent协作/多智能体规划方案实现
"""
import sqlite3
import time
import uuid
from typing import Dict, List, Optional, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Agent类型"""
    CONTROLLER = "controller"      # 主控制器
    EXECUTOR = "executor"          # 执行Agent
    KNOWLEDGE = "knowledge"        # 知识Agent (RAG)
    META = "meta"                 # 元Agent (调度策略)
    ENSEMBLE = "ensemble"         # 融合Agent


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class XujingAgent:
    """
    序境Agent基类
    """

    def __init__(self, agent_id: str, agent_type: AgentType, name: str, description: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.capabilities = []
        self.models = []
        self.status = "idle"
        self.task_history = []

    def add_capability(self, capability: str):
        """添加能力"""
        self.capabilities.append(capability)

    def assign_model(self, model_id: str, model_name: str):
        """分配模型"""
        self.models.append({"id": model_id, "name": model_name})

    def execute_task(self, task: Dict) -> Dict:
        """执行任务"""
        self.status = "running"
        result = {
            "agent_id": self.agent_id,
            "task_id": task.get("task_id"),
            "status": "success",
            "output": None,
            "timestamp": time.time()
        }
        self.status = "idle"
        return result


class ControllerAgent(XujingAgent):
    """
    主控制器Agent
    负责任务分发、流程协调、结果汇总
    """

    def __init__(self):
        super().__init__(
            agent_id="controller_001",
            agent_type=AgentType.CONTROLLER,
            name="主控制器",
            description="负责任务分发、流程协调、结果汇总"
        )
        self.sub_agents = []
        self.workflows = {}

    def add_sub_agent(self, agent: XujingAgent):
        """添加子Agent"""
        self.sub_agents.append(agent)

    def route_task(self, task: Dict) -> str:
        """路由任务到合适的Agent"""
        task_type = task.get("type", "general")

        # 根据任务类型路由
        if task_type == "knowledge":
            return "knowledge_001"
        elif task_type == "execution":
            return "executor_001"
        elif task_type == "meta":
            return "meta_001"
        else:
            return "executor_001"

    def coordinate(self, task: Dict, agents: Dict) -> Dict:
        """协调多Agent协作"""
        # 1. 分析任务
        task_type = task.get("type", "general")

        # 2. 选择合适的Agent
        target_agent_id = self.route_task(task)

        # 3. 分发任务
        if target_agent_id in agents:
            agent = agents[target_agent_id]
            result = agent.execute_task(task)
            return result
        else:
            return {"error": "Agent not found", "agent_id": target_agent_id}


class ExecutorAgent(XujingAgent):
    """
    执行Agent
    负责78+模型调度、任务执行
    """

    def __init__(self, db_path: str):
        super().__init__(
            agent_id="executor_001",
            agent_type=AgentType.EXECUTOR,
            name="执行Agent",
            description="负责78+模型调度、任务执行"
        )
        self.db_path = db_path
        self.load_models()

    def load_models(self):
        """加载可用模型"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            SELECT id, 模型名称, API地址, API密钥, 在线状态
            FROM 模型配置表
            WHERE 在线状态 = 'online'
            LIMIT 20
        ''')

        rows = c.fetchall()
        for r in rows:
            self.add_model({
                "id": r[0],
                "name": r[1],
                "api_url": r[2],
                "api_key": r[3],
                "status": r[4]
            })

        conn.close()

    def add_model(self, model: Dict):
        """添加模型"""
        self.models.append(model)

    def select_model(self, criteria: Dict = None) -> Optional[Dict]:
        """选择模型"""
        if not self.models:
            return None

        if criteria and "preferred" in criteria:
            for m in self.models:
                if criteria["preferred"] in m.get("name", ""):
                    return m

        # 默认返回第一个
        return self.models[0] if self.models else None

    def dispatch(self, task: Dict, model: Dict) -> Dict:
        """调度模型执行任务"""
        import requests

        result = {
            "task_id": task.get("task_id"),
            "model_id": model.get("id"),
            "model_name": model.get("name"),
            "status": "pending"
        }

        try:
            # 调用模型API
            headers = {
                'Authorization': 'Bearer ' + model.get("api_key", ""),
                'Content-Type': 'application/json'
            }

            data = {
                "model": model.get("name"),
                "messages": [{"role": "user", "content": task.get("prompt", "")}],
                "max_tokens": task.get("max_tokens", 500)
            }

            resp = requests.post(
                model.get("api_url", ""),
                headers=headers,
                json=data,
                timeout=30
            )

            if resp.status_code == 200:
                result["status"] = "success"
                result["output"] = resp.json()
            else:
                result["status"] = "failed"
                result["error"] = resp.text[:100]

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result


class KnowledgeAgent(XujingAgent):
    """
    知识Agent
    负责RAG、知识检索增强
    """

    def __init__(self):
        super().__init__(
            agent_id="knowledge_001",
            agent_type=AgentType.KNOWLEDGE,
            name="知识Agent",
            description="负责RAG、知识检索增强"
        )
        self.add_capability("知识检索")
        self.add_capability("上下文理解")
        self.add_capability("文档分析")

    def retrieve(self, query: str, memory_path: str = None) -> Dict:
        """检索知识"""
        results = []

        # 检索MEMORY.md
        if memory_path:
            try:
                with open(memory_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if query in content:
                        results.append({"source": "memory", "content": content[:500]})
            except:
                pass

        return {
            "query": query,
            "results": results,
            "count": len(results)
        }


class MetaAgent(XujingAgent):
    """
    元Agent
    负责调度策略、权重更新、模型评估
    """

    def __init__(self):
        super().__init__(
            agent_id="meta_001",
            agent_type=AgentType.META,
            name="元Agent",
            description="负责调度策略、权重更新、模型评估"
        )
        self.add_capability("策略优化")
        self.add_capability("模型评估")
        self.add_capability("权重更新")

    def evaluate_model(self, model_id: str, task_result: Dict) -> Dict:
        """评估模型表现"""
        score = 100

        if task_result.get("status") == "failed":
            score = 0
        elif task_result.get("status") == "error":
            score = 30

        return {
            "model_id": model_id,
            "score": score,
            "timestamp": time.time()
        }

    def update_weights(self, model_id: str, score: float):
        """更新模型权重"""
        logger.info(f"Updated model {model_id} weight to {score}")


class EnsembleAgent(XujingAgent):
    """
    融合Agent
    负责多模型结果投票、融合
    """

    def __init__(self):
        super().__init__(
            agent_id="ensemble_001",
            agent_type=AgentType.ENSEMBLE,
            name="融合Agent",
            description="负责多模型结果投票、融合"
        )
        self.add_capability("投票融合")
        self.add_capability("加权平均")
        self.add_capability("结果选择")

    def vote(self, results: List[Dict]) -> Dict:
        """投票融合结果"""
        if not results:
            return {"error": "No results to vote"}

        # 统计成功/失败
        success_count = sum(1 for r in results if r.get("status") == "success")
        total = len(results)

        # 多数决
        if success_count > total // 2:
            winner = [r for r in results if r.get("status") == "success"][0]
            return {
                "method": "majority_vote",
                "winner": winner,
                "score": success_count / total
            }
        else:
            return {
                "method": "majority_vote",
                "status": "failed",
                "score": success_count / total
            }

    def weighted_merge(self, results: List[Dict], weights: List[float] = None) -> Dict:
        """加权融合"""
        if not results:
            return {"error": "No results"}

        if weights is None:
            weights = [1.0] * len(results)

        # 简单加权平均
        total_weight = sum(weights)
        normalized = [w / total_weight for w in weights]

        return {
            "method": "weighted_merge",
            "results_count": len(results),
            "weights": normalized
        }


class MultiAgentSystem:
    """
    多Agent协作系统
    整合所有Agent实现协作
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.agents = {}
        self.task_queue = []
        self.init_agents()

    def init_agents(self):
        """初始化所有Agent"""
        # 主控制器
        self.agents["controller_001"] = ControllerAgent()

        # 执行Agent
        self.agents["executor_001"] = ExecutorAgent(self.db_path)

        # 知识Agent
        self.agents["knowledge_001"] = KnowledgeAgent()

        # 元Agent
        self.agents["meta_001"] = MetaAgent()

        # 融合Agent
        self.agents["ensemble_001"] = EnsembleAgent()

        # 绑定关系
        controller = self.agents["controller_001"]
        for agent_id, agent in self.agents.items():
            if agent_id != "controller_001":
                controller.add_sub_agent(agent)

    def execute(self, task: Dict) -> Dict:
        """执行任务"""
        task_id = task.get("task_id", str(uuid.uuid4())[:8])
        task["task_id"] = task_id

        # 1. 知识检索 (如果是知识任务)
        if task.get("type") == "knowledge":
            knowledge_agent = self.agents["knowledge_001"]
            memory_path = "C:/Users/Administrator/.openclaw/workspace/MEMORY.md"
            context = knowledge_agent.retrieve(task.get("prompt", ""), memory_path)
            task["context"] = context

        # 2. 执行任务
        controller = self.agents["controller_001"]
        result = controller.coordinate(task, self.agents)

        # 3. 元评估
        if result.get("model_id"):
            meta_agent = self.agents["meta_001"]
            evaluation = meta_agent.evaluate_model(result["model_id"], result)
            result["evaluation"] = evaluation

        return result

    def execute_ensemble(self, tasks: List[Dict]) -> Dict:
        """多模型并行执行+融合"""
        executor = self.agents["executor_001"]

        # 并行执行多个任务
        results = []
        for task in tasks:
            model = executor.select_model()
            if model:
                result = executor.dispatch(task, model)
                results.append(result)

        # 融合结果
        ensemble = self.agents["ensemble_001"]
        fused = ensemble.vote(results)

        return {
            "individual_results": results,
            "fused_result": fused
        }

    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            "total_agents": len(self.agents),
            "agents": {
                agent_id: {
                    "name": agent.name,
                    "type": agent.agent_type.value,
                    "status": agent.status,
                    "capabilities": agent.capabilities
                }
                for agent_id, agent in self.agents.items()
            }
        }


# 全局系统
_global_system = None

def get_multi_agent_system(db_path: str = None) -> MultiAgentSystem:
    """获取多Agent协作系统"""
    global _global_system

    if db_path is None:
        db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

    if _global_system is None:
        _global_system = MultiAgentSystem(db_path)

    return _global_system


# 测试
if __name__ == '__main__':
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

    print('=== Multi-Agent System Test ===\n')

    # 初始化系统
    system = MultiAgentSystem(db_path)

    # 查看状态
    status = system.get_status()
    print('System Status:')
    print('  Total Agents:', status['total_agents'])
    for agent_id, info in status['agents'].items():
        print(f'  - {info["name"]} ({info["type"]}): {info["capabilities"]}')

    # 测试执行
    print('\n=== Test Execution ===')
    task = {
        "type": "general",
        "prompt": "你好，请介绍序境系统",
        "max_tokens": 100
    }

    result = system.execute(task)
    print('Task Result:')
    print('  Status:', result.get('status'))
    print('  Model:', result.get('model_name'))

    # 测试多模型融合
    print('\n=== Test Ensemble ===')
    tasks = [
        {"prompt": "你好", "max_tokens": 50},
        {"prompt": "hello", "max_tokens": 50}
    ]

    ensemble_result = system.execute_ensemble(tasks)
    print('Ensemble Result:')
    print('  Method:', ensemble_result['fused_result'].get('method'))
    print('  Results:', len(ensemble_result['individual_results']))
