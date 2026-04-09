# -*- coding: utf-8 -*-
"""
序境系统 - 多脑调度入口
=====================
统一入口：symphony_scheduler (基础调度) + DetectThenTeam (多脑组队) + FineGrainedWorkflow (工作流)

使用方式：
  from symphony_multi_brain import symphony_multi_brain
  result = symphony_multi_brain("你的问题")
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Kernel.multi_agent.detect_then_team import DetectThenTeamSystem
from Kernel.workflow.fine_grained_workflow import FineGrainedWorkflow, WorkflowBuilder
from Kernel.intelligent_strategy_scheduler import IntelligentStrategyScheduler
import symphony_scheduler

# 全局实例
_dtt_system = None
_strategy_scheduler = None

def get_dtt_system():
    global _dtt_system
    if _dtt_system is None:
        _dtt_system = DetectThenTeamSystem()
    return _dtt_system

def get_strategy_scheduler():
    global _strategy_scheduler
    if _strategy_scheduler is None:
        _strategy_scheduler = IntelligentStrategyScheduler()
    return _strategy_scheduler

def symphony_multi_brain(prompt: str, mode: str = "auto", team_size: int = 2) -> dict:
    """
    序境多脑调度主入口
    
    Args:
        prompt: 用户问题
        mode: "auto" | "single" | "team"
            - auto: 自动选择（简单问题single，复杂问题team）
            - single: 直接调度单一最优模型
            - team: Detect-Then-Team组队执行
        team_size: 组队模式下的团队大小
    
    Returns:
        dict: {
            "success": bool,
            "mode": str,
            "result": str,
            "team_info": dict,  # team模式时有效
            "latency_ms": int
        }
    """
    start_time = time.time()
    result = {"success": False, "mode": mode, "result": None, "latency_ms": 0}
    
    # Step 1: 策略调度器分析任务
    strategy_sched = get_strategy_scheduler()
    strategy_result = strategy_sched.schedule({"type": "unknown", "prompt": prompt})
    available_strategies = strategy_result.get("available_strategies", [])
    
    # Step 2: 根据策略选择模式
    if mode == "auto":
        # 简单问题用single，复杂问题用team
        if any(k in prompt.lower() for k in ["分析", "比较", "什么", "如何", "why", "how", "what"]):
            mode = "team"
        else:
            mode = "single"
    
    print(f"[symphony_multi_brain] mode={mode}, prompt={prompt[:50]}...")
    
    if mode == "single":
        # 单一模型直接调度
        print("[symphony_multi_brain] Using symphony_scheduler (single mode)")
        response = symphony_scheduler.symphony_scheduler(prompt)
        result["success"] = response is not None
        result["result"] = response or "调度失败"
        
    elif mode == "team":
        # Detect-Then-Team组队执行
        print("[symphony_multi_brain] Using DetectThenTeam (team mode)")
        dtt = get_dtt_system()
        
        # 执行组队调度
        exec_result = dtt.execute(prompt, team_size=team_size)
        
        result["success"] = exec_result["success_count"] > 0
        result["result"] = exec_result["final_result"]
        result["team_info"] = {
            "task_type": exec_result["team_info"]["task_type"],
            "team_size": exec_result["team_info"]["team_size"],
            "online_count": exec_result["team_info"]["online_count"],
            "success_count": exec_result["success_count"],
            "team": [m["model_id"] for m in exec_result["team_info"]["team"]]
        }
    
    result["latency_ms"] = int((time.time() - start_time) * 1000)
    result["available_strategies"] = available_strategies
    
    return result


def symphony_workflow(prompt: str, workflow_type: str = "text") -> dict:
    """
    使用FineGrainedWorkflow执行任务
    
    Args:
        prompt: 用户任务
        workflow_type: "text" | "voice" | "code"
    
    Returns:
        dict: Workflow执行结果
    """
    start_time = time.time()
    
    if workflow_type == "voice":
        wf = WorkflowBuilder.text_to_voice_workflow(prompt)
    elif workflow_type == "code":
        wf = WorkflowBuilder.code_generation_workflow(prompt)
    else:
        wf = FineGrainedWorkflow(prompt)
        wf.add_step("reasoning", "理解任务", {"task": prompt})
        # 调用symphony_scheduler
        wf.add_step("tool_call", "LLM调度", {
            "tool": "symphony_scheduler",
            "input": {"prompt": prompt}
        })
        wf.add_step("merge", "合并结果", {})
    
    exec_result = wf.execute()
    
    return {
        "success": exec_result.success,
        "output": exec_result.output,
        "steps": [{"name": s.name, "status": s.status.value} for s in exec_result.steps],
        "total_latency_ms": exec_result.total_latency_ms,
        "errors": exec_result.errors
    }


# ==================== 命令行测试 ====================
if __name__ == "__main__":
    print("=" * 60)
    print(" Symphony Multi-Brain 调度器测试")
    print("=" * 60)
    
    # Test 1: Single mode
    print("\n[Test1] Single mode (symphony_scheduler)")
    r1 = symphony_multi_brain("你好，今天天气怎么样？", mode="single")
    print(f"  Result: {r1['result'][:80] if r1['result'] else 'None'}")
    print(f"  Success: {r1['success']}, Latency: {r1['latency_ms']}ms")
    
    # Test 2: Team mode
    print("\n[Test2] Team mode (DetectThenTeam)")
    r2 = symphony_multi_brain("What is 1+1? Reply with one number.", mode="team", team_size=2)
    print(f"  Result: {r2['result']}")
    print(f"  Team: {r2.get('team_info', {}).get('team', [])}")
    print(f"  Success: {r2['success']}, Latency: {r2['latency_ms']}ms")
    
    # Test 3: Workflow
    print("\n[Test3] Workflow mode")
    r3 = symphony_workflow("你好", workflow_type="text")
    print(f"  Steps: {len(r3['steps'])}")
    print(f"  Success: {r3['success']}")
    
    print("\n" + "=" * 60)
    print(" 测试完成")
    print("=" * 60)
