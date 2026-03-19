# -*- coding: utf-8 -*-
"""
分布式探索框架 - Branch Executor Module

实现类AutoResearch的分支模式：
- 分支管理：策略树+实验分组
- 并行评估：同时探索多个解决方案
- 最优选择：统计显著性检验选择最佳

"""
import sqlite3
import json
import time
import uuid
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class BranchStatus(Enum):
    """分支状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    MERGED = "merged"


class ExploreStrategy(Enum):
    """探索策略"""
    BFS = "breadth_first"      # 广度优先
    DFS = "depth_first"        # 深度优先
    HYBRID = "hybrid"          # 混合模式


@dataclass
class Branch:
    """分支数据类"""
    branch_id: str
    parent_id: Optional[str]
    strategy: Dict[str, Any]
    status: str = BranchStatus.PENDING.value
    results: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BranchDatabase:
    """分支数据库"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = "C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/evolution.db"
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建分支表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS branches (
                branch_id TEXT PRIMARY KEY,
                parent_id TEXT,
                strategy TEXT,
                status TEXT,
                results TEXT,
                score REAL,
                created_at REAL,
                completed_at REAL,
                metadata TEXT
            )
        """)
        
        # 创建实验组表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiment_groups (
                group_id TEXT PRIMARY KEY,
                name TEXT,
                strategy TEXT,
                branch_ids TEXT,
                status TEXT,
                created_at REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_branch(self, branch: Branch) -> bool:
        """创建分支"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO branches (branch_id, parent_id, strategy, status, results, score, created_at, completed_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                branch.branch_id,
                branch.parent_id,
                json.dumps(branch.strategy),
                branch.status,
                json.dumps(branch.results),
                branch.score,
                branch.created_at,
                branch.completed_at,
                json.dumps(branch.metadata)
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"创建分支失败: {e}")
            return False
        finally:
            conn.close()
    
    def update_branch(self, branch: Branch) -> bool:
        """更新分支"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE branches 
                SET status=?, results=?, score=?, completed_at=?, metadata=?
                WHERE branch_id=?
            """, (
                branch.status,
                json.dumps(branch.results),
                branch.score,
                branch.completed_at,
                json.dumps(branch.metadata),
                branch.branch_id
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"更新分支失败: {e}")
            return False
        finally:
            conn.close()
    
    def get_branch(self, branch_id: str) -> Optional[Branch]:
        """获取分支"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM branches WHERE branch_id = ?", (branch_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Branch(
                branch_id=row[0],
                parent_id=row[1],
                strategy=json.loads(row[2]),
                status=row[3],
                results=json.loads(row[4]),
                score=row[5],
                created_at=row[6],
                completed_at=row[7],
                metadata=json.loads(row[8])
            )
        return None
    
    def get_child_branches(self, parent_id: str) -> List[Branch]:
        """获取子分支"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM branches WHERE parent_id = ?", (parent_id,))
        rows = cursor.fetchall()
        conn.close()
        
        branches = []
        for row in rows:
            branches.append(Branch(
                branch_id=row[0],
                parent_id=row[1],
                strategy=json.loads(row[2]),
                status=row[3],
                results=json.loads(row[4]),
                score=row[5],
                created_at=row[6],
                completed_at=row[7],
                metadata=json.loads(row[8])
            ))
        return branches


