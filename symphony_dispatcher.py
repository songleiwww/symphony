#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交响调度器 - 统一入口
支持两种模式：
1. 独立模式：使用交响自己的config.py配置
2. OpenClaw模式：从OpenClaw读取配置
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class SymphonyDispatcher:
    """
    交响调度器 - 统一入口
    """
    
    def __init__(self, mode: str = "independent"):
        """
        初始化调度器
        
        Args:
            mode: 运行模式
                - "independent": 独立模式，使用config.py（交响自己的配置）
                - "openclaw": OpenClaw模式，从OpenClaw读取
        """
        self.mode = mode
        self.config = self._load_config()
        
        print("="*60)
        print(f"交响调度器初始化")
        print(f"运行模式: {self.mode}")
        print(f"API: {self.config.get('base_url', 'N/A')}")
        print(f"主模型: {self.config.get('primary_model', 'N/A')}")
        print("="*60)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.mode == "independent":
            return self._load_independent_config()
        else:
            return self._load_openclaw_config()
    
    def _load_independent_config(self) -> Dict[str, Any]:
        """
        加载交响独立配置（自己的config.py）
        """
        try:
            # 尝试导入config.py
            import sys
            symphony_path = Path(__file__).parent
            sys.path.insert(0, str(symphony_path))
            
            from config import API_CONFIG
            
            return {
                "api_key": API_CONFIG.get("api_key", ""),
                "base_url": API_CONFIG.get("base_url", ""),
                "primary_model": API_CONFIG.get("primary_model", "z-ai/glm4.7"),
                "models": API_CONFIG.get("models", []),
                "source": "config.py"
            }
        except Exception as e:
            print(f"加载config.py失败: {e}")
            # 硬编码备用配置
            return {
                "api_key": "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",
                "base_url": "https://integrate.api.nvidia.com/v1",
                "primary_model": "z-ai/glm4.7",
                "models": [
                    "z-ai/glm4.7",
                    "meta/llama-3.1-405b-instruct",
                    "qwen/qwen3.5-397b-a17b",
                ],
                "source": "fallback"
            }
    
    def _load_openclaw_config(self) -> Dict[str, Any]:
        """
        从OpenClaw加载配置（不推荐使用）
        """
        try:
            config_path = Path(r"C:\Users\Administrator\.openclaw\openclaw.cherry.json")
            if not config_path.exists():
                print("警告: OpenClaw配置文件不存在，使用独立配置")
                return self._load_independent_config()
            
            with open(config_path, encoding='utf-8') as f:
                openclaw_config = json.load(f)
            
            providers = openclaw_config.get("models", {}).get("providers", {})
            
            nvidia_config = providers.get("cherry-nvidia", {})
            if nvidia_config:
                models = [m["id"] for m in nvidia_config.get("models", [])]
                return {
                    "api_key": nvidia_config.get("apiKey", ""),
                    "base_url": nvidia_config.get("baseUrl", ""),
                    "primary_model": models[0] if models else "z-ai/glm4.7",
                    "models": models,
                    "source": "openclaw"
                }
            
            return self._load_independent_config()
            
        except Exception as e:
            print(f"加载OpenClaw配置失败: {e}，使用独立配置")
            return self._load_independent_config()
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config
    
    def get_models(self) -> List[str]:
        """获取可用模型列表"""
        return self.config.get("models", [])
    
    def print_info(self):
        """打印调度器信息"""
        print("\n" + "="*60)
        print("交响调度器信息")
        print("="*60)
        print(f"运行模式: {self.mode}")
        print(f"配置来源: {self.config.get('source', 'unknown')}")
        print(f"API地址: {self.config.get('base_url', 'N/A')}")
        print(f"API Key: {self.config.get('api_key', 'N/A')[:20]}...")
        print(f"主模型: {self.config.get('primary_model', 'N/A')}")
        print(f"可用模型: {len(self.config.get('models', []))}个")
        for i, m in enumerate(self.config.get("models", [])[:5], 1):
            print(f"  {i}. {m}")
        print("="*60)


# =============================================================================
# 对外接口 - 供OpenClaw调用
# =============================================================================

def get_symphony_dispatcher() -> SymphonyDispatcher:
    """
    获取交响调度器（使用独立配置）
    供OpenClaw调用时使用
    """
    return SymphonyDispatcher("independent")


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    print("测试: 独立模式（交响自己的配置）")
    dispatcher = SymphonyDispatcher("independent")
    dispatcher.print_info()
