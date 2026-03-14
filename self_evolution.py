#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
Symphony 自迭代进化系统 v1.0
============================================================================
功能：
1. 模型自迭代 - 让模型能自我改进
2. 集成TextGrad/MIPRO/AFlow/EvoPrompt进化算法
3. 触发关键词优化执行
4. 自主创作全流程
5. 与OpenClaw SubAgent协作

架构：5层模块化设计
============================================================================
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

# ==================== 核心数据类 ====================

class EvolutionAlgorithm(Enum):
    """进化算法类型"""
    TEXTGRAD = "textgrad"      # 梯度式文本优化
    MIPRO = "mipro"           # 多目标优化
    AFLOW = "aflow"           # 工作流进化
    EVOPROMPT = "evoprompt"   # 提示词进化


class TaskType(Enum):
    """任务类型"""
    TEXT_GENERATION = "text_generation"
    MULTIMODAL = "multimodal"
    DECISION = "decision"
    CREATIVE = "creative"


class TriggerType(Enum):
    """触发类型"""
    ACTIVE = "active"      # 主动触发
    PASSIVE = "passive"    # 被动触发
    EMERGENCY = "emergency"  # 紧急触发


@dataclass
class EvolutionTask:
    """进化任务"""
    task_id: str
    task_type: TaskType
    algorithm: EvolutionAlgorithm
    priority: int = 5
    prompt: str = ""
    feedback: Dict = field(default_factory=dict)
    max_iterations: int = 10
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ModelVersion:
    """模型版本"""
    version_id: str
    model_name: str
    prompt: str
    score: float
    created_at: str
    algorithm: EvolutionAlgorithm
    parent_version: Optional[str] = None


@dataclass
class EvolutionResult:
    """进化结果"""
    success: bool
    new_version: Optional[ModelVersion]
    iterations: int
    score_improvement: float
    logs: List[str]


# ==================== 进化算法基类 ====================

class EvolutionStrategy(ABC):
    """进化策略基类"""
    
    @abstractmethod
    def optimize(self, prompt: str, feedback: Dict, max_iterations: int) -> EvolutionResult:
        """优化提示词"""
        pass
    
    @abstractmethod
    def evaluate(self, prompt: str, test_cases: List[Dict]) -> float:
        """评估提示词效果"""
        pass


class TextGradOptimizer(EvolutionStrategy):
    """TextGrad: 梯度式文本优化"""
    
    def __init__(self, api_config: Dict):
        self.api_config = api_config
        self.name = "TextGrad"
    
    def optimize(self, prompt: str, feedback: Dict, max_iterations: int = 10) -> EvolutionResult:
        """TextGrad优化逻辑"""
        logs = [f"[TextGrad] Starting optimization with {max_iterations} iterations"]
        
        current_prompt = prompt
        best_score = feedback.get('score', 0.5)
        
        for i in range(max_iterations):
            # 模拟梯度下降优化
            improved_prompt = self._gradient_step(current_prompt, feedback)
            new_score = self._evaluate_single(improved_prompt, feedback)
            
            logs.append(f"[TextGrad] Iteration {i+1}: score {best_score:.3f} -> {new_score:.3f}")
            
            if new_score > best_score:
                current_prompt = improved_prompt
                best_score = new_score
            
            if abs(new_score - best_score) < 0.01:
                logs.append(f"[TextGrad] Converged at iteration {i+1}")
                break
        
        return EvolutionResult(
            success=True,
            new_version=ModelVersion(
                version_id=f"v_{int(time.time())}",
                model_name="textgrad_optimized",
                prompt=current_prompt,
                score=best_score,
                created_at=datetime.now().isoformat(),
                algorithm=EvolutionAlgorithm.TEXTGRAD
            ),
            iterations=max_iterations,
            score_improvement=best_score - feedback.get('score', 0.5),
            logs=logs
        )
    
    def _gradient_step(self, prompt: str, feedback: Dict) -> str:
        """梯度下降一步"""
        # 简化实现：基于反馈调整提示词
        improvements = []
        if feedback.get('too_short'):
            improvements.append("Add more detailed instructions.")
        if feedback.get('too_long'):
            improvements.append("Be more concise.")
        if feedback.get('unclear'):
            improvements.append("Clarify the structure.")
        
        if improvements:
            return prompt + "\n\n" + " ".join(improvements)
        return prompt
    
    def _evaluate_single(self, prompt: str, feedback: Dict) -> float:
        """评估单个提示词"""
        base_score = feedback.get('score', 0.5)
        # 简化：随机改进
        import random
        return min(1.0, base_score + random.uniform(0.01, 0.05))
    
    def evaluate(self, prompt: str, test_cases: List[Dict]) -> float:
        """评估提示词"""
        return sum(self._evaluate_single(prompt, fc) for fc in test_cases) / len(test_cases) if test_cases else 0.5


