
"""
序境系统 - 工部尚书苏云渺
统一抽象层设计 (Unified Abstraction Layer)

定义标准化模块接口规范，实现服务商接入标准化
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json


class ModelStatus(Enum):
    """模型状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"
    OUT_OF_CONTROL = "失控"
    UNKNOWN = "unknown"


class PaymentType(Enum):
    """缴费类型枚举"""
    MONTHLY = "包月"
    COUPON = "优惠券"
    QUOTA = "500次"
    TOTAL_QUOTA = "总调100次"
    UNKNOWN = "unknown"


@dataclass
class ModelConfig:
    """模型配置数据类"""
    id: str
    model_name: str
    model_identifier: str
    model_type: str
    provider: str
    api_url: str
    api_key: str
    usage_rules: str
    created_at: str
    updated_at: str
    is_locked: bool
    status: ModelStatus
    payment_type: PaymentType
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -&gt; 'ModelConfig':
        """从字典创建模型配置"""
        return cls(
            id=str(data.get('id', '')),
            model_name=data.get('模型名称', ''),
            model_identifier=data.get('模型标识符', ''),
            model_type=data.get('模型类型', ''),
            provider=data.get('服务商', ''),
            api_url=data.get('API地址', ''),
            api_key=data.get('API密钥', ''),
            usage_rules=data.get('使用规则', ''),
            created_at=str(data.get('创建时间', '')),
            updated_at=str(data.get('更新时间', '')),
            is_locked=data.get('本行记录锁定') == '是',
            status=ModelStatus(data.get('在线状态', 'unknown')),
            payment_type=PaymentType(data.get('缴费类型', 'unknown'))
        )
    
    def to_dict(self) -&gt; Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            '模型名称': self.model_name,
            '模型标识符': self.model_identifier,
            '模型类型': self.model_type,
            '服务商': self.provider,
            'API地址': self.api_url,
            'API密钥': self.api_key,
            '使用规则': self.usage_rules,
            '创建时间': self.created_at,
            '更新时间': self.updated_at,
            '本行记录锁定': '是' if self.is_locked else '否',
            '在线状态': self.status.value,
            '缴费类型': self.payment_type.value
        }


class BaseProviderAdapter(ABC):
    """服务商适配器基类 - 定义标准化接口"""
    
    @abstractmethod
    def get_name(self) -&gt; str:
        """获取服务商名称"""
        pass
    
    @abstractmethod
    def validate_api_config(self, api_url: str, api_key: str) -&gt; bool:
        """验证API配置"""
        pass
    
    @abstractmethod
    async def check_model_health(self, model_config: ModelConfig) -&gt; ModelStatus:
        """检查模型健康状态"""
        pass
    
    @abstractmethod
    def get_supported_models(self) -&gt; List[str]:
        """获取支持的模型列表"""
        pass
    
    @abstractmethod
    def normalize_api_response(self, raw_response: Any) -&gt; Dict[str, Any]:
        """标准化API响应格式"""
        pass


class ProviderRegistry:
    """服务商注册表 - 管理所有服务商适配器"""
    
    def __init__(self):
        self._adapters: Dict[str, BaseProviderAdapter] = {}
    
    def register(self, provider_name: str, adapter: BaseProviderAdapter):
        """注册服务商适配器"""
        self._adapters[provider_name] = adapter
    
    def get(self, provider_name: str) -&gt; Optional[BaseProviderAdapter]:
        """获取服务商适配器"""
        return self._adapters.get(provider_name)
    
    def list_providers(self) -&gt; List[str]:
        """列出所有已注册的服务商"""
        return list(self._adapters.keys())
    
    def has_provider(self, provider_name: str) -&gt; bool:
        """检查服务商是否已注册"""
        return provider_name in self._adapters


class UnifiedInterface:
    """统一接口 - 提供标准化的服务访问"""
    
    def __init__(self, provider_registry: ProviderRegistry):
        self.provider_registry = provider_registry
    
    def get_model_config(self, model_identifier: str) -&gt; Optional[ModelConfig]:
        """获取模型配置（将由数据库模块实现）"""
        return None
    
    async def check_health(self, model_config: ModelConfig) -&gt; ModelStatus:
        """统一健康检查接口"""
        adapter = self.provider_registry.get(model_config.provider)
        if adapter:
            return await adapter.check_model_health(model_config)
        return ModelStatus.UNKNOWN
    
    def validate_provider(self, provider_name: str) -&gt; bool:
        """验证服务商是否支持"""
        return self.provider_registry.has_provider(provider_name)


# 全局注册表实例
_provider_registry = ProviderRegistry()

def get_provider_registry() -&gt; ProviderRegistry:
    """获取全局服务商注册表"""
    return _provider_registry

