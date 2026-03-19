"""
序境内核 - 主模块
基于序境系统总则构建
集成所有子模块的统一入口
"""

import time
from typing import Dict, Optional
import logging

from .core.scheduler import Scheduler, SchedulerConfig, ModelConfig, ModelStatus, get_scheduler
from .rules.engine import RuleEngine, get_rule_engine
from .monitor.monitor import Monitor, get_monitor
from .logs.logger import XujingLogger, get_logger
from .infra.database import ModelRepository
from .infra.api_client import APIClient, get_client

logger = logging.getLogger(__name__)


class XujingKernel:
    """
    序境内核 (总则第2条)
    集成调度/规则/监控/日志的自我维护系统
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.scheduler = get_scheduler()
        self.rule_engine = get_rule_engine()
        self.monitor = get_monitor()
        self.logger = get_logger()
        self.model_repo = ModelRepository(db_path)
        self.api_client = get_client()
        self._initialized = False
    
    def initialize(self):
        """初始化内核"""
        if self._initialized:
            return
        
        # 加载模型配置
        models = self.model_repo.get_all_enabled()
        for m in models:
            model = ModelConfig(
                model_id=str(m['id']),
                model_name=m['model_name'],
                provider=m['provider'],
                api_url=m['api_url'],
                api_key=m['api_key']
            )
            self.scheduler.register_model(model)
        
        logger.info(f"序境内核初始化完成: {len(models)}个模型")
        self._initialized = True
    
    def dispatch(self, prompt: str, user_id: str = "", **kwargs) -> Dict:
        """
        调度请求 (总则第6/7/8条)
        1. 选择模型
        2. 规则检查
        3. 调用API
        4. 记录结果
        """
        start_time = time.time()
        
        # 1. 选择模型 (总则第8条)
        model = self.scheduler.select_model()
        if not model:
            return {"error": "无可用模型", "code": 503}
        
        # 2. 规则检查 (总则第7条)
        context = {"prompt": prompt, "model": model.model_name, "user_id": user_id}
        rule_result = self.rule_engine.evaluate(context)
        
        # 3. 调用API
        result = self.api_client.call(
            api_url=model.api_url,
            api_key=model.api_key,
            model=model.model_name,
            prompt=prompt,
            **kwargs
        )
        
        latency = (time.time() - start_time) * 1000
        
        if result.get("success"):
            tokens = result.get("total_tokens", 0)
            
            # 4. 记录成功
            self.scheduler.on_success(model, tokens, latency)
            self.logger.log_dispatch(model.model_name, model.provider, tokens, user_id)
            self.monitor.record("tokens_used", tokens, {"model": model.model_name})
            self.monitor.record("latency_ms", latency, {"model": model.model_name})
            
            return {
                "code": 200,
                "content": result.get("content", ""),
                "model": model.model_name,
                "provider": model.provider,
                "tokens": tokens,
                "latency_ms": latency
            }
        else:
            # 4. 记录失败
            self.scheduler.on_fail(model)
            self.logger.log("error", f"调度失败: {result.get('error')}", model_name=model.model_name)
            self.monitor.record("fail_count", 1, {"model": model.model_name})
            
            # 尝试备用模型 (总则第16条)
            return self._fallback_dispatch(prompt, user_id, **kwargs)
    
    def _fallback_dispatch(self, prompt: str, user_id: str, **kwargs) -> Dict:
        """备用模型调度 (总则第16条)"""
        logger.info("尝试备用模型调度")
        
        # 排除当前失败的模型
        failed_models = [m.model_name for m in self.scheduler.models.values() if m.status == ModelStatus.DEGRADE]
        
        for model in self.scheduler.models.values():
            if model.model_name in failed_models:
                continue
            if model.status not in [ModelStatus.ONLINE, ModelStatus.DEGRADE]:
                continue
            
            result = self.api_client.call(
                api_url=model.api_url,
                api_key=model.api_key,
                model=model.model_name,
                prompt=prompt,
                **kwargs
            )
            
            if result.get("success"):
                tokens = result.get("total_tokens", 0)
                self.scheduler.on_success(model, tokens, 0)
                self.logger.log_dispatch(model.model_name, model.provider, tokens, user_id)
                
                return {
                    "code": 200,
                    "content": result.get("content", ""),
                    "model": model.model_name,
                    "provider": model.provider,
                    "tokens": tokens,
                    "fallback": True
                }
        
        return {"error": "所有模型均失败", "code": 503}
    
    def record_usage(self, model_name: str, provider: str, tokens: int, user_id: str = ""):
        """记录使用 (总则第24条)"""
        model = next((m for m in self.scheduler.models.values() if m.model_name == model_name), None)
        if model:
            self.scheduler.on_success(model, tokens, 0)
        self.logger.log_dispatch(model_name, provider, tokens, user_id)
        self.monitor.record("tokens_used", tokens, {"model": model_name, "provider": provider})
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "scheduler": self.scheduler.get_stats(),
            "monitor": self.monitor.get_stats(),
            "logger": self.logger.get_summary()
        }
    
    def reload_models(self):
        """重新加载模型配置"""
        models = self.model_repo.get_all_enabled()
        for m in models:
            model = ModelConfig(
                model_id=str(m['id']),
                model_name=m['模型名称'],
                provider=m['服务商'],
                api_url=m['API地址'],
                api_key=m['API密钥']
            )
            self.scheduler.register_model(model)
        logger.info(f"重新加载模型: {len(models)}个")


_kernel: Optional[XujingKernel] = None


def get_kernel(db_path: str = "") -> XujingKernel:
    """获取内核实例"""
    global _kernel
    if _kernel is None:
        if not db_path:
            db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
        _kernel = XujingKernel(db_path)
        _kernel.initialize()
    return _kernel
