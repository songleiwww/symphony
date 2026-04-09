# -*- coding: utf-8 -*-
"""内核自愈包装�?- 零侵入兼容现�?EvolutionKernel v4.3.0"""
import time
import logging
from typing import Any, Dict, Optional, List
from functools import wraps

from .self_healing_monitor import SelfHealingMonitor
from .types import HealthStatus

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries: int = 3, retry_delay: float = 1.0):
    """方法重试装饰器：API调用失败自动重试"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    retries += 1
                    logger.warning(f"Method {func.__name__} failed, retry {retries}/{max_retries}: {e}")
                    if retries >= max_retries:
                        logger.error(f"Method {func.__name__} failed after {max_retries} retries")
                        raise
                    time.sleep(retry_delay)
            return None
        return wrapper
    return decorator

class SelfHealingKernelWrapper:
    """内核自愈包装器：完全兼容 EvolutionKernel 接口，零侵入添加自愈能力
    
    使用方法�?    替换原有初始化代码：
    kernel = EvolutionKernel()
    为：
    kernel = SelfHealingKernelWrapper(EvolutionKernel())
    
    所有原有接口保持不变，自动获得自愈能力
    """
    def __init__(self, kernel_instance, monitor_config: Optional[Dict] = None):
        self.kernel = kernel_instance
        self.monitor = SelfHealingMonitor(self.kernel, monitor_config)
        # 启动监控�?        self.monitor.start()
        logger.info("Self-healing kernel wrapper initialized, monitor running")
    
    def __getattr__(self, name: str) -> Any:
        """转发所有未定义的属性和方法到原内核实例，保证接口完全兼�?""
        attr = getattr(self.kernel, name)
        if callable(attr):
            # 对方法添加重试装饰器
            @wraps(attr)
            def wrapped(*args, **kwargs):
                try:
                    return attr(*args, **kwargs)
                except Exception as e:
                    # 捕获异常，通知监控�?                    logger.warning(f"Kernel method {name} raised exception: {e}")
                    # 重试3�?                    for i in range(3):
                        try:
                            time.sleep(0.5)
                            return attr(*args, **kwargs)
                        except Exception as retry_e:
                            logger.warning(f"Retry {i+1} for {name} failed: {retry_e}")
                    # 重试失败，尝试降级处�?                    logger.error(f"All retries failed for {name}, triggering fallback")
                    return self._get_fallback_response(name, *args, **kwargs)
            return wrapped
        return attr
    
    def _get_fallback_response(self, method_name: str, *args, **kwargs) -> Any:
        """获取降级响应，保证业务不中断"""
        logger.info(f"Using fallback for method {method_name}")
        
        # 常用方法的降级响�?        if method_name == "execute":
            return {
                "status": "degraded",
                "result": "系统当前负载较高，已为您切换到轻量模式处理请�?,
                "degraded": True,
                "timestamp": time.time()
            }
        elif method_name == "dispatch_task":
            return {
                "task_id": f"degraded_{int(time.time())}",
                "status": "pending",
                "degraded": True,
                "message": "任务已提交，将在资源可用时执�?
            }
        elif method_name == "_get_online_models_from_federation":
            # 返回备用模型列表
            return [
                {"provider": "zhipu", "model": "glm-4-flash", "status": "online"},
                {"provider": "nvidia", "model": "deepseek-ai/deepseek-v3.2", "status": "online"}
            ]
        
        # 默认降级响应
        return {
            "status": "degraded",
            "message": "服务暂时不可用，已触发降级模�?,
            "degraded": True,
            "timestamp": time.time()
        }
    
    @retry_on_failure(max_retries=3)
    def execute(self, task: str, *args, **kwargs) -> Dict[str, Any]:
        """包装execute方法，添加重试和降级能力"""
        return self.kernel.execute(task, *args, **kwargs)
    
    @retry_on_failure(max_retries=2)
    def dispatch(self, task: str, *args, **kwargs) -> Dict[str, Any]:
        """包装dispatch方法，添加重试和降级能力"""
        if hasattr(self.kernel, 'dispatch'):
            return self.kernel.dispatch(task, *args, **kwargs)
        return self.execute(task, *args, **kwargs)
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取系统健康状态（新增方法，不影响原有接口�?""
        report = self.monitor.get_health_report()
        if not report:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health report available"
            }
        
        return {
            "status": report.overall_status.value,
            "timestamp": report.timestamp,
            "resource_usage": report.resource_usage,
            "component_status": {k: v.value for k, v in report.component_status.items()},
            "anomaly_count": len(report.anomalies)
        }
    
    def generate_rca_report(self, hours: int = 24) -> Dict[str, Any]:
        """生成最近N小时的根因分析报告（新增方法�?""
        end_time = time.time()
        start_time = end_time - hours * 3600
        return self.monitor.generate_rca_report(start_time, end_time)
    
    def stop(self):
        """停止内核和监控器"""
        self.monitor.stop()
        if hasattr(self.kernel, 'stop'):
            self.kernel.stop()
        logger.info("Self-healing kernel stopped")

