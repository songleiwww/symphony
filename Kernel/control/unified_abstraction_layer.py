"""
序境系统 - 统一抽象层设计
工部尚书苏云渺 · 阶段一P0任务

功能：
1. 定义标准化模块接口规范
2. 实现服务商接入标准化
3. 模型治理模块
"""

import sqlite3
import json
import abc
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class ModelStatus(Enum):
    """模型状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "失控"
    UNKNOWN = "unknown"


class ProviderType(Enum):
    """服务商类型枚举"""
    VOLC_ENGINE = "火山引擎"
    SILICON_FLOW = "硅基流动"
    NVIDIA = "英伟达"
    MODEL_SCOPE = "魔搭"
    MODEL_ARK = "魔力方舟"
    ZHIPU = "智谱"


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
    locked: str
    status: str
    payment_type: str

    @classmethod
    def from_db_row(cls, row):
        """从数据库行创建对象"""
        return cls(
            id=str(row.get('id', '')),
            model_name=row.get('模型名称', ''),
            model_identifier=row.get('模型标识符', ''),
            model_type=row.get('模型类型', ''),
            provider=row.get('服务商', ''),
            api_url=row.get('API地址', ''),
            api_key=row.get('API密钥', ''),
            usage_rules=row.get('使用规则', ''),
            created_at=str(row.get('创建时间', '')),
            updated_at=str(row.get('更新时间', '')),
            locked=row.get('本行记录锁定', '否'),
            status=row.get('在线状态', 'unknown'),
            payment_type=row.get('缴费类型', '')
        )

    def to_dict(self):
        """转换为字典"""
        return asdict(self)


class IProviderAdapter(abc.ABC):
    """服务商适配器接口 - 标准化模块接口规范"""
    
    @abc.abstractmethod
    def get_provider_name(self):
        """获取服务商名称"""
        pass

    @abc.abstractmethod
    def validate_config(self, config):
        """验证模型配置"""
        pass

    @abc.abstractmethod
    def check_health(self, config):
        """检查模型健康状态"""
        pass

    @abc.abstractmethod
    def normalize_api_url(self, url):
        """标准化API地址"""
        pass


class BaseProviderAdapter(IProviderAdapter):
    """基础服务商适配器 - 提供通用实现"""
    
    def __init__(self, provider_name):
        self.provider_name = provider_name

    def get_provider_name(self):
        return self.provider_name

    def validate_config(self, config):
        """基础验证逻辑"""
        if not config.api_url or not config.api_key:
            return False
        return True

    def check_health(self, config):
        """基础健康检查（子类可覆盖）"""
        # 默认返回在线状态
        is_healthy = config.status == ModelStatus.ONLINE.value
        message = "Healthy" if is_healthy else "Unhealthy"
        return is_healthy, message

    def normalize_api_url(self, url):
        """标准化API地址"""
        url = url.strip()
        if not url.endswith('/'):
            url += '/'
        return url


class VolcEngineAdapter(BaseProviderAdapter):
    """火山引擎适配器"""
    
    def __init__(self):
        super().__init__("火山引擎")

    def normalize_api_url(self, url):
        """火山引擎特定的URL标准化"""
        url = super().normalize_api_url(url)
        if 'volces.com' in url:
            return url
        return url


class SiliconFlowAdapter(BaseProviderAdapter):
    """硅基流动适配器"""
    
    def __init__(self):
        super().__init__("硅基流动")


class NvidiaAdapter(BaseProviderAdapter):
    """英伟达适配器"""
    
    def __init__(self):
        super().__init__("英伟达")


class ModelScopeAdapter(BaseProviderAdapter):
    """魔搭适配器"""
    
    def __init__(self):
        super().__init__("魔搭")


class ModelArkAdapter(BaseProviderAdapter):
    """魔力方舟适配器"""
    
    def __init__(self):
        super().__init__("魔力方舟")


class ZhipuAdapter(BaseProviderAdapter):
    """智谱适配器"""
    
    def __init__(self):
        super().__init__("智谱")


class ProviderRegistry:
    """服务商注册表 - 实现服务商接入标准化"""
    
    def __init__(self):
        self._adapters = {}
        self._register_defaults()

    def _register_defaults(self):
        """注册默认服务商适配器"""
        self.register(VolcEngineAdapter())
        self.register(SiliconFlowAdapter())
        self.register(NvidiaAdapter())
        self.register(ModelScopeAdapter())
        self.register(ModelArkAdapter())
        self.register(ZhipuAdapter())

    def register(self, adapter):
        """注册服务商适配器"""
        self._adapters[adapter.get_provider_name()] = adapter

    def get(self, provider_name):
        """获取服务商适配器"""
        return self._adapters.get(provider_name)

    def list_providers(self):
        """列出所有已注册的服务商"""
        return list(self._adapters.keys())


class ModelGovernance:
    """模型治理模块 - 阶段一P0任务2"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.provider_registry = ProviderRegistry()

    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_models(self):
        """获取所有模型配置"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM 模型配置表;")
            rows = cursor.fetchall()
            
            models = []
            for row in rows:
                model = ModelConfig.from_db_row(dict(row))
                models.append(model)
            
            return models
        finally:
            conn.close()

    def get_models_by_provider(self, provider):
        """按服务商获取模型"""
        all_models = self.get_all_models()
        return [m for m in all_models if m.provider == provider]

    def get_models_by_status(self, status):
        """按状态获取模型"""
        all_models = self.get_all_models()
        return [m for m in all_models if m.status == status]

    def get_status_statistics(self):
        """统计各服务商模型在线状态"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 服务商, 在线状态, COUNT(*) as 数量 
                FROM 模型配置表 
                GROUP BY 服务商, 在线状态
                ORDER BY 服务商, 在线状态;
            """)
            
            stats = {}
            for row in cursor.fetchall():
                provider = row['服务商']
                status = row['在线状态']
                count = row['数量']
                
                if provider not in stats:
                    stats[provider] = {}
                stats[provider][status] = count
            
            return stats
        finally:
            conn.close()

    def get_summary(self):
        """获取治理摘要"""
        all_models = self.get_all_models()
        stats = self.get_status_statistics()
        
        total_models = len(all_models)
        online_count = len([m for m in all_models if m.status == ModelStatus.ONLINE.value])
        offline_count = len([m for m in all_models if m.status == ModelStatus.OFFLINE.value])
        error_count = len([m for m in all_models if m.status == ModelStatus.ERROR.value])
        
        return {
            "total_models": total_models,
            "online_count": online_count,
            "offline_count": offline_count,
            "error_count": error_count,
            "providers": self.provider_registry.list_providers(),
            "detailed_stats": stats,
            "online_rate": round(online_count / total_models * 100, 2) if total_models > 0 else 0
        }


class UnifiedAbstractionLayer:
    """统一抽象层 - 对外统一接口"""
    
    def __init__(self, db_path):
        self.model_governance = ModelGovernance(db_path)
        self.provider_registry = ProviderRegistry()

    def initialize(self):
        """初始化统一抽象层"""
        summary = self.model_governance.get_summary()
        return {
            "status": "initialized",
            "providers": self.provider_registry.list_providers(),
            "model_summary": summary
        }

    def get_system_status(self):
        """获取系统状态"""
        return {
            "abstraction_layer": "active",
            "model_governance": "active",
            "provider_registry": "active",
            "summary": self.model_governance.get_summary()
        }


# 主函数 - 演示使用
def main():
    print("=" * 80)
    print("序境系统 - 统一抽象层设计 · 工部尚书苏云渺")
    print("=" * 80)
    
    db_path = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db"
    
    # 初始化统一抽象层
    ual = UnifiedAbstractionLayer(db_path)
    result = ual.initialize()
    
    print(f"\n✅ 统一抽象层初始化完成")
    print(f"\n📊 系统状态:")
    summary = result['model_summary']
    print(f"   - 总模型数: {summary['total_models']}")
    print(f"   - 在线: {summary['online_count']}")
    print(f"   - 离线: {summary['offline_count']}")
    print(f"   - 异常: {summary['error_count']}")
    print(f"   - 在线率: {summary['online_rate']}%")
    
    print(f"\n🏢 已注册服务商:")
    for provider in result['providers']:
        print(f"   - {provider}")
    
    print(f"\n📈 详细统计:")
    for provider, statuses in summary['detailed_stats'].items():
        print(f"\n   {provider}:")
        for status, count in statuses.items():
            print(f"     - {status}: {count}")
    
    print("\n" + "=" * 80)
    print("✅ 阶段一P0任务完成")
    print("   - 任务1：统一抽象层设计 ✓")
    print("   - 任务2：模型治理模块 ✓")
    print("=" * 80)
    
    return {
        "已完成": ["任务1：统一抽象层设计", "任务2：模型治理模块"],
        "进行中": [],
        "系统状态": ual.get_system_status()
    }


if __name__ == "__main__":
    main()