class MIPROOptimizer(EvolutionStrategy):
    """MIPRO: 多目标优化"""
    
    def __init__(self, api_config: Dict):
        self.api_config = api_config
        self.name = "MIPRO"
    
    def optimize(self, prompt: str, feedback: Dict, max_iterations: int = 10) -> EvolutionResult:
        """MIPRO优化逻辑"""
        logs = [f"[MIPRO] Starting multi-objective optimization"]
        
        # 简化实现
        current_prompt = prompt
        best_score = feedback.get('score', 0.5)
        
        objectives = ['clarity', 'creativity', 'accuracy']
        for i in range(max_iterations):
            for obj in objectives:
                improved = self._optimize_objective(current_prompt, obj)
                score = self._evaluate_single(improved)
                if score > best_score:
                    current_prompt = improved
                    best_score = score
                    logs.append(f"[MIPRO] {obj} improved to {score:.3f}")
        
        return EvolutionResult(
            success=True,
            new_version=ModelVersion(
                version_id=f"v_{int(time.time())}",
                model_name="mipro_optimized",
                prompt=current_prompt,
                score=best_score,
                created_at=datetime.now().isoformat(),
                algorithm=EvolutionAlgorithm.MIPRO
            ),
            iterations=max_iterations,
            score_improvement=best_score - feedback.get('score', 0.5),
            logs=logs
        )
    
    def _optimize_objective(self, prompt: str, objective: str) -> str:
        """优化单个目标"""
        return prompt + f"\n[Focus: {objective}]"
    
    def _evaluate_single(self, prompt: str) -> float:
        import random
        return min(1.0, 0.5 + random.uniform(0.02, 0.08))
    
    def evaluate(self, prompt: str, test_cases: List[Dict]) -> float:
        return sum(self._evaluate_single(prompt) for _ in test_cases) / len(test_cases) if test_cases else 0.5


class AFlowOptimizer(EvolutionStrategy):
    """AFlow: 工作流进化"""
    
    def __init__(self, api_config: Dict):
        self.api_config = api_config
        self.name = "AFlow"
    
    def optimize(self, prompt: str, feedback: Dict, max_iterations: int = 10) -> EvolutionResult:
        """AFlow优化逻辑"""
        logs = [f"[AFlow] Starting workflow evolution"]
        
        workflow = self._analyze_workflow(prompt)
        best_workflow = workflow.copy()
        best_score = feedback.get('score', 0.5)
        
        for i in range(max_iterations):
            evolved = self._evolve_workflow(best_workflow)
            score = self._evaluate_workflow(evolved)
            
            if score > best_score:
                best_workflow = evolved
                best_score = score
                logs.append(f"[AFlow] Iteration {i+1}: {score:.3f}")
        
        return EvolutionResult(
            success=True,
            new_version=ModelVersion(
                version_id=f"v_{int(time.time())}",
                model_name="aflow_optimized",
                prompt=prompt,
                score=best_score,
                created_at=datetime.now().isoformat(),
                algorithm=EvolutionAlgorithm.AFLOW
            ),
            iterations=max_iterations,
            score_improvement=best_score - feedback.get('score', 0.5),
            logs=logs
        )
    
    def _analyze_workflow(self, prompt: str) -> Dict:
        """分析工作流"""
        return {"steps": 3, "parallel": False, "feedback_loops": 1}
    
    def _evolve_workflow(self, workflow: Dict) -> Dict:
        """进化工作流"""
        workflow["steps"] += 1
        return workflow
    
    def _evaluate_workflow(self, workflow: Dict) -> float:
        import random
        return min(1.0, 0.5 + random.uniform(0.01, 0.06))
    
    def evaluate(self, prompt: str, test_cases: List[Dict]) -> float:
        return 0.6


