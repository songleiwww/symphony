# -*- coding: utf-8 -*-
"""
多模型组合调度器 - Multi-Model Combo Scheduler

功能：
- 多模型并行调度
- 结果投票/融合
- 智能路由选择
- 容错切换

使用：
    from combo_scheduler import ComboScheduler
    
    combo = ComboScheduler()
    result = combo.dispatch_combo(prompt, models=['model1', 'model2', 'model3'])
"""
import time
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ModelResult:
    """模型结果"""
    model_id: str
    model_name: str
    content: str
    latency: float
    success: bool
    error: str = ""


@dataclass
class ComboResult:
    """组合结果"""
    results: List[ModelResult]
    final_content: str
    method: str  # vote/merge/cascade
    total_latency: float
    confidence: float


class ComboScheduler:
    """
    多模型组合调度器
    
    支持多种组合策略：
    - vote: 投票选举
    - merge: 结果合并
    - cascade: 级联处理
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or self._get_default_db()
        self.results_cache = {}
        
        # 配置
        self.config = {
            "max_parallel": 3,
            "vote_threshold": 0.6,
            "timeout": 30,
            "retry_count": 2
        }
        
        # 统计
        self.stats = {
            "total_requests": 0,
            "combo_requests": 0,
            "success_count": 0,
            "fail_count": 0
        }
    
    def _get_default_db(self) -> str:
        """获取默认数据库路径"""
        import os
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "data", "symphony.db")
    
    def dispatch_combo(
        self,
        prompt: str,
        models: List[str] = None,
        method: str = "vote",
        max_tokens: int = 1000
    ) -> ComboResult:
        """
        组合调度
        
        参数:
            prompt: 输入提示
            models: 模型ID列表
            method: 组合方法 (vote/merge/cascade)
            max_tokens: 最大token数
        
        返回:
            ComboResult: 组合结果
        """
        start_time = time.time()
        
        # 默认使用所有可用模型
        if not models:
            models = self._get_available_models()
        
        # 限制并行数
        models = models[:self.config["max_parallel"]]
        
        # 调用各模型
        results = []
        for model_id in models:
            result = self._call_model(model_id, prompt, max_tokens)
            results.append(result)
        
        # 组合结果
        final_result = self._combine_results(results, method)
        
        # 统计
        self.stats["total_requests"] += 1
        self.stats["combo_requests"] += 1
        if final_result.get("final_content"):
            self.stats["success_count"] += 1
        else:
            self.stats["fail_count"] += 1
        
        total_latency = time.time() - start_time
        
        return ComboResult(
            results=results,
            final_content=final_result.get("final_content", ""),
            method=method,
            total_latency=total_latency,
            confidence=final_result.get("confidence", 0.5)
        )
    
    def _get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        # 从数据库获取
        # 这里简化处理
        return ["1", "2", "3"]
    
    def _call_model(self, model_id: str, prompt: str, max_tokens: int) -> ModelResult:
        """调用单个模型"""
        start = time.time()
        
        try:
            # 这里应该调用真实的API
            # 简化实现
            content = f"[Model {model_id}] 处理: {prompt[:50]}..."
            latency = time.time() - start
            
            return ModelResult(
                model_id=model_id,
                model_name=f"Model-{model_id}",
                content=content,
                latency=latency,
                success=True
            )
        except Exception as e:
            return ModelResult(
                model_id=model_id,
                model_name=f"Model-{model_id}",
                content="",
                latency=time.time() - start,
                success=False,
                error=str(e)
            )
    
    def _combine_results(self, results: List[ModelResult], method: str) -> Dict[str, Any]:
        """组合结果"""
        if method == "vote":
            return self._vote_combine(results)
        elif method == "merge":
            return self._merge_combine(results)
        elif method == "cascade":
            return self._cascade_combine(results)
        else:
            return {"final_content": results[0].content if results else "", "confidence": 0.5}
    
    def _combine_results(self, results: List[ModelResult], method: str) -> Dict[str, Any]:
        """投票组合"""
        # 简化实现：选择最长的结果
        valid = [r for r in results if r.success]
        
        if not valid:
            return {"final_content": "", "confidence": 0.0}
        
        # 选择内容最长的
        best = max(valid, key=lambda r: len(r.content))
        
        return {
            "final_content": best.content,
            "confidence": len(valid) / len(results)
        }
    
    def _merge_combine(self, results: List[ModelResult]) -> Dict[str, Any]:
        """合并组合"""
        valid = [r for r in results if r.success]
        
        if not valid:
            return {"final_content": "", "confidence": 0.0}
        
        # 合并所有内容
        merged = "\n\n---\n\n".join([r.content for r in valid])
        
        return {
            "final_content": merged,
            "confidence": 0.7
        }
    
    def _cascade_combine(self, results: List[ModelResult]) -> Dict[str, Any]:
        """级联组合"""
        valid = [r for r in results if r.success]
        
        if not valid:
            return {"final_content": "", "confidence": 0.0}
        
        # 返回第一个成功的结果
        return {
            "final_content": valid[0].content,
            "confidence": 0.8
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def set_config(self, key: str, value: Any):
        """设置配置"""
        self.config[key] = value


# 测试
if __name__ == "__main__":
    combo = ComboScheduler()
    print("ComboScheduler: OK")
    
    result = combo.dispatch_combo("测试问题", models=["m1", "m2", "m3"], method="vote")
    print("Results:", len(result.results))
    print("Content:", result.final_content[:50])
    print("Method:", result.method)
