#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw配置加载器
让交响自动从OpenClaw配置读取真实的模型和API Key
"""

import sys
import io

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


class OpenClawConfigLoader:
    """OpenClaw配置加载器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化加载器
        
        Args:
            config_path: OpenClaw配置文件路径，默认从用户目录读取
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".openclaw" / "openclaw.cherry.json"
        
        self._config: Optional[Dict] = None
    
    def load(self) -> Dict:
        """
        加载OpenClaw配置
        
        Returns:
            配置字典
        
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件解析失败
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"OpenClaw配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)
        
        return self._config
    
    def get_providers(self) -> Dict[str, Dict]:
        """
        获取所有提供商配置
        
        Returns:
            提供商字典，格式: {provider_name: provider_config}
        """
        if not self._config:
            self.load()
        
        return self._config.get("models", {}).get("providers", {})
    
    def get_models(self) -> List[Dict]:
        """
        获取所有模型配置，转换为交响格式
        
        Returns:
            模型列表，兼容交响的MODEL_CHAIN格式
        """
        providers = self.get_providers()
        models = []
        priority = 1
        
        # 按顺序处理提供商（确保优先级一致）
        provider_order = ["cherry-doubao", "cherry-minimax", "cherry-nvidia", "cherry-modelscope"]
        
        for provider_name in provider_order:
            if provider_name not in providers:
                continue
            
            provider_config = providers[provider_name]
            provider_models = provider_config.get("models", [])
            api_key = provider_config.get("apiKey", "")
            base_url = provider_config.get("baseURL", "")
            api_type = provider_config.get("apiType", "openai-completions")
            
            for model in provider_models:
                model_config = {
                    "name": self._generate_model_name(provider_name, model.get("id", "")),
                    "provider": provider_name,
                    "model_id": model.get("id", ""),
                    "alias": model.get("name", model.get("id", "")),
                    "base_url": base_url,
                    "api_key": api_key,
                    "api_type": api_type,
                    "context_window": model.get("contextWindow", 128000),
                    "timeout": 30,
                    "max_retries": 3,
                    "enabled": True,
                    "priority": priority
                }
                models.append(model_config)
                priority += 1
        
        # 验证模型数量
        doubao_count = sum(1 for m in models if m["provider"] == "cherry-doubao")
        minimax_count = sum(1 for m in models if m["provider"] == "cherry-minimax")
        nvidia_count = sum(1 for m in models if m["provider"] == "cherry-nvidia")
        modelscope_count = sum(1 for m in models if m["provider"] == "cherry-modelscope")
        
        # 检查数量是否正确
        if doubao_count != 5:
            print(f"⚠️ cherry-doubao有{doubao_count}个模型，期望5个")
        if minimax_count != 1:
            print(f"⚠️ cherry-minimax有{minimax_count}个模型，期望1个")
        if nvidia_count != 9:
            print(f"⚠️ cherry-nvidia有{nvidia_count}个模型，期望9个")
        if modelscope_count != 2:
            print(f"⚠️ cherry-modelscope有{modelscope_count}个模型，期望2个")
        
        return models
    
    def _generate_model_name(self, provider: str, model_id: str) -> str:
        """
        生成模型内部名称
        
        Args:
            provider: 提供商名称
            model_id: 模型ID
        
        Returns:
            清理后的模型名称
        """
        # 移除提供商前缀
        name = model_id
        
        # 替换特殊字符
        name = name.replace("/", "_")
        name = name.replace(".", "_")
        name = name.replace("-", "_")
        
        # 添加提供商前缀
        prefix = provider.replace("-", "_")
        
        return f"{prefix}_{name}"
    
    def get_model_by_priority(self, priority: int) -> Optional[Dict]:
        """
        根据优先级获取模型
        
        Args:
            priority: 优先级（1开始）
        
        Returns:
            模型配置，如果不存在返回None
        """
        models = self.get_models()
        for model in models:
            if model.get("priority") == priority:
                return model
        return None
    
    def get_model_by_name(self, name: str) -> Optional[Dict]:
        """
        根据名称获取模型
        
        Args:
            name: 模型名称
        
        Returns:
            模型配置，如果不存在返回None
        """
        models = self.get_models()
        for model in models:
            if model.get("name") == name:
                return model
        return None
    
    def print_summary(self):
        """打印配置摘要"""
        models = self.get_models()
        providers = self.get_providers()
        
        print("=" * 70)
        print("📦 OpenClaw配置加载器 - 配置摘要")
        print("=" * 70)
        print(f"\n配置文件: {self.config_path}")
        print(f"提供商数量: {len(providers)}")
        print(f"模型总数: {len(models)}")
        
        # 按提供商分组
        provider_models: Dict[str, List] = {}
        for model in models:
            p = model["provider"]
            if p not in provider_models:
                provider_models[p] = []
            provider_models[p].append(model)
        
        print("\n按提供商:")
        for provider_name, provider_models_list in provider_models.items():
            print(f"  {provider_name}: {len(provider_models_list)} 个模型")
            for i, model in enumerate(provider_models_list[:3], 1):
                print(f"    {i}. {model['alias']}")
            if len(provider_models_list) > 3:
                print(f"    ... 还有 {len(provider_models_list) - 3} 个")
        
        print("\n" + "=" * 70)


# 便捷函数
def load_symphony_models(config_path: Optional[str] = None) -> List[Dict]:
    """
    便捷函数：直接加载交响格式的模型列表
    
    Args:
        config_path: OpenClaw配置文件路径
    
    Returns:
        模型列表，可直接赋值给MODEL_CHAIN
    """
    loader = OpenClawConfigLoader(config_path)
    return loader.get_models()


def create_updated_config(config_path: Optional[str] = None) -> str:
    """
    创建更新后的config.py内容
    
    Args:
        config_path: OpenClaw配置文件路径
    
    Returns:
        新的config.py内容
    """
    loader = OpenClawConfigLoader(config_path)
    models = loader.get_models()
    
    # 生成模型列表代码
    models_code = "[\n"
    for model in models:
        models_code += "    {\n"
        for key, value in model.items():
            if isinstance(value, str):
                models_code += f'        "{key}": "{value}",\n'
            else:
                models_code += f'        "{key}": {value},\n'
        models_code += "    },\n"
    models_code += "]"
    
    # 读取原始config.py
    config_py_path = Path(__file__).parent / "config.py"
    with open(config_py_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # 替换MODEL_CHAIN
    import re
    new_content = re.sub(
        r"MODEL_CHAIN\s*=\s*\[.*?\]",
        f"MODEL_CHAIN = {models_code}",
        original_content,
        flags=re.DOTALL
    )
    
    return new_content


if __name__ == "__main__":
    # 测试
    loader = OpenClawConfigLoader()
    loader.print_summary()