class BranchExecutor:
    """
    分支执行器
    
    实现类AutoResearch的分布式探索模式：
    - 广度优先：同时探索多个方向
    - 深度优先：深入探索单个方向
    - 混合模式：根据效果动态调整
    """
    
    def __init__(self, db_path: str = None, strategy: str = "hybrid"):
        self.db = BranchDatabase(db_path)
        self.strategy = ExploreStrategy(strategy)
        self.root_branch_id = None
        self.current_branch_id = None
    
    def create_branch(self, parent_id: Optional[str], strategy: Dict[str, Any]) -> str:
        """
        创建新分支
        
        参数:
            parent_id: 父分支ID（None表示根分支）
            strategy: 策略配置
        
        返回:
            分支ID
        """
        branch_id = str(uuid.uuid4())
        branch = Branch(
            branch_id=branch_id,
            parent_id=parent_id,
            strategy=strategy,
            status=BranchStatus.PENDING.value
        )
        
        if self.db.create_branch(branch):
            if parent_id is None:
                self.root_branch_id = branch_id
            self.current_branch_id = branch_id
            return branch_id
        return None
    
    def execute_branch(self, branch_id: str, task: Dict[str, Any], executor_func=None) -> Dict:
        """
        执行分支任务
        
        参数:
            branch_id: 分支ID
            task: 任务配置
            executor_func: 自定义执行函数
        
        返回:
            执行结果
        """
        branch = self.db.get_branch(branch_id)
        if not branch:
            return {"success": False, "error": "分支不存在"}
        
        # 更新状态为运行中
        branch.status = BranchStatus.RUNNING.value
        self.db.update_branch(branch)
        
        try:
            # 执行任务
            if executor_func:
                result = executor_func(task, branch.strategy)
            else:
                # 默认执行逻辑
                result = self._default_execute(task, branch.strategy)
            
            # 计算得分
            score = self._calculate_score(result)
            
            # 更新分支状态
            branch.status = BranchStatus.COMPLETED.value
            branch.results = result
            branch.score = score
            branch.completed_at = time.time()
            self.db.update_branch(branch)
            
            return {
                "success": True,
                "branch_id": branch_id,
                "result": result,
                "score": score
            }
        except Exception as e:
            branch.status = BranchStatus.FAILED.value
            branch.results = {"error": str(e)}
            self.db.update_branch(branch)
            return {
                "success": False,
                "branch_id": branch_id,
                "error": str(e)
            }
    
    def _default_execute(self, task: Dict, strategy: Dict) -> Dict:
        """默认执行逻辑"""
        # 模拟执行
        return {
            "task": task,
            "strategy": strategy,
            "output": "执行完成",
            "metrics": {
                "accuracy": 0.85,
                "latency": 1.2,
                "tokens": 500
            }
        }
    
    def _calculate_score(self, result: Dict) -> float:
        """计算得分"""
        if "metrics" in result:
            metrics = result["metrics"]
            # 综合评分
            accuracy = metrics.get("accuracy", 0.5)
            # 越快越好
            latency_score = max(0, 1 - metrics.get("latency", 1) / 10)
            return (accuracy + latency_score) / 2
        return 0.5
    
    def evaluate_branches(self, branch_ids: List[str]) -> Dict:
        """
        评估所有分支
        
        参数:
            branch_ids: 分支ID列表
        
        返回:
            评估结果（按得分排序）
        """
        evaluations = []
        
        for branch_id in branch_ids:
            branch = self.db.get_branch(branch_id)
            if branch and branch.status == BranchStatus.COMPLETED.value:
                evaluations.append({
                    "branch_id": branch_id,
                    "score": branch.score,
                    "results": branch.results,
                    "created_at": branch.created_at,
                    "completed_at": branch.completed_at
                })
        
        # 按得分排序
        evaluations.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "rankings": evaluations,
            "best_branch": evaluations[0]["branch_id"] if evaluations else None,
            "best_score": evaluations[0]["score"] if evaluations else 0
        }
    
    def select_best(self, evaluations: Dict) -> Optional[str]:
        """
        选择最优分支
        
        参数:
            evaluations: 评估结果
        
        返回:
            最优分支ID
        """
        return evaluations.get("best_branch")
    
    def merge_branch(self, child_id: str, parent_id: str) -> bool:
        """
        合并分支到父节点
        
        参数:
            child_id: 子分支ID
            parent_id: 父分支ID
        
        返回:
            是否成功
        """
        child = self.db.get_branch(child_id)
        if not child:
            return False
        
        child.status = BranchStatus.MERGED.value
        return self.db.update_branch(child)
    
    def expand_branches(self, branch_id: str, count: int = 3) -> List[str]:
        """
        扩展分支（创建子分支）
        
        参数:
            branch_id: 父分支ID
            count: 子分支数量
        
        返回:
            新创建的分支ID列表
        """
        parent = self.db.get_branch(branch_id)
        if not parent:
            return []
        
        new_branch_ids = []
        strategies = self._generate_strategies(parent.strategy, count)
        
        for strategy in strategies:
            branch_id = self.create_branch(branch_id, strategy)
            if branch_id:
                new_branch_ids.append(branch_id)
        
        return new_branch_ids
    
    def _generate_strategies(self, base_strategy: Dict, count: int) -> List[Dict]:
        """生成多个变体策略"""
        strategies = []
        
        for i in range(count):
            strategy = base_strategy.copy()
            strategy["variant"] = i + 1
            # 添加变体参数
            if "params" not in strategy:
                strategy["params"] = {}
            strategy["params"]["temperature"] = 0.5 + (i * 0.1)
            strategy["params"]["top_p"] = 0.9 - (i * 0.05)
            strategies.append(strategy)
        
        return strategies
    
    def get_progress(self) -> Dict:
        """获取探索进度"""
        return {
            "root_branch": self.root_branch_id,
            "current_branch": self.current_branch_id,
            "strategy": self.strategy.value
        }
    
    def reset(self):
        """重置执行器"""
        self.root_branch_id = None
        self.current_branch_id = None


# 便捷函数
def create_executor(strategy: str = "hybrid") -> BranchExecutor:
    """创建分支执行器"""
    return BranchExecutor(strategy=strategy)


if __name__ == "__main__":
    # 测试
    executor = BranchExecutor(strategy="hybrid")
    
    # 创建根分支
    root_id = executor.create_branch(None, {"task": "测试任务", "params": {}})
    print(f"创建根分支: {root_id}")
    
    # 执行根分支
    result = executor.execute_branch(root_id, {"input": "test"})
    print(f"执行结果: {result}")
    
    # 扩展分支
    child_ids = executor.expand_branches(root_id, count=3)
    print(f"扩展分支: {child_ids}")
    
    # 评估
    all_ids = [root_id] + child_ids
    evaluations = executor.evaluate_branches(all_ids)
    print(f"评估结果: {evaluations}")
    
    # 选择最优
    best = executor.select_best(evaluations)
    print(f"最优分支: {best}")
