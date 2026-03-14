#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一配置管理器 - 从 config.py 读取所有模型配置
Unified Config Manager - Read all model config from config.py
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
    print("⚠️  config.py 不可用，使用默认配置")


# =============================================================================
# 统一配置管理器
# =============================================================================

class UnifiedConfigManager:
    """统一配置管理器"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if CONFIG_AVAILABLE:
            return {
                "models": getattr(config, "MODEL_CHAIN", []),
                "circuit_breaker": getattr(config, "CIRCUIT_BREAKER_CONFIG", {}),
                "retry": getattr(config, "RETRY_CONFIG", {}),
                "health_check": getattr(config, "HEALTH_CHECK_CONFIG", {}),
                "logging": getattr(config, "LOGGING_CONFIG", {}),
                "symphony": getattr(config, "SYMPHONY_CONFIG", {})
            }
        else:
            # 默认配置
            return {
                "models": [],
                "circuit_breaker": {},
                "retry": {},
                "health_check": {},
                "logging": {},
                "symphony": {}
            }
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """获取所有模型"""
        return self.config.get("models", [])
    
    def get_enabled_models(self) -> List[Dict[str, Any]]:
        """获取已启用的模型"""
        return [m for m in self.get_all_models() if m.get("enabled", True)]
    
    def get_model_by_alias(self, alias: str) -> Optional[Dict[str, Any]]:
        """通过别名获取模型"""
        for model in self.get_all_models():
            if model.get("alias") == alias:
                return model
        return None
    
    def get_model_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """通过名称获取模型"""
        for model in self.get_all_models():
            if model.get("name") == name:
                return model
        return None
    
    def get_models_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """按提供商获取模型"""
        return [m for m in self.get_all_models() if m.get("provider") == provider]
    
    def get_models_by_priority(self, min_priority: int = 1, max_priority: int = 100) -> List[Dict[str, Any]]:
        """按优先级获取模型"""
        return [
            m for m in self.get_all_models()
            if min_priority <= m.get("priority", 999) <= max_priority
        ]
    
    def get_providers(self) -> List[str]:
        """获取所有提供商"""
        providers = set()
        for model in self.get_all_models():
            provider = model.get("provider")
            if provider:
                providers.add(provider)
        return sorted(list(providers))
    
    def get_model_count(self) -> Dict[str, int]:
        """获取模型统计"""
        all_models = self.get_all_models()
        enabled_models = self.get_enabled_models()
        
        provider_counts = {}
        for model in all_models:
            provider = model.get("provider", "unknown")
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        return {
            "total": len(all_models),
            "enabled": len(enabled_models),
            "disabled": len(all_models) - len(enabled_models),
            "providers": provider_counts
        }
    
    def print_summary(self):
        """打印配置摘要"""
        print("=" * 80)
        print("📊 统一配置管理器 - 摘要")
        print("=" * 80)
        
        counts = self.get_model_count()
        
        print(f"\n📦 总模型数: {counts['total']}")
        print(f"✅ 已启用: {counts['enabled']}")
        print(f"❌ 已禁用: {counts['disabled']}")
        
        print(f"\n🔌 提供商分布:")
        for provider, count in counts['providers'].items():
            print(f"   - {provider}: {count}个")
        
        print(f"\n🎯 已启用模型列表:")
        for i, model in enumerate(self.get_enabled_models()[:10], 1):
            print(f"   {i}. {model.get('alias')} ({model.get('provider')})")
        
        if len(self.get_enabled_models()) > 10:
            print(f"   ... 还有 {len(self.get_enabled_models()) - 10} 个模型")
        
        print("\n" + "=" * 80)
        print("配置加载完成！")
        print("=" * 80)


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主程序"""
    manager = UnifiedConfigManager()
    manager.print_summary()


if __name__ == "__main__":
    main()
