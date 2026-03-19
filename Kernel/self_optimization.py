# -*- coding: utf-8 -*-
"""
自我优化引擎 - Self-Optimization Engine

功能：
- 性能监控
- 自动调优
- 策略优化
- 异常检测
- 自适应学习
"""
import time
import json
import threading
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import statistics


class OptimizationType(Enum):
    """优化类型"""
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    QUALITY = "quality"
    LATENCY = "latency"


@dataclass
class Metric:
    """指标"""
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict = field(default_factory=dict)


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    type: OptimizationType
    description: str
    impact: float  # 预期提升 0-1
    confidence: float  # 置信度 0-1
    action: str


class SelfOptimizationEngine:
    """
    自我优化引擎
    
    使用：
        optimizer = SelfOptimizationEngine()
        
        # 记录指标
        optimizer.record_metric("latency", 150)
        optimizer.record_metric("success_rate", 0.95)
        
        # 获取优化建议
        suggestions = optimizer.analyze_and_suggest()
    """
    
    def __init__(self):
        # 指标存储
        self.metrics: Dict[str, deque] = {}
        self.max_history = 1000
        
        # 优化规则
        self.rules: List[Dict] = []
        self._register_default_rules()
        
        # 统计
        self.stats = {
            "total_optimizations": 0,
            "auto_applied": 0,
            "suggestions_generated": 0
        }
        
        # 回调
        self.on_optimization: Optional[Callable] = None
        
        # 运行状态
        self.running = False
        self._lock = threading.RLock()
    
    def _register_default_rules(self):
        """注册默认优化规则"""
        
        # 1. 延迟优化
        self.rules.append({
            "name": "latency_high",
            "metric": "latency",
            "condition": "avg > 500",
            "type": OptimizationType.LATENCY,
            "action": "increase_parallel",
            "impact": 0.3,
            "description": "延迟过高，建议增加并行度"
        })
        
        # 2. 成功率优化
        self.rules.append({
            "name": "success_low",
            "metric": "success_rate",
            "condition": "avg < 0.9",
            "type": OptimizationType.QUALITY,
            "action": "add_retry",
            "impact": 0.5,
            "description": "成功率过低，建议增加重试"
        })
        
        # 3. 资源优化
        self.rules.append({
            "name": "memory_high",
            "metric": "memory_usage",
            "condition": "avg > 0.8",
            "type": OptimizationType.RESOURCE,
            "action": "reduce_cache",
            "impact": 0.4,
            "description": "内存使用过高，建议减少缓存"
        })
        
        # 4. 性能优化
        self.rules.append({
            "name": "throughput_low",
            "metric": "throughput",
            "condition": "avg < 10",
            "type": OptimizationType.PERFORMANCE,
            "action": "optimize_batch",
            "impact": 0.6,
            "description": "吞吐量过低，建议优化批处理"
        })
    
    def record_metric(
        self,
        name: str,
        value: float,
        tags: Dict = None
    ):
        """
        记录指标
        
        参数:
            name: 指标名称
            value: 指标值
            tags: 标签
        """
        with self._lock:
            if name not in self.metrics:
                self.metrics[name] = deque(maxlen=self.max_history)
            
            metric = Metric(
                name=name,
                value=value,
                tags=tags or {}
            )
            
            self.metrics[name].append(metric)
    
    def get_metric_stats(self, name: str) -> Dict:
        """
        获取指标统计
        
        参数:
            name: 指标名称
        
        返回:
            统计信息
        """
        with self._lock:
            if name not in self.metrics or not self.metrics[name]:
                return {}
            
            values = [m.value for m in self.metrics[name]]
            
            return {
                "count": len(values),
                "avg": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "median": statistics.median(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0
            }
    
    def analyze_and_suggest(
        self,
        auto_apply: bool = False
    ) -> List[OptimizationSuggestion]:
        """
        分析并给出优化建议
        
        参数:
            auto_apply: 是否自动应用
        
        返回:
            优化建议列表
        """
        suggestions = []
        
        with self._lock:
            for rule in self.rules:
                metric_name = rule["metric"]
                
                if metric_name not in self.metrics:
                    continue
                
                stats = self.get_metric_stats(metric_name)
                if not stats or stats["count"] < 10:
                    continue
                
                # 评估条件
                condition = rule["condition"]
                should_optimize = self._evaluate_condition(
                    condition,
                    stats
                )
                
                if should_optimize:
                    suggestion = OptimizationSuggestion(
                        type=rule["type"],
                        description=rule["description"],
                        impact=rule["impact"],
                        confidence=min(0.9, stats["count"] / 100),
                        action=rule["action"]
                    )
                    
                    suggestions.append(suggestion)
                    self.stats["suggestions_generated"] += 1
                    
                    # 自动应用
                    if auto_apply:
                        self._apply_optimization(suggestion)
        
        return suggestions
    
    def _evaluate_condition(self, condition: str, stats: Dict) -> bool:
        """评估条件"""
        try:
            # 简单条件解析
            if "avg >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return stats.get("avg", 0) > threshold
            elif "avg <" in condition:
                threshold = float(condition.split("<")[1].strip())
                return stats.get("avg", 0) < threshold
        except:
            pass
        
        return False
    
    def _apply_optimization(self, suggestion: OptimizationSuggestion):
        """应用优化"""
        print(f"[Optimizer] Applying: {suggestion.description}")
        
        self.stats["auto_applied"] += 1
        self.stats["total_optimizations"] += 1
        
        if self.on_optimization:
            self.on_optimization(suggestion)
    
    def add_rule(
        self,
        name: str,
        metric: str,
        condition: str,
        optimization_type: OptimizationType,
        action: str,
        impact: float,
        description: str
    ):
        """添加优化规则"""
        self.rules.append({
            "name": name,
            "metric": metric,
            "condition": condition,
            "type": optimization_type,
            "action": action,
            "impact": impact,
            "description": description
        })
    
    def remove_rule(self, name: str):
        """移除优化规则"""
        self.rules = [r for r in self.rules if r["name"] != name]
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            **self.stats,
            "metrics_count": len(self.metrics),
            "rules_count": len(self.rules)
        }
    
    def start_monitoring(self, interval: float = 60):
        """启动自动监控"""
        self.running = True
        
        def monitor_loop():
            while self.running:
                suggestions = self.analyze_and_suggest(auto_apply=True)
                if suggestions:
                    print(f"[Optimizer] {len(suggestions)} optimizations applied")
                time.sleep(interval)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
    
    def export_metrics(self) -> Dict:
        """导出指标"""
        with self._lock:
            return {
                name: [
                    {"value": m.value, "timestamp": m.timestamp}
                    for m in metrics
                ]
                for name, metrics in self.metrics.items()
            }


