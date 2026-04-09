# -*- coding: utf-8 -*-
"""
dual_engine_scheduler - 蜂蚁双引擎调度器
===========================================
功能：
  1. 蚁群算法（ACO）路由 - AntColonyOptimizerV2 驱动，节点注册、任务分配
  2. 蜂群算法（BCO）分配 - BeeColonySystem 驱动，任务提交、协作执行
实际使用 Kernel/swarm_intelligence.py 中的蚁群、蜂群算法实现
"""
import sys
import os

# 确保项目根目录在 sys.path 中，以便正确导入所有子模块
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 同时确保 algorithm 目录可导入
algorithm_dir = os.path.join(project_root, 'algorithm')
if algorithm_dir not in sys.path:
    sys.path.insert(0, algorithm_dir)

# ACO 模块（AntColonyOptimizerV2）
AntColonyOptimizerV2 = None
try:
    from algorithm.ant_colony_optimized import AntColonyOptimizerV2
except ImportError:
    pass

# BCO 模块（BeeColonySystem）
BeeColonySystem = None
try:
    from algorithm.bee_colony import BeeColonySystem
except ImportError:
    pass


class DualEngineConfig:
    """蜂蚁双引擎配置"""

    def __init__(
        self,
        enable_aco: bool = True,
        enable_bco: bool = True,
        enable_heterogeneity: bool = True,
        # ACO 参数
        aco_ants: int = 10,
        aco_iterations: int = 50,
        aco_evaporation: float = 0.5,
        # BCO 参数
        bco_scouts: int = 5,
        bco_workers: int = 20,
        bco_iterations: int = 30,
    ):
        self.enable_aco = enable_aco
        self.enable_bco = enable_bco
        self.enable_heterogeneity = enable_heterogeneity
        # ACO 配置
        self.aco_ants = aco_ants
        self.aco_iterations = aco_iterations
        self.aco_evaporation = aco_evaporation
        # BCO 配置（映射到 BeeColonySystem 参数名）
        self.bco_scouts = bco_scouts
        self.bco_workers = bco_workers
        self.bco_iterations = bco_iterations


class DualEngineScheduler:
    """
    蜂蚁双引擎调度器

    - 蚁群算法（ACO）：通过 AntColonyOptimizerV2 实现
      适合离散任务分配、最优路径选择
    - 蜂群算法（BCO）：通过 BeeColonySystem 实现
      适合资源发现、动态负载均衡、多目标优化
    """

    def __init__(self, config: DualEngineConfig = None):
        self.config = config or DualEngineConfig()
        self.aco_optimizer = None
        self.bco_optimizer = None
        self._init_aco()
        self._init_bco()

    def _init_aco(self) -> None:
        """初始化蚁群优化器"""
        if not self.config.enable_aco:
            return
        if AntColonyOptimizerV2 is None:
            return
        try:
            self.aco_optimizer = AntColonyOptimizerV2()
        except Exception:
            pass

    def _init_bco(self) -> None:
        """初始化蜂群优化器"""
        if not self.config.enable_bco:
            return
        if BeeColonySystem is None:
            return
        try:
            # BeeColonySystem 参数名：scout_count, worker_count
            self.bco_optimizer = BeeColonySystem(
                scout_count=self.config.bco_scouts,
                worker_count=self.config.bco_workers,
            )
        except Exception:
            pass

    def route_aco(self, tasks: list, providers: list) -> dict:
        """
        使用蚁群算法路由任务

        Args:
            tasks: 任务列表，每个任务需包含 id/cost/complexity
            providers: 可用服务商列表，每个需包含 id/capacity/load

        Returns:
            dict: 路由结果 {provider_id: [dispatch_result]}
        """
        if not self.aco_optimizer:
            return {}

        try:
            # 为ACO 注册节点（每个 provider 一个节点）
            node_map = {}  # provider_id -> node_id
            for p in providers:
                node_id = self.aco_optimizer.add_node(capacity=float(p.get('capacity', 1.0)))
                node_map[p['id']] = node_id

            # 分发每个任务
            result_map = {}
            for task in tasks:
                task_id = task.get('id', f"task_{id(task)}")
                task_cost = float(task.get('cost', 1.0))
                node_id, dispatch_info = self.aco_optimizer.dispatch_task(task_id, task_cost)
                result_map[task_id] = dispatch_info

            return result_map

        except Exception:
            return {}

    def allocate_bco(self, tasks: list, resources: list) -> dict:
        """
        使用蜂群算法分配资源

        Args:
            tasks: 任务列表，需包含 task_id �?cost
            resources: 可用资源列表

        Returns:
            dict: 分配结果
        """
        if not self.bco_optimizer:
            return {}

        try:
            # 标准化任务格式（BCO 需要 task_id 和 cost）            normalized_tasks = []
            for t in tasks:
                task_id = t.get('id', t.get('task_id', f"task_{id(t)}"))
                normalized_tasks.append({
                    'task_id': task_id,
                    'cost': float(t.get('cost', 1.0)),
                    'priority': t.get('priority', 0),
                })

            if not normalized_tasks:
                return {}

            result = self.bco_optimizer.submit_tasks(normalized_tasks)
            return result if isinstance(result, dict) else {}

        except Exception:
            return {}

    def get_status(self) -> dict:
        """
        获取引擎状态
        Returns:
            dict: 包含 aco_enabled, bco_enabled, heterogeneity_enabled,
                  aco_ready, bco_ready
        """
        return {
            "aco_enabled": self.config.enable_aco and AntColonyOptimizerV2 is not None,
            "bco_enabled": self.config.enable_bco and BeeColonySystem is not None,
            "heterogeneity_enabled": self.config.enable_heterogeneity,
            "aco_ready": self.aco_optimizer is not None,
            "bco_ready": self.bco_optimizer is not None,
        }

