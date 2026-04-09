# -*- coding: utf-8 -*-
"""
adaptive_algorithm_coordinator.py - 自适应算法协调器
======================================================
负责协调多种群体智能算法，包括蚁群、粒子群、蜂群等，
根据任务特性自适应选择最优算法组合
"""
from typing import Dict, List, Any, Optional
from enum import Enum
from loguru import logger

class AlgorithmCategory(Enum):
    """算法类型枚举"""
    ANT_COLONY = "ant_colony"
    PARTICLE_SWARM = "particle_swarm"
    BEE_COLONY = "bee_colony"
    GENETIC = "genetic_algorithm"
    SIMULATED_ANNEALING = "simulated_annealing"
    HILL_CLIMBING = "hill_climbing"

class AdaptiveAlgorithmCoordinator:
    """自适应算法协调器"""
    
    # 支持的算法类型
    ALGORITHMS = [
        "ant_colony",       # 蚁群算法
        "particle_swarm",   # 粒子群优化
        "bee_colony",       # 蜂群算法
        "genetic_algorithm", # 遗传算法
        "simulated_annealing", # 模拟退火
        "hill_climbing"     # 爬山法
    ]
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.algorithms = {}
        self.performance_history = {}
        self.current_best = None
        logger.info("自适应算法协调器初始化完成")
    
    def register_algorithm(self, name: str, algorithm_instance):
        """注册算法实例"""
        if name not in self.ALGORITHMS:
            logger.warning(f"注册未知算法: {name}")
        self.algorithms[name] = algorithm_instance
        self.performance_history[name] = []
        logger.debug(f"注册算法: {name}")
    
    def select_algorithm(self, task: Dict) -> str:
        """根据任务特性选择最适合的算法"""
        task_type = task.get("type", "optimization")
        dimensions = task.get("dimensions", 10)
        
        # 简单自适应选择逻辑
        if task_type == "path_planning":
            selected = "ant_colony"
        elif dimensions > 100:
            selected = "particle_swarm"
        elif task_type == "combinatorial":
            selected = "bee_colony"
        else:
            # 根据历史性能选择
            selected = self._select_by_history()
        
        logger.info(f"选择算法: {selected} 用于任务类型: {task_type}")
        return selected
    
    def _select_by_history(self) -> str:
        """根据历史性能选择算法"""
        if not self.performance_history:
            return self.ALGORITHMS[0]
        
        best_avg = -1
        best_alg = self.ALGORITHMS[0]
        for name, history in self.performance_history.items():
            if not history:
                continue
            avg = sum(history) / len(history)
            if avg > best_avg:
                best_avg = avg
                best_alg = name
        
        return best_alg
    
    def run_optimization(self, task: Dict, max_iterations: int = 100) -> Dict:
        """运行优化任务"""
        alg_name = self.select_algorithm(task)
        if alg_name not in self.algorithms:
            logger.error(f"算法未注册: {alg_name}")
            return {
                "success": False,
                "error": f"算法未注册: {alg_name}"
            }
        
        algorithm = self.algorithms[alg_name]
        start_time = time.time()
        
        result = algorithm.optimize(task, max_iterations)
        elapsed = time.time() - start_time
        
        # 记录性能
        if "fitness" in result:
            self.performance_history[alg_name].append(result["fitness"])
        
        return {
            "success": True,
            "algorithm": alg_name,
            "result": result,
            "elapsed": elapsed,
            "iterations": max_iterations
        }
    
    def get_performance_summary(self) -> Dict:
        """获取算法性能汇总"""
        summary = {}
        for name, history in self.performance_history.items():
            if history:
                summary[name] = {
                    "count": len(history),
                    "avg_fitness": sum(history) / len(history),
                    "best_fitness": max(history) if history else 0
                }
        return summary
    
    def execute(self, task: str, options: Optional[Dict] = None) -> Dict:
        """标准执行接口"""
        options = options or {}
        
        if task == "full_check":
            return {
                "success": True,
                "algorithms_registered": len(self.algorithms),
                "summary": self.get_performance_summary()
            }
        
        return {
            "success": True,
            "task": task,
            "options": options
        }

# 对外接口
__all__ = ['AdaptiveAlgorithmCoordinator']