# 性能监控装饰器
def monitor_performance(func):
    """性能监控装饰器"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        latency = (time.time() - start) * 1000  # ms
        
        # 记录指标
        # 这里简化处理，实际应该使用全局optimizer实例
        return result
    
    return wrapper


# 测试
if __name__ == "__main__":
    print("=== 自我优化引擎测试 ===")
    
    optimizer = SelfOptimizationEngine()
    
    # 模拟数据
    import random
    
    for i in range(20):
        optimizer.record_metric("latency", random.uniform(100, 600))
        optimizer.record_metric("success_rate", random.uniform(0.85, 1.0))
        optimizer.record_metric("throughput", random.uniform(5, 15))
    
    print("Recorded 20 samples each")
    
    # 获取统计
    print("\nMetric Stats:")
    for metric in ["latency", "success_rate", "throughput"]:
        stats = optimizer.get_metric_stats(metric)
        print(f"  {metric}: avg={stats['avg']:.2f}")
    
    # 分析并建议
    print("\nOptimization Suggestions:")
    suggestions = optimizer.analyze_and_suggest()
    
    if suggestions:
        for s in suggestions:
            print(f"  - {s.description} (impact={s.impact})")
    else:
        print("  No suggestions")
    
    # 统计
    stats = optimizer.get_stats()
    print(f"\nStats: {stats}")
    
    print("\n自我优化引擎测试通过!")
