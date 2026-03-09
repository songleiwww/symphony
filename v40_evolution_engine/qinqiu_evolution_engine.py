#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青丘v4.0进化引擎 - 核心引擎模块
QingQiu Evolution Engine v4.0 - Core Engine Module

架构师: 林思远
设计目标: 实现具有自我反思、持续进化能力的人工智能引擎核心
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable
import uuid
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntrospectionLevel(Enum):
    """自省级别枚举"""
    LIGHT = "light"      # 轻量级自省：基础状态检查
    NORMAL = "normal"    # 常规自省：状态+性能检查
    DEEP = "deep"        # 深度自省：状态+性能+逻辑合理性检查


class ExecutionStatus(Enum):
    """执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionResult:
    """执行结果数据类"""
    task_id: str
    status: ExecutionStatus
    result: Any = None
    error: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """获取执行耗时"""
        if self.end_time:
            return self.end_time - self.start_time
        return 0.0


@dataclass
class IntrospectionResult:
    """自省结果数据类"""
    level: IntrospectionLevel
    timestamp: float = field(default_factory=time.time)
    status: str = "healthy"
    issues: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MUSELoopResult:
    """MUSE循环结果数据类"""
    loop_id: str
    iteration: int
    observation: str
    understanding: str
    strategy: str
    execution: ExecutionResult
    learnings: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)


class SelfIntrospection:
    """
    三元自省模块
    Triple Introspection Module
    
    实现三个层次的自我检查：
    1. 状态自省：当前运行状态、资源使用情况
    2. 性能自省：执行效率、资源利用率
    3. 逻辑自省：决策合理性、结果正确性
    """
    
    def __init__(self, engine: 'QingQiuEvolutionEngine'):
        self.engine = engine
        self.introspection_history: List[IntrospectionResult] = []
        
    async def introspect(self, level: IntrospectionLevel = IntrospectionLevel.NORMAL) -> IntrospectionResult:
        """执行自省操作"""
        logger.info(f"执行{level.value}级别自省...")
        
        result = IntrospectionResult(level=level)
        
        # 1. 状态自省
        await self._introspect_state(result)
        
        if level in [IntrospectionLevel.NORMAL, IntrospectionLevel.DEEP]:
            # 2. 性能自省
            await self._introspect_performance(result)
            
        if level == IntrospectionLevel.DEEP:
            # 3. 逻辑自省
            await self._introspect_logic(result)
        
        self.introspection_history.append(result)
        
        # 保留最近100条自省记录
        if len(self.introspection_history) > 100:
            self.introspection_history.pop(0)
            
        logger.info(f"自省完成，状态: {result.status}, 发现问题: {len(result.issues)}个")
        return result
    
    async def _introspect_state(self, result: IntrospectionResult) -> None:
        """状态自省"""
        try:
            result.metrics['active_tasks'] = len(self.engine.active_tasks)
            result.metrics['completed_tasks'] = len(self.engine.execution_history)
            result.metrics['uptime'] = time.time() - self.engine.start_time
            result.metrics['pending_adaptations'] = len(self.engine.adaptation_queue)
            
            # 检查任务队列是否过长
            if len(self.engine.active_tasks) > self.engine.config.get('max_active_tasks', 100):
                result.issues.append({
                    'type': 'state',
                    'severity': 'warning',
                    'message': f"活动任务过多: {len(self.engine.active_tasks)}",
                    'suggestion': "考虑增加任务调度器的处理能力或限流"
                })
                
        except Exception as e:
            result.issues.append({
                'type': 'state',
                'severity': 'error',
                'message': f"状态自省失败: {str(e)}"
            })
            result.status = "unhealthy"
    
    async def _introspect_performance(self, result: IntrospectionResult) -> None:
        """性能自省"""
        try:
            # 计算平均执行时间
            if self.engine.execution_history:
                recent_executions = self.engine.execution_history[-20:]
                avg_duration = sum(r.duration for r in recent_executions) / len(recent_executions)
                result.metrics['average_execution_time'] = avg_duration
                
                # 检查是否有过慢的执行
                slow_executions = [r for r in recent_executions if r.duration > 10.0]  # 10秒阈值
                if slow_executions:
                    result.issues.append({
                        'type': 'performance',
                        'severity': 'warning',
                        'message': f"发现{len(slow_executions)}个执行时间超过10秒的任务",
                        'suggestion': "检查性能优化模块是否正常工作"
                    })
            
            # 检查内存使用（简化实现）
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            result.metrics['memory_usage_mb'] = memory_usage
            
            if memory_usage > self.engine.config.get('max_memory_mb', 2048):
                result.issues.append({
                    'type': 'performance',
                    'severity': 'warning',
                    'message': f"内存使用过高: {memory_usage:.2f}MB",
                    'suggestion': "考虑执行内存清理或优化数据结构"
                })
                
        except ImportError:
            logger.warning("psutil未安装，无法进行完整的性能自省")
        except Exception as e:
            result.issues.append({
                'type': 'performance',
                'severity': 'error',
                'message': f"性能自省失败: {str(e)}"
            })
    
    async def _introspect_logic(self, result: IntrospectionResult) -> None:
        """逻辑自省：检查最近决策的合理性"""
        try:
            # 检查最近的MUSE循环结果
            if self.engine.muse_history:
                recent_loops = self.engine.muse_history[-10:]
                success_rate = sum(1 for loop in recent_loops if loop.execution.status == ExecutionStatus.SUCCESS) / len(recent_loops)
                result.metrics['recent_success_rate'] = success_rate
                
                if success_rate < 0.7:  # 成功率低于70%
                    result.issues.append({
                        'type': 'logic',
                        'severity': 'warning',
                        'message': f"最近任务成功率过低: {success_rate:.1%}",
                        'suggestion': "检查决策逻辑是否需要调整，或重新训练模型"
                    })
            
            # 检查自省结果本身的一致性
            if len(self.introspection_history) >= 5:
                recent_issues = sum(len(r.issues) for r in self.introspection_history[-5:])
                if recent_issues > 10:
                    result.issues.append({
                        'type': 'logic',
                        'severity': 'warning',
                        'message': f"最近发现过多问题: {recent_issues}个",
                        'suggestion': "考虑进行深度系统诊断"
                    })
                    
        except Exception as e:
            result.issues.append({
                'type': 'logic',
                'severity': 'error',
                'message': f"逻辑自省失败: {str(e)}"
            })
    
    def get_introspection_history(self, limit: int = 20) -> List[IntrospectionResult]:
        """获取自省历史记录"""
        return self.introspection_history[-limit:]


class MUSELoop:
    """
    MUSE行动反思闭环
    Monitor - Understand - Strategize - Execute
    
    实现完整的感知-理解-决策-执行-反思闭环
    """
    
    def __init__(self, engine: 'QingQiuEvolutionEngine'):
        self.engine = engine
        self.loop_history: List[MUSELoopResult] = []
        self.max_history = 1000
        
    async def run(
        self,
        task: Dict[str, Any],
        max_iterations: int = 3,
        auto_improve: bool = True
    ) -> MUSELoopResult:
        """
        运行MUSE循环
        :param task: 任务描述
        :param max_iterations: 最大迭代次数
        :param auto_improve: 是否自动根据反思结果优化
        """
        loop_id = str(uuid.uuid4())
        logger.info(f"启动MUSE循环 {loop_id}, 任务: {task.get('description', '未命名任务')}")
        
        current_iteration = 0
        last_result: Optional[MUSELoopResult] = None
        
        while current_iteration < max_iterations:
            current_iteration += 1
            logger.info(f"MUSE循环迭代 {current_iteration}/{max_iterations}")
            
            # 1. Monitor (观察)：感知环境和当前状态
            observation = await self._monitor(task, last_result)
            
            # 2. Understand (理解)：分析问题和现状
            understanding = await self._understand(observation, task, last_result)
            
            # 3. Strategize (决策)：制定执行策略
            strategy = await self._strategize(understanding, task, last_result)
            
            # 4. Execute (执行)：执行策略
            execution = await self._execute(strategy, task)
            
            # 构建循环结果
            loop_result = MUSELoopResult(
                loop_id=loop_id,
                iteration=current_iteration,
                observation=observation,
                understanding=understanding,
                strategy=strategy,
                execution=execution
            )
            
            # 5. 反思学习
            await self._reflect(loop_result)
            
            # 保存历史
            self.loop_history.append(loop_result)
            if len(self.loop_history) > self.max_history:
                self.loop_history.pop(0)
            
            # 检查是否成功完成
            if execution.status == ExecutionStatus.SUCCESS:
                logger.info(f"MUSE循环 {loop_id} 在第{current_iteration}次迭代成功完成")
                return loop_result
                
            # 如果需要继续迭代，准备下一次
            last_result = loop_result
            if auto_improve:
                await self._apply_improvements(loop_result)
        
        logger.warning(f"MUSE循环 {loop_id} 达到最大迭代次数{max_iterations}，任务未完成")
        return last_result
    
    async def _monitor(self, task: Dict[str, Any], previous_result: Optional[MUSELoopResult]) -> str:
        """观察阶段：收集环境和状态信息"""
        observation_parts = []
        
        # 当前系统状态
        introspection = await self.engine.self_introspection.introspect(IntrospectionLevel.LIGHT)
        observation_parts.append(f"系统状态: {introspection.status}")
        observation_parts.append(f"活动任务数: {introspection.metrics.get('active_tasks', 0)}")
        
        # 任务本身信息
        observation_parts.append(f"任务目标: {task.get('description', '')}")
        observation_parts.append(f"任务要求: {task.get('requirements', '')}")
        
        # 之前的执行结果
        if previous_result:
            observation_parts.append(f"上一次执行状态: {previous_result.execution.status}")
            if previous_result.execution.error:
                observation_parts.append(f"上一次错误: {previous_result.execution.error}")
            observation_parts.append(f"上一次学习到的经验: {'; '.join(previous_result.learnings)}")
        
        return "\n".join(observation_parts)
    
    async def _understand(self, observation: str, task: Dict[str, Any], previous_result: Optional[MUSELoopResult]) -> str:
        """理解阶段：分析问题，识别关键障碍"""
        # 这里可以接入大模型进行深度分析
        understanding_parts = []
        
        understanding_parts.append("任务分析:")
        understanding_parts.append(f"- 目标明确度: {'明确' if task.get('description') else '不明确'}")
        understanding_parts.append(f"- 复杂度评估: {task.get('complexity', 'medium')}")
        
        if previous_result and previous_result.execution.status == ExecutionStatus.FAILED:
            understanding_parts.append("\n失败原因分析:")
            understanding_parts.append(f"- 错误类型: {self._classify_error(previous_result.execution.error)}")
            understanding_parts.append(f"- 是否可恢复: {'是' if self._is_recoverable(previous_result.execution.error) else '否'}")
        
        return "\n".join(understanding_parts)
    
    async def _strategize(self, understanding: str, task: Dict[str, Any], previous_result: Optional[MUSELoopResult]) -> str:
        """决策阶段：制定执行策略"""
        strategy_parts = []
        
        strategy_parts.append("执行策略:")
        strategy_parts.append(f"- 执行模型: {self.engine.config.get('preferred_model', 'default')}")
        strategy_parts.append(f"- 超时设置: {task.get('timeout', 30)}秒")
        
        if previous_result:
            strategy_parts.append("\n迭代优化:")
            strategy_parts.append("- 针对上一次失败调整执行参数")
            strategy_parts.append("- 增加错误重试机制")
        
        return "\n".join(strategy_parts)
    
    async def _execute(self, strategy: str, task: Dict[str, Any]) -> ExecutionResult:
        """执行阶段：实际执行任务"""
        task_id = str(uuid.uuid4())
        result = ExecutionResult(task_id=task_id, status=ExecutionStatus.RUNNING)
        
        try:
            # 注册到活动任务
            self.engine.active_tasks[task_id] = result
            
            # 实际执行逻辑（这里简化为调用执行器）
            exec_result = await self.engine._execute_task(task, strategy)
            
            result.status = ExecutionStatus.SUCCESS
            result.result = exec_result
            
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
            logger.error(f"任务执行失败: {str(e)}")
        finally:
            result.end_time = time.time()
            # 从活动任务移除，加入历史
            if task_id in self.engine.active_tasks:
                del self.engine.active_tasks[task_id]
            self.engine.execution_history.append(result)
            
            # 保留最近1000条执行记录
            if len(self.engine.execution_history) > 1000:
                self.engine.execution_history.pop(0)
        
        return result
    
    async def _reflect(self, result: MUSELoopResult) -> None:
        """反思阶段：总结经验教训"""
        if result.execution.status == ExecutionStatus.SUCCESS:
            result.learnings.append("任务执行成功，验证了当前策略的有效性")
            result.improvements.append("可以将当前策略添加到最佳实践库")
        else:
            result.learnings.append(f"任务执行失败，错误: {result.execution.error}")
            result.improvements.append(f"需要针对错误类型{self._classify_error(result.execution.error)}优化处理逻辑")
    
    async def _apply_improvements(self, result: MUSELoopResult) -> None:
        """应用改进措施"""
        for improvement in result.improvements:
            # 将改进措施加入自适应队列
            await self.engine.runtime_adaptation.add_adaptation_task({
                'type': 'improvement',
                'source': 'muse_loop',
                'description': improvement,
                'priority': 'medium'
            })
    
    def _classify_error(self, error: Optional[str]) -> str:
        """分类错误类型"""
        if not error:
            return "unknown"
        if "timeout" in error.lower() or "timed out" in error.lower():
            return "timeout"
        if "memory" in error.lower() or "oom" in error.lower():
            return "out_of_memory"
        if "api" in error.lower() or "key" in error.lower() or "authorization" in error.lower():
            return "api_error"
        if "network" in error.lower() or "connection" in error.lower():
            return "network_error"
        return "logic_error"
    
    def _is_recoverable(self, error: Optional[str]) -> bool:
        """判断错误是否可恢复"""
        error_type = self._classify_error(error)
        return error_type in ["timeout", "network_error", "api_error"]
    
    def get_loop_history(self, limit: int = 20) -> List[MUSELoopResult]:
        """获取MUSE循环历史"""
        return self.loop_history[-limit:]


class RuntimeAdaptation:
    """
    运行时自适应模块
    Runtime Adaptation Module
    
    实现系统在运行过程中的动态调整和优化
    """
    
    def __init__(self, engine: 'QingQiuEvolutionEngine'):
        self.engine = engine
        self.adaptation_queue: asyncio.Queue = asyncio.Queue()
        self.adaptation_history: List[Dict[str, Any]] = []
        self.adaptation_rules: List[Callable] = []
        self._worker_task: Optional[asyncio.Task] = None
        
    async def start(self) -> None:
        """启动自适应工作线程"""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._adaptation_worker())
            logger.info("运行时自适应模块已启动")
    
    async def stop(self) -> None:
        """停止自适应工作线程"""
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("运行时自适应模块已停止")
    
    async def add_adaptation_task(self, task: Dict[str, Any]) -> None:
        """添加自适应任务"""
        await self.adaptation_queue.put(task)
        logger.debug(f"已添加自适应任务: {task.get('description', '未命名')}")
    
    async def _adaptation_worker(self) -> None:
        """自适应工作线程"""
        while True:
            try:
                task = await self.adaptation_queue.get()
                try:
                    await self._process_adaptation_task(task)
                finally:
                    self.adaptation_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"自适应任务处理失败: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_adaptation_task(self, task: Dict[str, Any]) -> None:
        """处理单个自适应任务"""
        task_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"处理自适应任务 {task_id}: {task.get('description', '')}")
        
        try:
            task_type = task.get('type', '')
            
            if task_type == 'improvement':
                # 处理来自MUSE循环的改进建议
                await self._apply_improvement(task)
            elif task_type == 'configuration':
                # 配置调整
                await self._adjust_configuration(task)
            elif task_type == 'resource':
                # 资源调整
                await self._adjust_resources(task)
            elif task_type == 'strategy':
                # 策略优化
                await self._optimize_strategy(task)
            
            # 记录成功的自适应操作
            self.adaptation_history.append({
                'task_id': task_id,
                'task': task,
                'status': 'success',
                'duration': time.time() - start_time,
                'timestamp': time.time()
            })
            
            logger.info(f"自适应任务 {task_id} 处理完成")
            
        except Exception as e:
            # 记录失败的自适应操作
            self.adaptation_history.append({
                'task_id': task_id,
                'task': task,
                'status': 'failed',
                'error': str(e),
                'duration': time.time() - start_time,
                'timestamp': time.time()
            })
            logger.error(f"自适应任务 {task_id} 处理失败: {str(e)}")
    
    async def _apply_improvement(self, task: Dict[str, Any]) -> None:
        """应用改进建议"""
        description = task.get('description', '')
        # 这里可以实现具体的改进逻辑，例如：
        # - 更新策略库
        # - 调整模型参数
        # - 优化提示词
        logger.debug(f"应用改进建议: {description}")
    
    async def _adjust_configuration(self, task: Dict[str, Any]) -> None:
        """调整系统配置"""
        config_updates = task.get('updates', {})
        self.engine.config.update(config_updates)
        logger.info(f"已更新系统配置: {list(config_updates.keys())}")
    
    async def _adjust_resources(self, task: Dict[str, Any]) -> None:
        """调整资源分配"""
        resource_type = task.get('resource_type', '')
        new_limit = task.get('new_limit', 0)
        
        if resource_type == 'memory':
            self.engine.config['max_memory_mb'] = new_limit
            logger.info(f"已调整内存上限为: {new_limit}MB")
        elif resource_type == 'tasks':
            self.engine.config['max_active_tasks'] = new_limit
            logger.info(f"已调整最大活动任务数为: {new_limit}")
    
    async def _optimize_strategy(self, task: Dict[str, Any]) -> None:
        """优化执行策略"""
        strategy_name = task.get('strategy_name', '')
        new_params = task.get('parameters', {})
        # 这里可以实现策略优化逻辑
        logger.info(f"已优化策略 {strategy_name}: {new_params}")
    
    def add_adaptation_rule(self, rule: Callable) -> None:
        """添加自适应规则"""
        self.adaptation_rules.append(rule)
        logger.info(f"已添加自适应规则: {rule.__name__}")
    
    async def run_rules(self, context: Dict[str, Any]) -> None:
        """运行所有自适应规则"""
        for rule in self.adaptation_rules:
            try:
                await rule(self.engine, context)
            except Exception as e:
                logger.error(f"自适应规则执行失败 {rule.__name__}: {str(e)}")
    
    def get_adaptation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取自适应历史记录"""
        return self.adaptation_history[-limit:]


