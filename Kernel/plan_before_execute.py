#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统v3.2.0 - 执行模块升级
引入先规划后执行范式
"""
import asyncio
import json
import time
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class ExecutionPhase(Enum):
    """执行阶段"""
    IDLE = "idle"
    PLANNING = "planning"      # 规划阶段
    VALIDATING = "validating"  # 验证阶段
    EXECUTING = "executing"    # 执行阶段
    MONITORING = "monitoring"  # 监控阶段
    COMPLETED = "completed"   # 完成
    FAILED = "failed"         # 失败

@dataclass
class PlanStep:
    """规划步骤"""
    id: str
    name: str
    description: str
    expected_output: str
    estimated_time: int = 60
    required_tools: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    status: ExecutionPhase = ExecutionPhase.IDLE

@dataclass
class ExecutionContext:
    """执行上下文"""
    task_id: str
    user_input: str
    start_time: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)

class PlanGenerator:
    """规划生成器"""
    
    def __init__(self):
        self.planning_templates = {
            "analysis": self._plan_analysis,
            "development": self._plan_development,
            "research": self._plan_research,
            "general": self._plan_general
        }
    
    def generate_plan(self, user_input: str, task_type: str = "general") -> List[PlanStep]:
        """
        生成执行计划
        
        Args:
            user_input: 用户输入
            task_type: 任务类型
        
        Returns:
            规划步骤列表
        """
        planner = self.planning_templates.get(task_type, self._plan_general)
        return planner(user_input)
    
    def _plan_analysis(self, user_input: str) -> List[PlanStep]:
        """分析任务规划"""
        return [
            PlanStep(
                id="step_1",
                name="理解需求",
                description="分析用户输入，理解真实需求",
                expected_output="需求分析报告",
                estimated_time=30,
                required_tools=["nlp"],
                dependencies=[]
            ),
            PlanStep(
                id="step_2",
                name="数据收集",
                description="收集相关数据和信息",
                expected_output="数据集",
                estimated_time=60,
                required_tools=["search", "database"],
                dependencies=["step_1"]
            ),
            PlanStep(
                id="step_3",
                name="深度分析",
                description="进行深度分析和建模",
                expected_output="分析结果",
                estimated_time=120,
                required_tools=["analytics"],
                dependencies=["step_2"]
            ),
            PlanStep(
                id="step_4",
                name="生成报告",
                description="生成分析报告和建议",
                expected_output="完整报告",
                estimated_time=45,
                required_tools=["report"],
                dependencies=["step_3"]
            )
        ]
    
    def _plan_development(self, user_input: str) -> List[PlanStep]:
        """开发任务规划"""
        return [
            PlanStep(
                id="step_1",
                name="需求理解",
                description="理解开发需求和目标",
                expected_output="需求规格",
                estimated_time=30,
                required_tools=["nlp"],
                dependencies=[]
            ),
            PlanStep(
                id="step_2",
                name="架构设计",
                description="设计系统架构和模块",
                expected_output="架构文档",
                estimated_time=60,
                required_tools=["design"],
                dependencies=["step_1"]
            ),
            PlanStep(
                id="step_3",
                name="代码实现",
                description="实现代码功能",
                expected_output="源代码",
                estimated_time=180,
                required_tools=["code_editor"],
                dependencies=["step_2"]
            ),
            PlanStep(
                id="step_4",
                name="测试验证",
                description="编写测试并验证功能",
                expected_output="测试报告",
                estimated_time=90,
                required_tools=["test"],
                dependencies=["step_3"]
            ),
            PlanStep(
                id="step_5",
                name="优化部署",
                description="优化代码并部署",
                expected_output="部署结果",
                estimated_time=60,
                required_tools=["deploy"],
                dependencies=["step_4"]
            )
        ]
    
    def _plan_research(self, user_input: str) -> List[PlanStep]:
        """研究任务规划"""
        return [
            PlanStep(
                id="step_1",
                name="问题定义",
                description="明确研究问题和目标",
                expected_output="研究问题定义",
                estimated_time=30,
                dependencies=[]
            ),
            PlanStep(
                id="step_2",
                name="文献调研",
                description="搜索和分析相关文献",
                expected_output="文献综述",
                estimated_time=90,
                required_tools=["search"],
                dependencies=["step_1"]
            ),
            PlanStep(
                id="step_3",
                name="方案设计",
                description="设计研究方案",
                expected_output="研究方案",
                estimated_time=60,
                dependencies=["step_2"]
            ),
            PlanStep(
                id="step_4",
                name="实验执行",
                description="执行实验或分析",
                expected_output="实验结果",
                estimated_time=120,
                dependencies=["step_3"]
            ),
            PlanStep(
                id="step_5",
                name="结论总结",
                description="总结研究发现",
                expected_output="研究报告",
                estimated_time=45,
                dependencies=["step_4"]
            )
        ]
    
    def _plan_general(self, user_input: str) -> List[PlanStep]:
        """通用任务规划"""
        return [
            PlanStep(
                id="step_1",
                name="理解任务",
                description="理解用户任务",
                expected_output="任务理解",
                estimated_time=20,
                dependencies=[]
            ),
            PlanStep(
                id="step_2",
                name="执行任务",
                description="执行任务",
                expected_output="执行结果",
                estimated_time=60,
                dependencies=["step_1"]
            ),
            PlanStep(
                id="step_3",
                name="结果验证",
                description="验证执行结果",
                expected_output="验证报告",
                estimated_time=30,
                dependencies=["step_2"]
            )
        ]

class PlanValidator:
    """规划验证器"""
    
    def __init__(self):
        self.validation_rules = []
    
    def validate(self, plan: List[PlanStep], context: ExecutionContext) -> Dict:
        """
        验证规划
        
        Args:
            plan: 规划步骤
            context: 执行上下文
        
        Returns:
            验证结果
        """
        issues = []
        
        # 检查1: 依赖循环
        if self._has_circular_dependency(plan):
            issues.append({
                "type": "circular_dependency",
                "severity": "high",
                "message": "存在循环依赖"
            })
        
        # 检查2: 缺失依赖
        missing = self._check_missing_dependencies(plan)
        if missing:
            issues.append({
                "type": "missing_dependencies",
                "severity": "high",
                "message": f"缺失依赖: {missing}"
            })
        
        # 检查3: 估计时间
        total_time = sum(step.estimated_time for step in plan)
        if total_time > 600:  # 超过10分钟
            issues.append({
                "type": "long_execution",
                "severity": "medium",
                "message": f"预计执行时间{total_time}秒较长"
            })
        
        # 检查4: 资源需求
        all_tools = set()
        for step in plan:
            all_tools.update(step.required_tools)
        
        return {
            "valid": len([i for i in issues if i["severity"] == "high"]) == 0,
            "issues": issues,
            "total_steps": len(plan),
            "total_time": total_time,
            "required_tools": list(all_tools),
            "risk_score": self._calculate_risk(issues)
        }
    
    def _has_circular_dependency(self, plan: List[PlanStep]) -> bool:
        """检查循环依赖"""
        # 构建依赖图
        graph = {step.id: step.dependencies for step in plan}
        
        # DFS检测循环
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    return True
        
        return False
    
    def _check_missing_dependencies(self, plan: List[PlanStep]) -> List[str]:
        """检查缺失依赖"""
        plan_ids = {step.id for step in plan}
        missing = []
        
        for step in plan:
            for dep in step.dependencies:
                if dep not in plan_ids:
                    missing.append(f"{step.id}->{dep}")
        
        return missing
    
    def _calculate_risk(self, issues: List[Dict]) -> float:
        """计算风险分数"""
        weights = {"high": 0.5, "medium": 0.3, "low": 0.1}
        return sum(weights.get(i["severity"], 0.1) for i in issues)

class PlanExecutor:
    """规划执行器"""
    
    def __init__(self):
        self.validator = PlanValidator()
        self.execution_history: List[Dict] = []
    
    async def execute(self, plan: List[PlanStep], context: ExecutionContext) -> Dict:
        """
        执行规划
        
        Args:
            plan: 规划步骤
            context: 执行上下文
        
        Returns:
            执行结果
        """
        # 验证规划
        validation = self.validator.validate(plan, context)
        
        if not validation["valid"]:
            return {
                "success": False,
                "phase": "validation",
                "error": "规划验证失败",
                "issues": validation["issues"]
            }
        
        # 执行每个步骤
        results = []
        step_results = {}
        
        for step in plan:
            # 检查依赖是否满足
            deps_satisfied = all(
                step_results.get(dep, {}).get("status") == "completed"
                for dep in step.dependencies
            )
            
            if not deps_satisfied:
                step.status = ExecutionPhase.FAILED
                results.append({
                    "step_id": step.id,
                    "status": "skipped",
                    "error": "依赖未满足"
                })
                continue
            
            # 执行步骤
            step.status = ExecutionPhase.EXECUTING
            result = await self._execute_step(step, context)
            step_results[step.id] = result
            
            results.append(result)
            
            # 失败处理
            if result.get("status") == "failed":
                break
        
        # 生成最终报告
        success = all(r.get("status") == "completed" for r in results)
        
        final_result = {
            "success": success,
            "total_steps": len(plan),
            "completed_steps": len([r for r in results if r.get("status") == "completed"]),
            "failed_steps": len([r for r in results if r.get("status") == "failed"]),
            "step_results": results,
            "execution_time": time.time() - context.start_time,
            "validation": validation
        }
        
        # 记录历史
        self.execution_history.append(final_result)
        
        return final_result
    
    async def _execute_step(self, step: PlanStep, context: ExecutionContext) -> Dict:
        """执行单个步骤"""
        try:
            # 模拟执行
            await asyncio.sleep(0.1)
            
            step.status = ExecutionPhase.COMPLETED
            
            return {
                "step_id": step.id,
                "step_name": step.name,
                "status": "completed",
                "output": step.expected_output,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            step.status = ExecutionPhase.FAILED
            return {
                "step_id": step.id,
                "step_name": step.name,
                "status": "failed",
                "error": str(e)
            }

class PlanBeforeExecuteEngine:
    """先规划后执行引擎"""
    
    def __init__(self):
        self.planner = PlanGenerator()
        self.validator = PlanValidator()
        self.executor = PlanExecutor()
    
    async def process(self, user_input: str, task_type: str = "general") -> Dict:
        """
        处理用户请求
        
        Args:
            user_input: 用户输入
            task_type: 任务类型
        
        Returns:
            处理结果
        """
        # 创建上下文
        context = ExecutionContext(
            task_id=f"task_{int(time.time())}",
            user_input=user_input
        )
        
        # 阶段1: 规划
        plan = self.planner.generate_plan(user_input, task_type)
        
        # 阶段2: 验证
        validation = self.validator.validate(plan, context)
        
        # 阶段3: 执行
        result = await self.executor.execute(plan, context)
        
        return {
            "task_id": context.task_id,
            "task_type": task_type,
            "plan": [self._step_to_dict(p) for p in plan],
            "validation": validation,
            "execution": result
        }
    
    def _step_to_dict(self, step: PlanStep) -> Dict:
        """转换步骤为字典"""
        return {
            "id": step.id,
            "name": step.name,
            "description": step.description,
            "expected_output": step.expected_output,
            "estimated_time": step.estimated_time,
            "required_tools": step.required_tools,
            "dependencies": step.dependencies
        }


# 测试代码
if __name__ == "__main__":
    engine = PlanBeforeExecuteEngine()
    
    # 测试
    result = asyncio.run(engine.process(
        "分析序境系统的性能优化方案",
        task_type="analysis"
    ))
    
    print("=== 先规划后执行测试 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
