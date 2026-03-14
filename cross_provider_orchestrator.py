#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨提供商调度器 - 优先选择不同API接口的模型
Cross-Provider Orchestrator - Prioritize Different API Providers
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional


# =============================================================================
# 修复Windows编码
# =============================================================================

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# =============================================================================
# 导入配置
# =============================================================================

try:
    import config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


# =============================================================================
# 当前模型（你的模型）
# =============================================================================

CURRENT_PROVIDER = "cherry-doubao"  # 你当前使用的API


# =============================================================================
# 跨提供商调度器
# =============================================================================

class CrossProviderOrchestrator:
    """跨提供商调度器"""
    
    def __init__(self, current_provider: str = CURRENT_PROVIDER):
        self.current_provider = current_provider
        self.models = self._load_models()
    
    def _load_models(self) -> List[Dict[str, Any]]:
        """加载模型列表"""
        if CONFIG_AVAILABLE:
            return getattr(config, "MODEL_CHAIN", [])
        return []
    
    def get_different_provider_models(self) -> List[Dict[str, Any]]:
        """获取不同提供商的模型（排除当前使用的）"""
        return [
            m for m in self.models 
            if m.get("provider") != self.current_provider 
            and m.get("enabled", True)
        ]
    
    def get_same_provider_models(self) -> List[Dict[str, Any]]:
        """获取相同提供商的模型"""
        return [
            m for m in self.models 
            if m.get("provider") == self.current_provider 
            and m.get("enabled", True)
        ]
    
    def get_provider_distribution(self) -> Dict[str, List[Dict]]:
        """获取提供商分布"""
        providers = {}
        for model in self.get_different_provider_models():
            provider = model.get("provider", "unknown")
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(model)
        return providers
    
    def select_models_for_orchestration(
        self, 
        num_models: int = 3,
        prefer_different_provider: bool = True
    ) -> List[Dict[str, Any]]:
        """
        选择用于调度的模型
        
        优先级：
        1. 不同提供商的模型（优先）
        2. 同一提供商但不同的模型
        """
        if prefer_different_provider:
            # 优先选择不同提供商的模型
            different = self.get_different_provider_models()
            
            # 按优先级排序
            different.sort(key=lambda x: x.get("priority", 999))
            
            # 选择不同提供商的模型
            selected = []
            used_providers = set()
            
            for model in different:
                provider = model.get("provider")
                if provider not in used_providers:
                    selected.append(model)
                    used_providers.add(provider)
                    
                    if len(selected) >= num_models:
                        break
            
            # 如果还不够，从相同提供商补充
            if len(selected) < num_models:
                same = self.get_same_provider_models()
                same.sort(key=lambda x: x.get("priority", 999))
                for model in same:
                    if model not in selected:
                        selected.append(model)
                        if len(selected) >= num_models:
                            break
            
            return selected
        else:
            # 不区分提供商，按优先级选择
            all_enabled = [m for m in self.models if m.get("enabled", True)]
            all_enabled.sort(key=lambda x: x.get("priority", 999))
            return all_enabled[:num_models]
    
    def print_recommendations(self, num_models: int = 3):
        """打印推荐模型"""
        print("=" * 80)
        print("🎯 跨提供商调度器 - 模型推荐")
        print("=" * 80)
        
        print(f"\n📡 当前模型提供商: {self.current_provider}")
        print(f"🎬 推荐调度模型数量: {num_models}")
        
        # 推荐模型
        selected = self.select_models_for_orchestration(num_models)
        
        print(f"\n✅ 推荐模型（避免相同API接口）:")
        for i, model in enumerate(selected, 1):
            provider = model.get("provider", "unknown")
            is_different = provider != self.current_provider
            
            print(f"\n   {i}. {model.get('alias')}")
            print(f"      提供商: {provider}")
            print(f"      模型ID: {model.get('model_id')}")
            print(f"      优先级: {model.get('priority')}")
            print(f"      与当前API: {'✅ 不同' if is_different else '⚠️ 相同'}")
        
        # 提供商分布
        print("\n" + "=" * 80)
        print("📊 不同提供商可用模型")
        print("=" * 80)
        
        providers = self.get_provider_distribution()
        for provider, models in providers.items():
            print(f"\n🔌 {provider}: {len(models)}个模型")
            for m in models[:3]:
                print(f"   - {m.get('alias')}")
            if len(models) > 3:
                print(f"   ... 还有{len(models)-3}个")
        
        print("\n" + "=" * 80)
        print("调度建议")
        print("=" * 80)
        
        print(f"\n✅ 优先使用不同提供商的模型可以：")
        print(f"   1. 避免Rate Limiting")
        print(f"   2. 提高并发调用成功率")
        print(f"   3. 获得更好的模型多样性")
        
        print("\n" + "=" * 80)


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主程序"""
    orchestrator = CrossProviderOrchestrator()
    orchestrator.print_recommendations(num_models=3)


if __name__ == "__main__":
    main()