class QingQiuEvolutionEngine:
    """
    青丘v4.0进化引擎主类
    QingQiu Evolution Engine v4.0 Main Class
    
    整合三大核心模块，提供完整的进化能力
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.start_time = time.time()
        self.instance_id = str(uuid.uuid4())
        
        # 核心模块
        self.self_introspection = SelfIntrospection(self)
        self.muse_loop = MUSELoop(self)
        self.runtime_adaptation = RuntimeAdaptation(self)
        
        # 状态管理
        self.active_tasks: Dict[str, ExecutionResult] = {}
        self.execution_history: List[ExecutionResult] = []
        self.muse_history: List[MUSELoopResult] = []
        
        # 回调函数
        self.on_task_completed: Optional[Callable[[ExecutionResult], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        
        logger.info(f"青丘v4.0进化引擎实例 {self.instance_id} 已创建")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'max_active_tasks': 100,
            'max_memory_mb': 2048,
            'preferred_model': 'default',
            'max_muse_iterations': 3,
            'auto_introspection_interval': 60,  # 自动自省间隔（秒）
            'enable_auto_adaptation': True,
            'log_level': 'INFO'
        }
    
    async def start(self) -> None:
        """启动引擎"""
        logger.info("启动青丘v4.0进化引擎...")
        
        # 启动自适应模块
        if self.config.get('enable_auto_adaptation', True):
            await self.runtime_adaptation.start()
        
        # 启动自动自省任务
        if self.config.get('auto_introspection_interval', 0) > 0:
            asyncio.create_task(self._auto_introspection_loop())
        
        logger.info("青丘v4.0进化引擎已启动，准备接受任务")
    
    async def stop(self) -> None:
        """停止引擎"""
        logger.info("停止青丘v4.0进化引擎...")
        
        # 停止自适应模块
        await self.runtime_adaptation.stop()
        
        # 取消所有活动任务
        for task_id, task in self.active_tasks.items():
            task.status = ExecutionStatus.CANCELLED
            task.end_time = time.time()
        
        logger.info("青丘v4.0进化引擎已停止")
    
    async def _auto_introspection_loop(self) -> None:
        """自动自省循环"""
        interval = self.config.get('auto_introspection_interval', 60)
        logger.info(f"启动自动自省循环，间隔{interval}秒")
        
        while True:
            try:
                # 执行常规自省
                result = await self.self_introspection.introspect(IntrospectionLevel.NORMAL)
                
                # 如果有问题，触发自适应
                if result.issues and self.config.get('enable_auto_adaptation', True):
                    for issue in result.issues:
                        await self.runtime_adaptation.add_adaptation_task({
                            'type': 'improvement',
                            'source': 'auto_introspection',
                            'description': issue['suggestion'],
                            'priority': issue['severity'],
                            'issue': issue
                        })
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"自动自省失败: {str(e)}")
                await asyncio.sleep(interval)
    
    async def execute_task(self, task: Dict[str, Any]) -> ExecutionResult:
        """
        执行任务的对外接口
        :param task: 任务字典，包含description、requirements等字段
        """
        logger.info(f"接收新任务: {task.get('description', '未命名任务')}")
        
        # 使用MUSE循环执行任务
        muse_result = await self.muse_loop.run(task)
        
        # 保存MUSE历史
        self.muse_history.append(muse_result)
        if len(self.muse_history) > 1000:
            self.muse_history.pop(0)
        
        # 触发回调
        if self.on_task_completed:
            try:
                self.on_task_completed(muse_result.execution)
            except Exception as e:
                logger.error(f"任务完成回调执行失败: {str(e)}")
        
        return muse_result.execution
    
    async def _execute_task(self, task: Dict[str, Any], strategy: str) -> Any:
        """
        实际执行任务的内部方法
        这里可以根据需要接入具体的执行逻辑，例如调用大模型、执行代码等
        """
        # 示例实现：模拟任务执行
        task_type = task.get('type', 'default')
        duration = task.get('simulate_duration', 1.0)
        
        await asyncio.sleep(duration)
        
        # 返回模拟结果
        return {
            'task_type': task_type,
            'strategy_applied': strategy,
            'completed_at': datetime.now().isoformat(),
            'status': 'success'
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """获取引擎当前状态"""
        uptime = time.time() - self.start_time
        
        # 计算成功率
        success_count = sum(
            1 for r in self.execution_history 
            if r.status == ExecutionStatus.SUCCESS
        )
        total_count = len(self.execution_history)
        success_rate = success_count / total_count if total_count > 0 else 0.0
        
        return {
            'instance_id': self.instance_id,
            'start_time': self.start_time,
            'uptime': uptime,
            'uptime_formatted': str(datetime.utcfromtimestamp(uptime).strftime('%H:%M:%S')),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': total_count,
            'success_rate': f"{success_rate:.1%}",
            'introspection_history_count': len(self.self_introspection.introspection_history),
            'muse_loop_count': len(self.muse_history),
            'adaptation_queue_size': self.runtime_adaptation.adaptation_queue.qsize(),
            'config': self.config
        }
    
    async def save_state(self, path: str) -> None:
        """保存引擎状态到文件"""
        state = {
            'instance_id': self.instance_id,
            'start_time': self.start_time,
            'config': self.config,
            'execution_history': [
                {
                    'task_id': r.task_id,
                    'status': r.status.value,
                    'result': r.result,
                    'error': r.error,
                    'start_time': r.start_time,
                    'end_time': r.end_time,
                    'metadata': r.metadata
                } for r in self.execution_history[-100:]  # 只保存最近100条
            ],
            'adaptation_history': self.runtime_adaptation.get_adaptation_history(100),
            'timestamp': time.time()
        }
        
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        logger.info(f"引擎状态已保存到: {file_path}")
    
    async def load_state(self, path: str) -> None:
        """从文件加载引擎状态"""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"状态文件不存在: {path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        self.instance_id = state.get('instance_id', self.instance_id)
        self.start_time = state.get('start_time', self.start_time)
        self.config.update(state.get('config', {}))
        
        # 恢复执行历史
        self.execution_history = []
        for r in state.get('execution_history', []):
            self.execution_history.append(ExecutionResult(
                task_id=r['task_id'],
                status=ExecutionStatus(r['status']),
                result=r['result'],
                error=r['error'],
                start_time=r['start_time'],
                end_time=r['end_time'],
                metadata=r['metadata']
            ))
        
        logger.info(f"引擎状态已从 {file_path} 加载")
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """注册回调函数"""
        if event == 'task_completed':
            self.on_task_completed = callback
        elif event == 'error':
            self.on_error = callback
        else:
            raise ValueError(f"不支持的事件类型: {event}")


# 单元测试示例
async def test_engine():
    """测试引擎基本功能"""
    print("=" * 80)
    print("青丘v4.0进化引擎单元测试")
    print("=" * 80)
    
    # 创建引擎实例
    config = {
        'max_active_tasks': 50,
        'auto_introspection_interval': 10,
        'enable_auto_adaptation': True
    }
    
    engine = QingQiuEvolutionEngine(config)
    
    try:
        # 启动引擎
        await engine.start()
        
        # 获取引擎状态
        status = await engine.get_status()
        print("\n引擎初始状态:")
        print(f"  实例ID: {status['instance_id']}")
        print(f"  运行时间: {status['uptime_formatted']}")
        print(f"  配置: {status['config']}")
        
        # 测试自省功能
        print("\n测试自省功能...")
        introspection_result = await engine.self_introspection.introspect(IntrospectionLevel.DEEP)
        print(f"  自省状态: {introspection_result.status}")
        print(f"  发现问题: {len(introspection_result.issues)}个")
        print(f"  性能指标: {introspection_result.metrics}")
        
        # 测试任务执行
        print("\n测试任务执行...")
        task = {
            'description': '测试任务',
            'type': 'test',
            'simulate_duration': 0.5,
            'requirements': '完成测试任务，返回成功结果'
        }
        
        result = await engine.execute_task(task)
        print(f"  任务ID: {result.task_id}")
        print(f"  执行状态: {result.status}")
        print(f"  执行结果: {result.result}")
        print(f"  执行耗时: {result.duration:.3f