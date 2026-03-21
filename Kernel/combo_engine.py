#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境统一组合引擎 v4.0
合并自：combo_skill, combo_scheduler, super_combo_v3

功能：
- 多模型并行/串行组合
- 投票/置信度/级联融合
- 智能路由选择
- 容错切换
- 自适应调度

使用：
    from combo_engine import ComboEngine
    
    combo = ComboEngine()
    result = combo.dispatch(prompt, models=['model1', 'model2'])
"""
import time
import json
import sqlite3
import os
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from enum import Enum

KERNEL_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(KERNEL_PATH, '..', 'data')
DB_PATH = os.path.join(DATA_PATH, 'symphony.db')


class FusionMethod(Enum):
    """融合方法"""
    VOTE = "vote"           # 投票
    CONFIDENCE = "confidence"  # 置信度
    CASCADE = "cascade"     # 级联
    ADAPTIVE = "adaptive"   # 自适应


class ComboMode(Enum):
    """组合模式"""
    PARALLEL = "parallel"  # 并行
    SEQUENTIAL = "sequential"  # 串行


@dataclass
class ModelResult:
    """模型结果"""
    model_id: str
    model_name: str
    provider: str
    content: str
    latency: float
    success: bool
    error: str = ""
    tokens: int = 0


@dataclass
class ComboResult:
    """组合结果"""
    results: List[ModelResult]
    final_content: str
    method: str
    total_latency: float
    success_count: int
    adaptive_used: bool = False


class ComboEngine:
    """序境统一组合引擎"""
    
    def __init__(self):
        self.mode = ComboMode.PARALLEL
        self.fusion = FusionMethod.CONFIDENCE
        self.max_workers = 5
        self.timeout = 30
        self.fallback_enabled = True
        
        # 加载配置
        self.models = self._load_models()
        self.providers = list(set(m['provider'] for m in self.models))
    
    def _load_models(self) -> List[Dict]:
        """加载可用模型"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT r.id, r.姓名, m.模型名称, m.服务商, m.API地址, m.API密钥
                FROM 官署角色表 r
                JOIN 模型配置表 m ON r.模型配置表_ID = m.id
                WHERE m.在线状态 = '正常'
            ''')
            
            models = []
            for row in cursor.fetchall():
                models.append({
                    'id': row[0],
                    'name': row[1],
                    'model': row[2],
                    'provider': row[3],
                    'api': row[4],
                    'key': row[5]
                })
        except:
            # 备用：从环境变量读取
            models = [{
                'id': 'default',
                'name': 'default',
                'model': 'ark-code-latest',
                'provider': 'volcengine',
                'api': 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
                'key': os.environ.get('ARK_API_KEY', '')
            }]
        
        conn.close()
        return models
    
    def _call_model(self, model_info: Dict, prompt: str) -> ModelResult:
        """调用单个模型"""
        start = time.time()
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {model_info['key']}"
            }
            
            resp = requests.post(
                model_info['api'],
                headers=headers,
                json={
                    'model': model_info['model'],
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 1000
                },
                timeout=self.timeout
            )
            
            latency = time.time() - start
            
            if resp.status_code == 200:
                data = resp.json()
                content = data['choices'][0]['message']['content']
                return ModelResult(
                    model_id=model_info['id'],
                    model_name=model_info['model'],
                    provider=model_info['provider'],
                    content=content,
                    latency=latency,
                    success=True
                )
            else:
                return ModelResult(
                    model_id=model_info['id'],
                    model_name=model_info['model'],
                    provider=model_info['provider'],
                    content='',
                    latency=latency,
                    success=False,
                    error=f"HTTP {resp.status_code}"
                )
                
        except Exception as e:
            return ModelResult(
                model_id=model_info['id'],
                model_name=model_info['model'],
                provider=model_info['provider'],
                content='',
                latency=time.time() - start,
                success=False,
                error=str(e)
            )
    
    def _parallel_dispatch(self, prompt: str, models: List[Dict]) -> List[ModelResult]:
        """并行调度多个模型"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._call_model, m, prompt): m 
                for m in models
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    model = futures[future]
                    results.append(ModelResult(
                        model_id=model['id'],
                        model_name=model['model'],
                        provider=model['provider'],
                        content='',
                        latency=0,
                        success=False,
                        error=str(e)
                    ))
        
        return results
    
    def _cascade_fusion(self, results: List[ModelResult]) -> str:
        """级联融合：按顺序使用结果"""
        # 优先使用成功的，最快的
        successful = [r for r in results if r.success]
        if successful:
            # 按延迟排序，返回最快的
            successful.sort(key=lambda x: x.latency)
            return successful[0].content
        return ""
    
    def _vote_fusion(self, results: List[ModelResult]) -> str:
        """投票融合"""
        successful = [r for r in results if r.success]
        if not successful:
            return ""
        if len(successful) == 1:
            return successful[0].content
        
        # 简单投票：返回第一个结果
        # 实际可扩展为文本相似度聚类
        return successful[0].content
    
    def _confidence_fusion(self, results: List[ModelResult]) -> str:
        """置信度融合"""
        successful = [r for r in results if r.success]
        if not successful:
            return ""
        if len(successful) == 1:
            return successful[0].content
        
        # 按响应速度作为置信度代理
        successful.sort(key=lambda x: x.latency)
        return successful[0].content
    
    def _adaptive_select(self, results: List[ModelResult]) -> str:
        """自适应选择"""
        successful = [r for r in results if r.success]
        if not successful:
            return ""
        
        # 策略：根据提供商数量选择
        providers = set(r.provider for r in successful)
        
        if len(providers) > 1:
            # 多提供商：选择最慢但可能更全面的
            successful.sort(key=lambda x: x.latency, reverse=True)
            return successful[0].content
        else:
            # 单提供商：选择最快的
            successful.sort(key=lambda x: x.latency)
            return successful[0].content
    
    def dispatch(self, prompt: str, models: Optional[List[str]] = None, 
                 mode: ComboMode = ComboMode.PARALLEL,
                 fusion: FusionMethod = FusionMethod.ADAPTIVE) -> ComboResult:
        """
        调度组合
        
        Args:
            prompt: 提示词
            models: 模型列表（名称或ID），None表示使用全部
            mode: 组合模式
            fusion: 融合方法
        
        Returns:
            ComboResult: 组合结果
        """
        start = time.time()
        
        # 选择模型
        if models:
            selected = [m for m in self.models if m['model'] in models or m['id'] in models]
            if not selected:
                selected = self.models[:3]  # 默认前3个
        else:
            selected = self.models[:3]
        
        # 并行调度
        results = self._parallel_dispatch(prompt, selected)
        
        # 融合
        if fusion == FusionMethod.VOTE:
            final = self._vote_fusion(results)
        elif fusion == FusionMethod.CONFIDENCE:
            final = self._confidence_fusion(results)
        elif fusion == FusionMethod.CASCADE:
            final = self._cascade_fusion(results)
        else:  # ADAPTIVE
            final = self._adaptive_select(results)
        
        total_latency = time.time() - start
        success_count = sum(1 for r in results if r.success)
        
        return ComboResult(
            results=results,
            final_content=final,
            method=fusion.value,
            total_latency=total_latency,
            success_count=success_count,
            adaptive_used=(fusion == FusionMethod.ADAPTIVE)
        )
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'models_count': len(self.models),
            'providers': self.providers,
            'mode': self.mode.value,
            'fusion': self.fusion.value,
            'max_workers': self.max_workers
        }


# 全局实例
_combo_engine = None

def get_combo_engine() -> ComboEngine:
    """获取组合引擎实例"""
    global _combo_engine
    if _combo_engine is None:
        _combo_engine = ComboEngine()
    return _combo_engine
