# -*- coding: utf-8 -*-
"""
Multi-Model Orchestrator v1.0
=============================
Core responsibilities:
1. Model health check -> available pool
2. DAG scheduling -> prevent cycles A->B->C->A
3. Continuous dispatch -> continue until task done
4. Tool auto-discovery -> Skills/MCP adaptive config
5. Resource monitor -> CPU/memory/API dynamic throttling
"""

import sqlite3
import time
import threading
import os
import sys
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict, deque

DATA_DIR = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data'
SKILLS_DIR = r'C:\Users\Administrator\.openclaw\workspace\skills'


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"


@dataclass
class DispatchNode:
    node_id: str
    model_id: str
    provider: str
    task_prompt: str
    depends_on: Set[str] = field(default_factory=set)
    child_nodes: List[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    depth: int = 0


class ResourceMonitor:
    """Monitor CPU/memory/API, dynamic throttle"""

    def __init__(self):
        self._lock = threading.Lock()
        self._api_call_times: Dict[str, List[float]] = defaultdict(list)
        self._throttled_until: Dict[str, float] = {}
        self._min_interval = 1.0

    def check_api_interval(self, provider: str) -> float:
        now = time.time()
        with self._lock:
            if provider in self._throttled_until:
                wait = self._throttled_until[provider] - now
                if wait > 0:
                    return wait
            if provider in self._api_call_times:
                recent = [t for t in self._api_call_times[provider] if now - t < 60]
                if len(recent) >= 30:
                    self._throttled_until[provider] = now + 5.0
                    return 5.0
            return 0.0

    def record_api_call(self, provider: str):
        now = time.time()
        with self._lock:
            self._api_call_times[provider].append(now)
            self._api_call_times[provider] = [
                t for t in self._api_call_times[provider] if now - t < 60
            ]

    def get_status(self) -> Dict:
        return {
            "providers_throttled": list(self._throttled_until.keys()),
            "can_schedule": True
        }


class ModelOrchestrator:
    """
    Orchestrates multi-model dispatch

    Flow:
    1. Health check -> available pool
    2. Parse task -> build DAG
    3. Cycle detection -> no cycles allowed
    4. Resource check -> dynamic throttle
    5. Execute nodes -> continuous until done
    6. Aggregate results
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self._db_path = f'{DATA_DIR}/symphony.db'
        self._resource_monitor = ResourceMonitor()
        self._federation = None
        self._nodes: Dict[str, DispatchNode] = {}

        # Config
        self._max_depth = 10
        self._max_concurrent = 5

        # Tool registry
        self._tool_registry: Dict[str, Dict] = {}
        self._auto_discover_tools()

    @property
    def federation(self):
        if self._federation is None:
            sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0, sys_path)
            from model_federation import ModelFederation
            self._federation = ModelFederation()
        return self._federation

    def _auto_discover_tools(self):
        """Scan skills dir, auto-register tools"""
        if not os.path.exists(SKILLS_DIR):
            return
        try:
            for skill_name in os.listdir(SKILLS_DIR):
                skill_path = os.path.join(SKILLS_DIR, skill_name)
                if not os.path.isdir(skill_path):
                    continue
                skill_file = os.path.join(skill_path, 'SKILL.md')
                if os.path.exists(skill_file):
                    self._tool_registry[skill_name] = {
                        "name": skill_name,
                        "type": "skill",
                        "path": skill_path,
                        "enabled": True
                    }
        except Exception as e:
            print(f"[Orchestrator] Tool discovery error: {e}")
        print(f"[Orchestrator] Discovered {len(self._tool_registry)} tools")

    def get_healthy_models(self) -> List[Tuple[str, str]]:
        """Get health-checked available models"""
        if not os.path.exists(self._db_path):
            return []
        conn = sqlite3.connect(self._db_path)
        conn.text_factory = str
        cur = conn.cursor()
        try:
            cur.execute("SELECT model_identifier, provider FROM model_config WHERE status='online'")
            results = [(r[0], r[1]) for r in cur.fetchall()]
        finally:
            conn.close()
        print(f"[Orchestrator] Available models: {len(results)}")
        return results

    def build_dag(self, task: Dict, depth: int = 0) -> Optional[str]:
        """Build dispatch DAG for task"""
        if depth > self._max_depth:
            return None

        node_id = f"node_{len(self._nodes)}_{int(time.time() * 1000)}"
        model_id, provider = self._select_best_model(task)

        node = DispatchNode(
            node_id=node_id,
            model_id=model_id,
            provider=provider,
            task_prompt=task.get('prompt', ''),
            depends_on=set(),
            depth=depth
        )
        self._nodes[node_id] = node

        # Handle subtasks as child nodes
        subtasks = task.get('subtasks', [])
        if subtasks and depth < self._max_depth:
            parent_id = node_id
            for subtask in subtasks:
                child_id = self.build_dag(subtask, depth + 1)
                if child_id:
                    self._nodes[child_id].depends_on.add(parent_id)
                    self._nodes[parent_id].child_nodes.append(child_id)

        return node_id

    def _select_best_model(self, task: Dict) -> Tuple[str, str]:
        """Select optimal model based on task type"""
        task_type = task.get('task_type', 'general')
        prompt = task.get('prompt', '').lower()
        combined = (prompt + ' ' + task_type).lower()

        # Task type keywords
        type_keywords = {
            'code': ['coder', 'code', 'programming', '代码', 'programming'],
            'reasoning': ['reason', 'logic', '推理', 'think', '思??],
            'vision': ['vision', 'image', 'visual', 'vl', '视觉', '图像', 'chart', 'screenshot'],
            'embedding': ['embedding', 'vector', '嵌入'],
            'general': []
        }

        detected = 'general'
        for t, kws in type_keywords.items():
            if any(kw.lower() in combined for kw in kws):
                detected = t
                break

        # Provider priority (cost-based)
        provider_priority = {
            'glm-4-flash': 1, 'zhipu': 1,
            'ali_bailian': 2,
            'modelscope': 3, 'nvidia': 4,
            'volcano': 5, 'minimax': 6, 'ollama': 7,
        }

        models = self.get_healthy_models()
        if not models:
            return ('glm-4-flash', 'zhipu')

        def score(item):
            model_id, provider = item
            s = provider_priority.get(provider, 99)
            if detected == 'code' and 'coder' in model_id.lower():
                s -= 5
            elif detected == 'reasoning' and ('r1' in model_id.lower() or 'qwq' in model_id.lower()):
                s -= 5
            elif detected == 'vision' and ('vl' in model_id.lower() or 'vision' in model_id.lower()):
                s -= 5
            return s

        models.sort(key=score)
        return models[0]

    def _detect_cycle(self) -> Optional[List[str]]:
        """Kahn's algorithm for cycle detection in DAG"""
        in_degree = {nid: len(n.depends_on) for nid, n in self._nodes.items()}
        queue = deque([nid for nid, d in in_degree.items() if d == 0])
        visited = 0

        while queue:
            nid = queue.popleft()
            visited += 1
            for child in self._nodes[nid].child_nodes:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if visited < len(self._nodes):
            cycle_nodes = [nid for nid, d in in_degree.items() if d > 0]
            path = [nid for nid in cycle_nodes]
            path_names = [self._nodes[nid].model_id for nid in path]
            return path_names

        return None

    def execute(self, task: Dict, max_depth: int = None) -> Dict:
        """Main execution entry"""
        if max_depth:
            self._max_depth = max_depth

        start_time = time.time()
        print(f"\n{'='*60}")
        print(f"[Orchestrator] Execute: {task.get('task', 'unknown')}")
        print(f"{'='*60}")

        self._nodes.clear()
        root_id = self.build_dag(task)

        if not root_id:
            return {"success": False, "error": "DAG build failed", "results": []}

        cycle = self._detect_cycle()
        if cycle:
            print(f"[ERROR] Cycle detected: {' -> '.join(cycle)}")
            return {
                "success": False,
                "error": f"Cycle forbidden: {' -> '.join(cycle)}",
                "results": [],
                "cycle": cycle
            }

        print(f"[DAG] Nodes: {len(self._nodes)}, root: {root_id}")

        results = self._execute_topo(root_id)

        return {
            "success": any(r.get('success') for r in results),
            "total_time": time.time() - start_time,
            "nodes_executed": len(results),
            "root_node": root_id,
            "results": results,
            "resource_status": self._resource_monitor.get_status()
        }

    def _execute_topo(self, root_id: str) -> List[Dict]:
        """Topological sort execution"""
        results = []

        def can_run(nid: str) -> bool:
            node = self._nodes.get(nid)
            if not node:
                return False
            return all(
                self._nodes.get(d).status == NodeStatus.COMPLETED
                for d in node.depends_on
            )

        pending = list(self._nodes.keys())

        while pending:
            runnable = [nid for nid in pending if can_run(nid)]
            if not runnable:
                break

            batch = runnable[:self._max_concurrent]

            for node_id in batch:
                result = self._exec_node(node_id)
                results.append(result)
                pending.remove(node_id)

        return results

    def _exec_node(self, node_id: str) -> Dict:
        """Execute single dispatch node"""
        node = self._nodes.get(node_id)
        if not node:
            return {"success": False, "error": f"Node not found: {node_id}"}

        node.status = NodeStatus.RUNNING
        print(f"[EXEC] {node.model_id}@{node.provider} (depth={node.depth})")

        wait = self._resource_monitor.check_api_interval(node.provider)
        if wait > 0:
            time.sleep(wait)

        try:
            from model_federation import InferenceRequest

            # Build full prompt with context
            full_prompt = self._build_full_prompt(node)

            request = InferenceRequest(
                messages=[{"role": "user", "content": full_prompt}],
                model=node.model_id,
                temperature=0.7,
                max_tokens=4096
            )

            self._resource_monitor.record_api_call(node.provider)
            result = self.federation.inference(request)

            if result.success:
                node.status = NodeStatus.COMPLETED
                node.result = result.content
                return {
                    "success": True,
                    "node_id": node_id,
                    "model": node.model_id,
                    "provider": node.provider,
                    "result": result.content,
                    "depth": node.depth
                }
            else:
                node.status = NodeStatus.FAILED
                node.error = result.error
                return {
                    "success": False,
                    "node_id": node_id,
                    "model": node.model_id,
                    "error": result.error
                }

        except Exception as e:
            node.status = NodeStatus.FAILED
            node.error = str(e)
            return {
                "success": False,
                "node_id": node_id,
                "model": node.model_id,
                "error": str(e)
            }

    def _build_full_prompt(self, node: DispatchNode) -> str:
        """Build full prompt with tools and upstream context"""
        prompt = node.task_prompt

        # Tools context
        if self._tool_registry:
            tools = [f"[{n}] {info.get('name', n)}"
                    for n, info in self._tool_registry.items() if info.get('enabled', True)]
            if tools:
                prompt += f"\n\n## Available Tools:\n" + "\n".join(tools[:10])

        # Upstream results
        for dep_id in node.depends_on:
            dep = self._nodes.get(dep_id)
            if dep and dep.result:
                prompt += f"\n\n## Upstream[{dep_id}] result:\n{dep.result[:500]}"

        return prompt

    def get_status(self) -> Dict:
        """Get orchestrator status"""
        completed = len([n for n in self._nodes.values() if n.status == NodeStatus.COMPLETED])
        failed = len([n for n in self._nodes.values() if n.status == NodeStatus.FAILED])
        running = len([n for n in self._nodes.values() if n.status == NodeStatus.RUNNING])
        pending = len([n for n in self._nodes.values() if n.status == NodeStatus.PENDING])

        return {
            "available_models": len(self.get_healthy_models()),
            "nodes_total": len(self._nodes),
            "nodes_completed": completed,
            "nodes_failed": failed,
            "nodes_running": running,
            "nodes_pending": pending,
            "tools_registered": len(self._tool_registry),
            "resource_status": self._resource_monitor.get_status()
        }

