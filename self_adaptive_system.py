"""
Symphony 自适应系统
- 实时监控
- 自动调优
- 智能预警
"""
import time
import threading
from datetime import datetime
from typing import Dict, List, Callable


class SelfAdaptiveSystem:
    """自适应系统"""
    
    def __init__(self):
        self.metrics = {
            "response_time": [],
            "error_rate": [],
            "load": []
        }
        self.thresholds = {
            "response_time": 2000,  # ms
            "error_rate": 0.05,     # 5%
            "load": 0.8             # 80%
        }
        self.alerts = []
        self.optimizations = []
        self.monitors = []
    
    def record_metric(self, metric_name: str, value: float):
        """记录指标"""
        if metric_name in self.metrics:
            self.metrics[metric_name].append({
                "value": value,
                "timestamp": datetime.now().isoformat()
            })
            # 保持最近100条
            if len(self.metrics[metric_name]) > 100:
                self.metrics[metric_name] = self.metrics[metric_name][-100:]
    
    def check_health(self) -> dict:
        """健康检查"""
        health = {"status": "healthy", "issues": []}
        
        # 检查响应时间
        if self.metrics["response_time"]:
            avg = sum(m["value"] for m in self.metrics["response_time"][-10:]) / 10
            if avg > self.thresholds["response_time"]:
                health["issues"].append(f"响应时间过高: {avg:.0f}ms")
                health["status"] = "warning"
        
        # 检查错误率
        if self.metrics["error_rate"]:
            avg = sum(m["value"] for m in self.metrics["error_rate"][-10:]) / 10
            if avg > self.thresholds["error_rate"]:
                health["issues"].append(f"错误率过高: {avg*100:.1f}%")
                health["status"] = "warning"
        
        return health
    
    def auto_optimize(self) -> List[str]:
        """自动优化"""
        suggestions = []
        health = self.check_health()
        
        if health["status"] == "warning":
            for issue in health["issues"]:
                if "响应时间" in issue:
                    suggestions.append("建议：增加缓存、优化数据库查询")
                if "错误率" in issue:
                    suggestions.append("建议：检查服务日志、排查异常")
                self.optimizations.append({
                    "issue": issue,
                    "suggestions": suggestions,
                    "timestamp": datetime.now().isoformat()
                })
        
        return suggestions
    
    def register_monitor(self, name: str, callback: Callable):
        """注册监控回调"""
        self.monitors.append({"name": name, "callback": callback})
    
    def start_monitoring(self):
        """启动监控"""
        def monitor_loop():
            while True:
                health = self.check_health()
                for monitor in self.monitors:
                    try:
                        monitor["callback"](health)
                    except:
                        pass
                time.sleep(10)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
    
    def get_system_status(self) -> dict:
        """获取系统状态"""
        return {
            "health": self.check_health(),
            "metrics_count": {k: len(v) for k, v in self.metrics.items()},
            "optimizations": len(self.optimizations),
            "alerts": len(self.alerts)
        }


# 全局实例
adaptive_system = SelfAdaptiveSystem()
