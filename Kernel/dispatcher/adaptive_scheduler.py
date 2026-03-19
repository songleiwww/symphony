#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统v3.2.0 - 调度模块升级
引入任务分解与动态规划
"""
import json
import asyncio
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field

class TaskPriority(Enum):
    """任务优先级"""
    URGENT = 1      # 紧急
    HIGH = 2        # 高
    NORMAL = 3      # 普通
    LOW = 4         # 低

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"         # 待执行
    PLANNING = "planning"       # 规划中
    EXECUTING = "executing"     # 执行中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"           # 失败
    PAUSED = "paused"          # 暂停

@dataclass
class SubTask:
    """子任务"""
    id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    result: Any = None
    error: Optional[str] = None
    estimated_time: int = 60  # 秒
    actual_time: int = 0

@dataclass
class Task:
    """任务"""
    id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    subtasks: List[SubTask] = field(default_factory=list)
    parent_task: Optional[str] = None
    context: Dict = field(default_factory=dict)
    result: Any = None
    created_at: float = 0
    updated_at: float = 0

class TaskDecomposer:
    """任务分解器"""
    
    def __init__(self):
        self.decomposition_strategies = {
            "sequential": self._sequential_decompose,
            "parallel": self._parallel_decompose,
            "hierarchical": self._hierarchical_decompose,
            "conditional": self._conditional_decompose
        }
    
    def decompose(self, task: Task, strategy: str = "hierarchical") -> List[SubTask]:
        """
        分解任务为子任务
        
        Args:
            task: 原始任务
            strategy: 分解策略
        
        Returns:
            子任务列表
        """
        decomposer = self.decomposition_strategies.get(strategy, self._hierarchical_decompose)
        return decomposer(task)
    
    def _sequential_decompose(self, task: Task) -> List[SubTask]:
        """顺序分解 - 串行执行的子任务"""
        # 基于关键词分解
        keywords = ["首先", "然后", "接着", "最后", "步骤1", "步骤2", "步骤3"]
        subtasks = []
        
        # 简单分解
        steps = task.description.split("。")
        for i, step in enumerate(steps):
            if step.strip():
                subtask = SubTask(
                    id=f"{task.id}_step_{i+1}",
                    name=f"步骤{i+1}",
                    description=step.strip(),
                    dependencies=[subtasks[-1].id] if subtasks else [],
                    estimated_time=60
                )
                subtasks.append(subtask)
        
        return subtasks
    
    def _parallel_decompose(self, task: Task) -> List[SubTask]:
        """并行分解 - 独立可并行的子任务"""
        # 基于任务类型分解
        categories = {
            "分析": ["数据分析", "趋势分析", "对比分析"],
            "处理": ["数据清洗", "格式转换", "验证"],
            "输出": ["生成报告", "可视化", "导出"]
        }
        
        subtasks = []
        for i, (cat, subs) in enumerate(categories.items()):
            for j, sub in enumerate(subs):
                subtask = SubTask(
                    id=f"{task.id}_{cat}_{j}",
                    name=sub,
                    description=f"{cat}: {sub}",
                    estimated_time=45
                )
                subtasks.append(subtask)
        
        return subtasks
    
    def _hierarchical_decompose(self, task: Task) -> List[SubTask]:
        """层级分解 - 父子任务结构"""
        # 主任务
        main_subtask = SubTask(
            id=f"{task.id}_main",
            name="主任务",
            description=task.description,
            estimated_time=120
        )
        
        # 子任务1: 准备
        prep_subtask = SubTask(
            id=f"{task.id}_prep",
            name="准备阶段",
            description="收集所需信息和资源",
            dependencies=[],
            estimated_time=30
        )
        
        # 子任务2: 执行
        exec_subtask = SubTask(
            id=f"{task.id}_exec",
            name="执行阶段",
            description="执行核心任务",
            dependencies=[prep_subtask.id],
            estimated_time=60
        )
        
        # 子任务3: 验证
        verify_subtask = SubTask(
            id=f"{task.id}_verify",
            name="验证阶段",
            description="验证执行结果",
            dependencies=[exec_subtask.id],
            estimated_time=30
        )
        
        return [main_subtask, prep_subtask, exec_subtask, verify_subtask]
    
    def _conditional_decompose(self, task: Task) -> List[SubTask]:
        """条件分解 - 根据条件分支"""
        # 分支1: 成功路径
        success = SubTask(
            id=f"{task.id}_success",
            name="成功分支",
            description="执行成功流程",
            estimated_time=60
        )
        
        # 分支2: 失败处理
        fallback = SubTask(
            id=f"{task.id}_fallback",
            name="降级分支",
            description="执行降级处理",
            dependencies=[],
            estimated_time=45
        )
        
        return [success, fallback]

class DynamicPlanner:
    """动态规划器"""
    
    def __init__(self):
        self.execution_history: List[Dict] = []
    
    def plan(self, task: Task, context: Dict = None) -> Dict:
        """
        生成执行计划
        
        Args:
            task: 任务
            context: 执行上下文
        
        Returns:
            执行计划
        """
        # 1. 分析任务
        analysis = self._analyze_task(task)
        
        # 2. 选择策略
        strategy = self._select_strategy(analysis, context)
        
        # 3. 分解任务
        decomposer = TaskDecomposer()
        subtasks = decomposer.decompose(task, strategy)
        
        # 4. 排序子任务
        sorted_subtasks = self._sort_subtasks(subtasks)
        
        # 5. 生成计划
        plan = {
            "task_id": task.id,
            "strategy": strategy,
            "subtasks": [self._subtask_to_dict(s) for s in sorted_subtasks],
            "estimated_time": sum(s.estimated_time for s in sorted_subtasks),
            "parallel_groups": self._group_for_parallelism(sorted_subtasks)
        }
        
        # 记录历史
        self.execution_history.append({
            "task_id": task.id,
            "strategy": strategy,
            "subtask_count": len(sorted_subtasks)
        })
        
        return plan
    
    def _analyze_task(self, task: Task) -> Dict:
        """分析任务"""
        desc_length = len(task.description)
        complexity = "high" if desc_length > 200 else "medium" if desc_length > 50 else "low"
        
        return {
            "id": task.id,
            "complexity": complexity,
            "priority": task.priority,
            "has_dependencies": bool(task.context.get("dependencies"))
        }
    
    def _select_strategy(self, analysis: Dict, context: Dict = None) -> str:
        """选择分解策略"""
        if analysis["complexity"] == "high":
            return "hierarchical"
        elif analysis["complexity"] == "medium":
            return "conditional"
        else:
            return "sequential"
    
    def _sort_subtasks(self, subtasks: List[SubTask]) -> List[SubTask]:
        """拓扑排序子任务"""
        # 简单排序：先处理无依赖的
        sorted_tasks = []
        remaining = list(subtasks)
        
        while remaining:
            # 找没有未完成依赖的任务
            ready = [t for t in remaining 
                    if all(dep in [s.id for s in sorted_tasks] 
                          for dep in t.dependencies)]
            
            if not ready:
                # 死循环保护
                ready = [remaining[0]]
            
            # 按优先级排序
            ready.sort(key=lambda x: x.priority.value)
            sorted_tasks.append(ready[0])
            remaining.remove(ready[0])
        
        return sorted_tasks
    
    def _group_for_parallelism(self, subtasks: List[SubTask]) -> List[List[str]]:
        """分组以支持并行执行"""
        groups = []
        current_group = []
        
        for task in subtasks:
            if task.dependencies:
                # 有依赖，加入前一组
                if current_group:
                    groups.append([t.id for t in current_group])
                    current_group = []
            else:
                # 无依赖，可并行
                current_group.append(task)
        
        if current_group:
            groups.append([t.id for t in current_group])
        
        return groups
    
    def _subtask_to_dict(self, subtask: SubTask) -> Dict:
        """转换子任务为字典"""
        return {
            "id": subtask.id,
            "name": subtask.name,
            "description": subtask.description,
            "status": subtask.status.value,
            "dependencies": subtask.dependencies,
            "estimated_time": subtask.estimated_time
        }

class AdaptiveScheduler:
    """自适应调度器"""
    
    def __init__(self):
        self.planner = DynamicPlanner()
        self.execution_queue: asyncio.Queue = None
        self.running_tasks: Dict[str, Task] = {}
    
    async def schedule(self, task: Task) -> Dict:
        """
        调度任务
        
        Args:
            task: 任务
        
        Returns:
            执行结果
        """
        # 生成计划
        plan = self.planner.plan(task)
        
        # 更新任务状态
        task.status = TaskStatus.PLANNING
        task.subtasks = [SubTask(**s) for s in plan["subtasks"]]
        
        # 执行计划
        results = await self._execute_plan(task, plan)
        
        return {
            "task_id": task.id,
            "plan": plan,
            "results": results,
            "status": task.status.value
        }
    
    async def _execute_plan(self, task: Task, plan: Dict) -> List[Dict]:
        """执行计划"""
        results = []
        
        # 按组执行
        for group in plan["parallel_groups"]:
            group_results = []
            
            # 并行执行同组任务
            tasks = [self._execute_subtask(task, sub_id) for sub_id in group]
            group_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            results.extend(group_results)
        
        # 检查结果
        if all(isinstance(r, dict) and not r.get("error") for r in results):
            task.status = TaskStatus.COMPLETED
            task.result = results
        else:
            task.status = TaskStatus.FAILED
        
        return results
    
    async def _execute_subtask(self, task: Task, subtask_id: str) -> Dict:
        """执行子任务"""
        # 查找子任务
        subtask = next((s for s in task.subtasks if s.id == subtask_id), None)
        if not subtask:
            return {"error": "子任务不存在"}
        
        subtask.status = TaskStatus.EXECUTING
        
        try:
            # 模拟执行
            await asyncio.sleep(0.1)
            
            subtask.status = TaskStatus.COMPLETED
            subtask.result = f"完成: {subtask.name}"
            
            return {
                "subtask_id": subtask_id,
                "status": "completed",
                "result": subtask.result
            }
        except Exception as e:
            subtask.status = TaskStatus.FAILED
            subtask.error = str(e)
            return {
                "subtask_id": subtask_id,
                "status": "failed",
                "error": str(e)
            }


# 测试代码
if __name__ == "__main__":
    import time
    
    # 创建任务
    task = Task(
        id="task_001",
        name="序境系统升级",
        description="分析并优化序境系统的性能和安全性",
        priority=TaskPriority.HIGH,
        context={}
    )
    
    # 调度
    scheduler = AdaptiveScheduler()
    result = asyncio.run(scheduler.schedule(task))
    
    print("=== 调度结果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
