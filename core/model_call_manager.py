#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型调用管理器 - 统一模型调用入口（修复版）
"""
import os
import sys
import time
import requests
import sqlite3
from typing import Dict, List, Optional, Tuple
from collections import deque

class ModelCallManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            current_file = os.path.abspath(__file__)
            project_dir = os.path.dirname(os.path.dirname(current_file))
            self.db_path = os.path.join(project_dir, "data", "symphony.db")
        else:
            self.db_path = db_path
        
        # 限流控制
        self.rate_limits = {
            "火山引擎": {"max_calls": 60, "window": 60},
            "智谱": {"max_calls": 100, "window": 60},
            "硅基流动": {"max_calls": 60, "window": 60},
            "OpenRouter": {"max_calls": 20, "window": 60},
        }
        
        # 调用记录
        self.call_history: Dict[str, deque] = {}
        
        # 已加载的模型配置
        self.model_configs: Dict[str, Dict] = {}
        self._load_model_configs()
    
    def _load_model_configs(self):
        """从数据库加载模型配置"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询所有在线模型
            cursor.execute('SELECT id, 模型名称, 服务商, url, key, 限制说明 FROM 模型配置表 WHERE 是否在线="在线"')
            
            for row in cursor.fetchall():
                model_name = row[1]
                self.model_configs[model_name] = {
                    "id": row[0],
                    "name": model_name,
                    "provider": row[2],
                    "url": row[3],
                    "key": row[4],
                    "limit_desc": row[5]
                }
            
            conn.close()
            print(f"已加载 {len(self.model_configs)} 个模型配置")
        except Exception as e:
            print(f"加载模型配置失败: {e}")
    
    def _check_rate_limit(self, provider: str) -> bool:
        """检查是否触发限流"""
        if provider not in self.rate_limits:
            return True
        
        now = time.time()
        limit = self.rate_limits[provider]
        
        if provider not in self.call_history:
            self.call_history[provider] = deque()
        
        # 清理过期的调用记录
        while self.call_history[provider] and now - self.call_history[provider][0] > limit["window"]:
            self.call_history[provider].popleft()
        
        # 检查是否超限
        if len(self.call_history[provider]) >= limit["max_calls"]:
            return False
        
        # 记录本次调用
        self.call_history[provider].append(now)
        return True
    
    def call_model(self, model_name: str, prompt: str, **kwargs) -> Tuple[bool, str, Dict]:
        """调用模型"""
        if model_name not in self.model_configs:
            return False, f"模型 {model_name} 不存在", {}
        
        config = self.model_configs[model_name]
        provider = config["provider"]
        
        # 检查限流
        if not self._check_rate_limit(provider):
            return False, f"服务商 {provider} 触发限流，请稍后再试", {}
        
        try:
            url = config["url"]
            key = config["key"]
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}"
            }
            
            data = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", 2000)
            }
            
            # 发送请求
            start_time = time.time()
            response = requests.post(url, headers=headers, json=data, timeout=kwargs.get("timeout", 60))
            duration = time.time() - start_time
            
            # 解析响应
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                
                return True, content, {
                    "model": model_name,
                    "provider": provider,
                    "duration": duration,
                    "token_usage": usage.get("total_tokens", 0)
                }
            else:
                return False, f"模型返回格式错误: {result}", {}
        
        except requests.exceptions.Timeout:
            return False, "模型调用超时", {}
        except requests.exceptions.RequestException as e:
            return False, f"网络错误: {str(e)}", {}
        except Exception as e:
            return False, f"调用失败: {str(e)}", {}

# 单例实例
_model_manager_instance: Optional[ModelCallManager] = None

def get_model_manager() -> ModelCallManager:
    """获取模型调用管理器单例"""
    global _model_manager_instance
    if _model_manager_instance is None:
        _model_manager_instance = ModelCallManager()
    return _model_manager_instance

if __name__ == "__main__":
    manager = get_model_manager()
    print(f"已加载 {len(manager.model_configs)} 个模型配置")