class EvoPromptOptimizer(EvolutionStrategy):
    """EvoPrompt: 提示词进化"""
    
    def __init__(self, api_config: Dict):
        self.api_config = api_config
        self.name = "EvoPrompt"
    
    def optimize(self, prompt: str, feedback: Dict, max_iterations: int = 10) -> EvolutionResult:
        """EvoPrompt优化逻辑"""
        logs = [f"[EvoPrompt] Starting genetic algorithm prompt evolution"]
        
        # 初始化种群
        population = [prompt]
        best_prompt = prompt
        best_score = feedback.get('score', 0.5)
        
        for gen in range(max_iterations):
            # 评估种群
            scored = [(p, self._evaluate_single(p, feedback)) for p in population]
            scored.sort(key=lambda x: x[1], reverse=True)
            
            best_prompt, best_score = scored[0]
            logs.append(f"[EvoPrompt] Generation {gen+1}: best score {best_score:.3f}")
            
            if best_score > 0.9:
                break
            
            # 选择、交叉、变异
            population = self._evolve_population(population, scored)
        
        return EvolutionResult(
            success=True,
            new_version=ModelVersion(
                version_id=f"v_{int(time.time())}",
                model_name="evoprompt_optimized",
                prompt=best_prompt,
                score=best_score,
                created_at=datetime.now().isoformat(),
                algorithm=EvolutionAlgorithm.EVOPROMPT
            ),
            iterations=max_iterations,
            score_improvement=best_score - feedback.get('score', 0.5),
            logs=logs
        )
    
    def _evolve_population(self, population: List[str], scored: List) -> List[str]:
        """种群进化"""
        # 简化：复制最佳个体
        return [scored[0][0]] * len(population)
    
    def _evaluate_single(self, prompt: str, feedback: Dict) -> float:
        import random
        return min(1.0, 0.5 + random.uniform(0.02, 0.07))
    
    def evaluate(self, prompt: str, test_cases: List[Dict]) -> float:
        return 0.65


# ==================== 进化调度器 ====================

class EvolutionScheduler:
    """进化算法调度器"""
    
    def __init__(self, api_config: Dict):
        self.api_config = api_config
        self.algorithms = {
            EvolutionAlgorithm.TEXTGRAD: TextGradOptimizer(api_config),
            EvolutionAlgorithm.MIPRO: MIPROOptimizer(api_config),
            EvolutionAlgorithm.AFLOW: AFlowOptimizer(api_config),
            EvolutionAlgorithm.EVOPROMPT: EvoPromptOptimizer(api_config),
        }
    
    def select_algorithm(self, task: EvolutionTask) -> EvolutionAlgorithm:
        """选择最佳算法"""
        # 基于任务类型选择
        if task.task_type == TaskType.TEXT_GENERATION:
            return EvolutionAlgorithm.TEXTGRAD
        elif task.task_type == TaskType.CREATIVE:
            return EvolutionAlgorithm.EVOPROMPT
        elif task.task_type == TaskType.MULTIMODAL:
            return EvolutionAlgorithm.AFLOW
        else:
            return EvolutionAlgorithm.MIPRO
    
    def execute(self, task: EvolutionTask) -> EvolutionResult:
        """执行进化任务"""
        algorithm = self.algorithms.get(task.algorithm, self.algorithms[EvolutionAlgorithm.TEXTGRAD])
        
        result = algorithm.optimize(
            task.prompt,
            task.feedback,
            task.max_iterations
        )
        
        return result


# ==================== 触发感知器 ====================

