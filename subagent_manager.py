#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响子代理系统 - 交交自己的子代理能力
不依赖OpenClaw subagent的独立任务调度
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from smart_orchestrator import SmartOrchestrator, call_model
import concurrent.futures
import threading
import queue
import json
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional

# =============================================================================
# 子代理类
# =============================================================================

class SubAgent:
    """交响自己的子代理"""
    
    def __init__(self, name: str, model_config: Dict[str, Any]):
        self.name = name
        self.model_config = model_config
        self.status = "idle"  # idle, working, completed, failed
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
    
    def execute(self, prompt: str) -> Dict[str, Any]:
        """执行任务"""
        self.status = "working"
        self.start_time = datetime.now()
        
        try:
            result = call_model(self.model_config, prompt)
            self.result = result
            self.status = "completed" if result.get("success") else "failed"
            if not result.get("success"):
                self.error = result.get("error")
        except Exception as e:
            self.error = str(e)
            self.status = "failed"
        
        self.end_time = datetime.now()
        return self.result or {"success": False, "error": self.error}
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "model": self.model_config.get("model_id"),
            "provider": self.model_config.get("provider"),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }

# =============================================================================
# 子代理管理器
# =============================================================================

class SubAgentManager:
    """子代理管理器 - 交交自己的子代理系统"""
    
    def __init__(self):
        self.agents: Dict[str, SubAgent] = {}
        self.task_queue = queue.Queue()
        self.results: Dict[str, Any] = {}
        self.lock = threading.Lock()
        
        # 加载模型配置
        self.orchestrator = SmartOrchestrator()
        print(f"📋 子代理系统加载了 {len(self.orchestrator.models)} 个模型")
    
    def create_agent(self, name: str, provider: str = None) -> SubAgent:
        """创建子代理"""
        # 选择模型
        model = None
        if provider:
            for m in self.orchestrator.models:
                if provider in m["provider"]:
                    model = m
                    break
        
        if not model and self.orchestrator.models:
            model = self.orchestrator.models[0]
        
        agent = SubAgent(name, model)
        self.agents[name] = agent
        return agent
    
    def execute_parallel(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """并行执行多个任务"""
        print(f"\n🚀 子代理系统并行执行 {len(tasks)} 个任务...")
        
        results = []
        
        # 为每个任务创建代理
        agents = []
        for i, task in enumerate(tasks):
            agent_name = f"agent_{i}_{task.get('expert', 'unknown')}"
            
            # 选择模型
            provider = task.get("provider")
            model = None
            for m in self.orchestrator.models:
                if provider and provider in m["provider"]:
                    model = m
                    break
            
            if not model:
                model = self.orchestrator.models[i % len(self.orchestrator.models)]
            
            agent = SubAgent(agent_name, model)
            self.agents[agent_name] = agent
            agents.append((agent, task))
        
        # 并行执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(agents)) as executor:
            futures = {
                executor.submit(agent.execute, task["prompt"]): (agent, task)
                for agent, task in agents
            }
            
            for future in concurrent.futures.as_completed(futures):
                agent, task = futures[future]
                try:
                    result = future.result()
                    results.append({
                        "expert": task.get("expert"),
                        "agent": agent.name,
                        "model": agent.model_config.get("model_id"),
                        "result": result
                    })
                    
                    status = "✅" if result.get("success") else "❌"
                    print(f"{status} {task.get('expert')} - {agent.name}")
                    
                except Exception as e:
                    print(f"❌ {task.get('expert')} - Error: {e}")
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self.agents),
            "agents": [a.get_info() for a in self.agents.values()]
        }

# =============================================================================
# 测试
# =============================================================================

def main():
    print("=" * 60)
    print("🎼 交响子代理系统测试")
    print("不依赖OpenClaw subagent的独立任务调度")
    print("=" * 60)
    
    # 创建子代理管理器
    manager = SubAgentManager()
    
    # 测试任务
    tasks = [
        {
            "expert": "林思远",
            "provider": "cherry-doubao",
            "prompt": "用一句话介绍你自己"
        },
        {
            "expert": "张晓明",
            "provider": "cherry-doubao",
            "prompt": "你最擅长什么"
        },
        {
            "expert": "王明远",
            "provider": "cherry-nvidia",
            "prompt": "Python有什么优点"
        },
        {
            "expert": "陈浩然",
            "provider": "cherry-doubao",
            "prompt": "如何保证代码安全"
        }
    ]
    
    # 并行执行
    results = manager.execute_parallel(tasks)
    
    # 统计
    print("\n" + "=" * 60)
    print("📊 执行结果")
    print("=" * 60)
    
    success = sum(1 for r in results if r["result"].get("success"))
    tokens = sum(r["result"].get("total_tokens", 0) for r in results)
    
    for r in results:
        status = "✅" if r["result"].get("success") else "❌"
        print(f"{status} {r['expert']} - {r['model']}")
    
    print(f"\n📈 成功率: {success}/{len(results)}")
    print(f"📊 总Token: {tokens}")
    
    # 状态
    status = manager.get_status()
    print(f"\n📋 子代理数量: {status['total_agents']}")
    
    return results

if __name__ == "__main__":
    main()