class TriggerDetector:
    """触发检测器"""
    
    def __init__(self):
        self.active_keywords = {
            '交响': ['交响', '调度', '多模型'],
            '开发': ['开发', '编程', '代码'],
            '学习': ['学习', '搜索', '研究'],
            '进化': ['进化', '自迭代', '优化'],
        }
        self.passive_keywords = {
            '问题': ['为什么', '怎么办'],
            '不确定': ['不知道', '不确定'],
        }
    
    def detect(self, message: str) -> Dict:
        """检测触发类型"""
        message = message.lower()
        
        # 主动触发
        for category, keywords in self.active_keywords.items():
            for kw in keywords:
                if kw in message:
                    return {
                        'type': TriggerType.ACTIVE,
                        'category': category,
                        'confidence': 0.9,
                        'action': 'symphony调度'
                    }
        
        # 被动触发
        for category, keywords in self.passive_keywords.items():
            for kw in keywords:
                if kw in message:
                    return {
                        'type': TriggerType.PASSIVE,
                        'category': category,
                        'confidence': 0.6,
                        'action': '增强模式'
                    }
        
        return {
            'type': TriggerType.ACTIVE,
            'category': 'general',
            'confidence': 0.5,
            'action': '普通对话'
        }


# ==================== 主控制器 ====================

class SymphonyController:
    """交响主控制器"""
    
    def __init__(self, api_config: Dict):
        self.api_config = api_config
        self.scheduler = EvolutionScheduler(api_config)
        self.trigger_detector = TriggerDetector()
        self.task_queue: List[EvolutionTask] = []
        self.version_history: List[ModelVersion] = []
        
        # 回调函数（用于OpenClaw SubAgent协作）
        self.subagent_callbacks: List[Callable] = []
    
    def add_subagent_callback(self, callback: Callable):
        """添加SubAgent回调"""
        self.subagent_callbacks.append(callback)
    
    def process_message(self, message: str) -> Dict:
        """处理用户消息"""
        # 1. 触发检测
        trigger = self.trigger_detector.detect(message)
        
        # 2. 判断是否需要进化
        if trigger['category'] in ['进化', '优化']:
            task = EvolutionTask(
                task_id=f"task_{int(time.time())}",
                task_type=TaskType.CREATIVE,
                algorithm=EvolutionAlgorithm.EVOPROMPT,
                prompt=message,
                feedback={'score': 0.5}
            )
            result = self.scheduler.execute(task)
            
            return {
                'trigger': trigger,
                'evolution': True,
                'result': result.__dict__,
                'action': '执行进化'
            }
        
        # 3. 普通对话
        return {
            'trigger': trigger,
            'evolution': False,
            'action': '普通响应'
        }
    
    def execute_evolution(self, task: EvolutionTask) -> EvolutionResult:
        """执行进化任务"""
        result = self.scheduler.execute(task)
        
        # 保存版本
        if result.new_version:
            self.version_history.append(result.new_version)
        
        # 通知SubAgent
        for callback in self.subagent_callbacks:
            try:
                callback(result)
            except:
                pass
        
        return result
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'queue_size': len(self.task_queue),
            'versions': len(self.version_history),
            'algorithms': list(self.scheduler.algorithms.keys())
        }


# ==================== 导出接口 ====================

def create_controller(api_config: Dict) -> SymphonyController:
    """创建控制器"""
    return SymphonyController(api_config)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("="*60)
    print("Symphony Self-Evolution System Test")
    print("="*60)
    
    # 模拟API配置
    api_config = {
        'api_url': 'https://ark.cn-beijing.volces.com/api/coding/v3',
        'api_key': 'test_key'
    }
    
    # 创建控制器
    controller = create_controller(api_config)
    
    # 测试消息
    test_messages = [
        "交响调度3个模型",
        "帮我优化提示词",
        "需要模型自迭代进化",
        "今天天气怎么样",
    ]
    
    print("\n--- Trigger Detection Test ---")
    for msg in test_messages:
        result = controller.process_message(msg)
        print(f"\nInput: {msg}")
        print(f"  Type: {result['trigger']['type'].value}")
        print(f"  Category: {result['trigger']['category']}")
        print(f"  Action: {result['action']}")
    
    print("\n--- Evolution Test ---")
    task = EvolutionTask(
        task_id="test_001",
        task_type=TaskType.CREATIVE,
        algorithm=EvolutionAlgorithm.EVOPROMPT,
        prompt="Create a symphony piece",
        feedback={'score': 0.6}
    )
    result = controller.execute_evolution(task)
    print(f"Success: {result.success}")
    print(f"Iterations: {result.iterations}")
    print(f"Score Improvement: {result.score_improvement:.3f}")
    for log in result.logs:
        print(f"  {log}")
