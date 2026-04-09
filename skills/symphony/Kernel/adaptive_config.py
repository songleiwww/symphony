# -*- coding: utf-8 -*-
"""
AdaptiveConfig - 自适应配置管理系统
======================================
所有变量皆可配置 + 变更自动检测 + 故障自动适应

核心原则：
- 配置与代码分离
- 所有变量皆可配置
- 变更自动检测
- 故障自动切换

变量清单（全部可配置）：
1. API Keys - 可能过期/变更
2. 模型列表 - 可能下线/新增
3. 服务商端点 - 可能变化
4. 超时/重试策略
5. Token 预算
6. 熔断阈值
"""

import os
import json
import time
import sqlite3
import threading
import requests
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'


class ConfigChangeType(Enum):
    """配置变更类型"""
    API_KEY_EXPIRED = "api_key_expired"
    MODEL_OFFLINE = "model_offline"
    QUOTA_EXCEEDED = "quota_exceeded"
    NETWORK_ERROR = "network_error"
    CONFIG_UPDATED = "config_updated"
    USER_SWITCHED = "user_switched"  # 用户主动切换
    QUOTA_WARNING = "quota_warning"  # 额度即将用完
    COST_EXCEEDED = "cost_exceeded"  # 超出成本预算


@dataclass
class ConfigVar:
    """配置变量 - 任意类型皆可"""
    key: str
    value: Any
    var_type: str  # "str", "int", "float", "bool", "json", "secret"
    description: str = ""
    last_verified: float = 0
    verify_interval: int = 300  # 5分钟验证一次
    is_stale: bool = False  # 是否过期
    on_change_callback: Callable = None  # 变更回调
    
    def needs_verify(self) -> bool:
        """是否需要重新验证"""
        return time.time() - self.last_verified > self.verify_interval


class AdaptiveConfigManager:
    """
    自适应配置管理器
    
    功能：
    - 所有变量统一存储在 symphony.db
    - 支持 secret 类型（自动掩码）
    - 变更检测 + 自动回调
    - 定时健康检查
    - 配置版本管理
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._cache: Dict[str, ConfigVar] = {}
        self._lock = threading.RLock()
        self._change_listeners: List[Callable] = []
        self._init_db()
        self._start_health_checker()
    
    def _init_db(self):
        """初始化配置表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS adaptive_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                var_type TEXT DEFAULT 'str',
                description TEXT DEFAULT '',
                last_verified REAL DEFAULT 0,
                verify_interval INTEGER DEFAULT 300,
                created_at REAL DEFAULT 0,
                updated_at REAL DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT,
                old_value TEXT,
                new_value TEXT,
                changed_at REAL,
                reason TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def set(self, key: str, value: Any, var_type: str = "str", 
            description: str = "", verify_interval: int = 300,
            on_change: Callable = None) -> bool:
        """
        设置配置变量
        
        Args:
            key: 配置键
            value: 配置值
            var_type: 类型 (str/int/float/bool/json/secret)
            description: 描述
            verify_interval: 验证间隔(秒)
            on_change: 变更回调函数
        """
        with self._lock:
            # 获取旧值（不自动验证）
            old_value = self.get(key, auto_verify=False)
            
            # 序列化值
            if var_type == "json":
                value_str = json.dumps(value, ensure_ascii=False)
            elif var_type == "secret":
                value_str = self._mask_secret(str(value))
            else:
                value_str = str(value)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO adaptive_config (key, value, var_type, description, 
                    verify_interval, last_verified, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    var_type = excluded.var_type,
                    description = excluded.description,
                    verify_interval = excluded.verify_interval,
                    updated_at = excluded.updated_at
            """, (key, value_str, var_type, description, verify_interval, 
                  time.time(), time.time(), time.time()))
            
            conn.commit()
            conn.close()
            
            # 更新缓存
            self._cache[key] = ConfigVar(
                key=key, value=value, var_type=var_type,
                description=description, verify_interval=verify_interval,
                last_verified=time.time(),
                on_change_callback=on_change
            )
            
            # 检测变更
            if old_value != value and old_value is not None:
                self._notify_change(key, old_value, value)
            
            return True
    
    def get(self, key: str, default: Any = None, auto_verify: bool = True) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            auto_verify: 是否自动验证（检查是否过期）
        """
        var = self._get_from_cache(key)
        
        if var is None:
            var = self._load_from_db(key)
        
        if var is None:
            return default
        
        # 自动验证
        if auto_verify and var.needs_verify():
            self._verify_and_refresh(key, var)
        
        return var.value
    
    def get_masked(self, key: str) -> str:
        """获取掩码后的值（用于日志）"""
        var = self._get_from_cache(key) or self._load_from_db(key)
        if var is None:
            return None
        if var.var_type == "secret":
            return var.value
        return self._mask_secret(str(var.value))
    
    def _get_from_cache(self, key: str) -> Optional[ConfigVar]:
        """从缓存获取"""
        with self._lock:
            return self._cache.get(key)
    
    def _load_from_db(self, key: str) -> Optional[ConfigVar]:
        """从数据库加载"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value, var_type, description, verify_interval, last_verified FROM adaptive_config WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        value_str, var_type, description, verify_interval, last_verified = row
        
        # 反序列化值
        if var_type == "json":
            value = json.loads(value_str)
        elif var_type == "int":
            value = int(value_str)
        elif var_type == "float":
            value = float(value_str)
        elif var_type == "bool":
            value = value_str.lower() in ("true", "1", "yes")
        else:
            value = value_str
        
        var = ConfigVar(
            key=key, value=value, var_type=var_type,
            description=description, verify_interval=verify_interval,
            last_verified=last_verified
        )
        
        with self._lock:
            self._cache[key] = var
        
        return var
    
    def _verify_and_refresh(self, key: str, var: ConfigVar):
        """验证并刷新配置"""
        try:
            # 调用验证函数
            is_valid = self._validate(key, var)
            
            with self._lock:
                var.last_verified = time.time()
                var.is_stale = not is_valid
            
            if not is_valid:
                print(f"[AdaptiveConfig] {key} 验证失败，标记为过期")
                self._notify_change(key, var.value, None, ConfigChangeType.MODEL_OFFLINE)
                
        except Exception as e:
            print(f"[AdaptiveConfig] {key} 验证异常: {e}")
            var.is_stale = True
    
    def _validate(self, key: str, var: ConfigVar) -> bool:
        """验证配置有效性"""
        # API Key 验证
        if key.startswith("api_key_"):
            return self._validate_api_key(var.value)
        
        # 模型验证
        if key.startswith("model_"):
            return self._validate_model(key, var.value)
        
        return True
    
    def _validate_api_key(self, key: str) -> bool:
        """验证 API Key 是否有效"""
        if not key:
            return False
        
        try:
            # 简单测试调用
            resp = requests.get("https://api.github.com", timeout=5)
            return True  # 如果能访问网络，认为 key 可能有效
        except:
            return True  # 网络问题不认为 key 失效
    
    def _validate_model(self, key: str, model_id: str) -> bool:
        """验证模型是否可用"""
        # 实际应该调用模型检测
        return True
    
    def _notify_change(self, key: str, old_value: Any, new_value: Any, 
                      change_type: ConfigChangeType = ConfigChangeType.CONFIG_UPDATED):
        """通知配置变更"""
        # 记录版本
        self._record_version(key, old_value, new_value)
        
        # 触发监听器
        for listener in self._change_listeners:
            try:
                listener(key, old_value, new_value, change_type)
            except Exception as e:
                print(f"[AdaptiveConfig] 监听器异常: {e}")
    
    def _record_version(self, key: str, old_value: Any, new_value: Any):
        """记录配置版本"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO config_versions (config_key, old_value, new_value, changed_at)
            VALUES (?, ?, ?, ?)
        """, (key, str(old_value)[:500], str(new_value)[:500], time.time()))
        conn.commit()
        conn.close()
    
    def _mask_secret(self, value: str) -> str:
        """掩码敏感信息"""
        if len(value) <= 8:
            return "***"
        return value[:4] + "***" + value[-4:]
    
    def on_change(self, listener: Callable):
        """注册配置变更监听器"""
        self._change_listeners.append(listener)
    
    def _start_health_checker(self):
        """启动健康检查线程"""
        def checker():
            while True:
                time.sleep(60)  # 每分钟检查一次
                self._health_check()
        
        thread = threading.Thread(target=checker, daemon=True)
        thread.start()
    
    def _health_check(self):
        """健康检查所有配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key FROM adaptive_config")
        
        for row in cursor.fetchall():
            key = row[0]
            var = self._get_from_cache(key)
            if var and var.needs_verify():
                self._verify_and_refresh(key, var)
        
        conn.close()
    
    def get_all_keys(self) -> List[str]:
        """获取所有配置键"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key FROM adaptive_config")
        keys = [row[0] for row in cursor.fetchall()]
        conn.close()
        return keys
    
    def diff(self, key1: str, key2: str) -> Dict:
        """对比两个配置"""
        v1 = self.get(key1)
        v2 = self.get(key2)
        return {
            "key1": {"key": key1, "value": v1, "type": type(v1).__name__},
            "key2": {"key": key2, "value": v2, "type": type(v2).__name__},
            "same": v1 == v2
        }


class AdaptiveProvider:
    """
    自适应提供商 - 封装 API 调用
    自动处理：
    - Key 过期切换
    - 模型降级
    - 超时重试
    - 熔断
    """
    
    def __init__(self, provider_name: str, config_manager: AdaptiveConfigManager = None):
        self.provider_name = provider_name
        self.config = config_manager or AdaptiveConfigManager()
        self.current_key_index = 0
        self.api_keys: List[str] = []
        self.models: List[str] = []
        self._load_config()
    
    def _load_config(self):
        """从配置管理器加载"""
        self.api_keys = self.config.get(f"api_keys_{self.provider_name}", [])
        self.models = self.config.get(f"models_{self.provider_name}", [])
    
    def get_api_key(self) -> Optional[str]:
        """获取当前有效的 API Key"""
        if not self.api_keys:
            return None
        
        # 如果当前 key 过期，尝试下一个
        for i in range(len(self.api_keys)):
            index = (self.current_key_index + i) % len(self.api_keys)
            key = self.api_keys[index]
            if self._is_key_valid(key):
                self.current_key_index = index
                return key
        
        return None
    
    def _is_key_valid(self, key: str) -> bool:
        """检查 key 是否有效"""
        # 实际应该验证
        return bool(key)
    
    def get_best_model(self, task_type: str = "chat") -> Optional[str]:
        """获取最佳模型"""
        if not self.models:
            return None
        # 实际应该根据延迟、成功率选择
        return self.models[0] if self.models else None
    
    def call(self, prompt: str, **kwargs) -> Dict:
        """执行调用 - 自适应重试和降级"""
        max_retries = kwargs.pop("max_retries", 3)
        
        last_error = None
        for attempt in range(max_retries):
            try:
                api_key = self.get_api_key()
                if not api_key:
                    return {"error": "No valid API key"}
                
                model = self.get_best_model()
                if not model:
                    return {"error": "No available model"}
                
                return self._do_call(api_key, model, prompt, **kwargs)
                
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"[{self.provider_name}] 调用失败，重试 {attempt + 1}/{max_retries}")
                    time.sleep(2 ** attempt)  # 指数退避
        
        return {"error": str(last_error)}
    
    def _do_call(self, api_key: str, model: str, prompt: str, **kwargs) -> Dict:
        """实际执行调用 - 子类实现"""
        raise NotImplementedError


# 全局单例
_global_config_manager: Optional[AdaptiveConfigManager] = None


def get_config_manager() -> AdaptiveConfigManager:
    """获取全局配置管理器"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = AdaptiveConfigManager()
    return _global_config_manager


# 预置配置键
class ConfigKeys:
    """常用配置键"""
    # API Keys
    API_KEY_ALIYUN = "api_key_aliyun"
    API_KEY_MINIMAX = "api_key_minimax"
    API_KEY_ZHIPU = "api_key_zhipu"
    API_KEY_NVIDIA = "api_key_nvidia"
    
    # Providers
    PROVIDER_PRIMARY = "provider_primary"
    PROVIDER_FALLBACK = "provider_fallback"
    
    # Models
    MODEL_TTS = "model_tts"
    MODEL_ASR = "model_asr"
    MODEL_CHAT = "model_chat"
    MODEL_CODE = "model_code"
    MODEL_VISION = "model_vision"
    
    # Limits
    MAX_TOKENS_PER_STEP = "max_tokens_per_step"
    MAX_TOTAL_TOKENS = "max_total_tokens"
    TIMEOUT_PER_STEP = "timeout_per_step"
    
    # Feishu
    FEISHU_APP_ID = "feishu_app_id"
    FEISHU_APP_SECRET = "feishu_app_secret"
    FEISHU_USER_OPEN_ID = "feishu_user_open_id"


class ModelQuotaTracker:
    """
    模型额度追踪器
    
    功能：
    - 记录每个模型的使用次数/Token
    - 设置额度上限（用户可配置）
    - 额度警告（80%时提醒）
    - 额度用完自动切换
    """
    
    # 模型额度表（可配置）
    DEFAULT_QUOTAS = {
        # 免费模型
        'edge_tts': {'limit': float('inf'), 'type': 'unlimited'},
        'whisper': {'limit': float('inf'), 'type': 'unlimited'},
        
        # 有次数限制的模型
        'sambert-zhinan-v1': {'limit': 10000, 'type': 'minutes'},  # TTS分钟数
        'qwen-plus': {'limit': 1000000, 'type': 'tokens'},  # Token数
        'glm-4': {'limit': 500000, 'type': 'tokens'},
        'MiniMax-Text-01': {'limit': 1000000, 'type': 'tokens'},
    }
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()
        self._quota_cache = {}
    
    def _init_db(self):
        """初始化额度表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_quotas (
                model_id TEXT PRIMARY KEY,
                usage_count INTEGER DEFAULT 0,
                usage_tokens INTEGER DEFAULT 0,
                quota_limit REAL DEFAULT 0,
                quota_type TEXT DEFAULT 'unlimited',
                last_used REAL DEFAULT 0,
                updated_at REAL DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_preferences (
                user_id TEXT,
                model_id TEXT,
                priority INTEGER DEFAULT 0,
                use_count INTEGER DEFAULT 0,
                last_used REAL DEFAULT 0,
                PRIMARY KEY (user_id, model_id)
            )
        """)
        conn.commit()
        conn.close()
    
    def get_quota(self, model_id: str) -> Dict:
        """获取模型额度信息"""
        if model_id in self._quota_cache:
            return self._quota_cache[model_id]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT usage_count, usage_tokens, quota_limit, quota_type
            FROM model_quotas WHERE model_id = ?
        """, (model_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            quota = {
                'usage_count': row[0],
                'usage_tokens': row[1],
                'limit': row[2],
                'type': row[3],
                'remaining': row[2] - row[0] if row[2] else float('inf')
            }
        else:
            # 使用默认额度
            default = self.DEFAULT_QUOTAS.get(model_id, {'limit': float('inf'), 'type': 'unlimited'})
            quota = {
                'usage_count': 0,
                'usage_tokens': 0,
                'limit': default['limit'],
                'type': default['type'],
                'remaining': default['limit']
            }
        
        self._quota_cache[model_id] = quota
        return quota
    
    def is_available(self, model_id: str) -> bool:
        """检查模型是否还有额度"""
        quota = self.get_quota(model_id)
        if quota['type'] == 'unlimited':
            return True
        return quota['remaining'] > 0
    
    def get_usage_percent(self, model_id: str) -> float:
        """获取使用百分比"""
        quota = self.get_quota(model_id)
        if quota['limit'] == float('inf'):
            return 0.0
        return (quota['usage_count'] / quota['limit']) * 100
    
    def record_usage(self, model_id: str, tokens: int = 0, count: int = 1):
        """记录模型使用"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 更新或插入
        cursor.execute("""
            INSERT INTO model_quotas (model_id, usage_count, usage_tokens, quota_limit, quota_type, last_used, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(model_id) DO UPDATE SET
                usage_count = usage_count + excluded.usage_count,
                usage_tokens = usage_tokens + excluded.usage_tokens,
                last_used = excluded.last_used,
                updated_at = excluded.updated_at
        """, (model_id, count, tokens, 
               self.DEFAULT_QUOTAS.get(model_id, {}).get('limit', float('inf')),
               self.DEFAULT_QUOTAS.get(model_id, {}).get('type', 'unlimited'),
               time.time(), time.time()))
        
        conn.commit()
        conn.close()
        
        # 清除缓存
        if model_id in self._quota_cache:
            del self._quota_cache[model_id]
    
    def check_and_switch(self, model_id: str, fallback_model: str) -> str:
        """
        检查额度，不够则切换
        返回实际使用的模型
        """
        if self.is_available(model_id):
            # 检查是否需要警告
            percent = self.get_usage_percent(model_id)
            if percent >= 80:
                print(f'[QuotaTracker] {model_id} 使用率已达 {percent:.1f}%，建议切换')
            return model_id
        
        # 额度用完，切换到备选
        print(f'[QuotaTracker] {model_id} 额度用完，切换到 {fallback_model}')
        return fallback_model
    
    def set_user_preference(self, user_id: str, model_id: str, priority: int = 0):
        """设置用户模型偏好"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO model_preferences (user_id, model_id, priority, use_count, last_used)
            VALUES (?, ?, ?, 0, ?)
            ON CONFLICT(user_id, model_id) DO UPDATE SET
                priority = excluded.priority,
                last_used = excluded.last_used
        """, (user_id, model_id, priority, time.time()))
        conn.commit()
        conn.close()
    
    def get_user_preferred_model(self, user_id: str, task_type: str = 'chat') -> Optional[str]:
        """获取用户偏好的模型"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT model_id FROM model_preferences
            WHERE user_id = ? AND priority > 0
            ORDER BY priority DESC, last_used DESC
            LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    
    def record_user_switch(self, user_id: str, model_id: str):
        """记录用户切换模型"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO model_preferences (user_id, model_id, use_count, last_used)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(user_id, model_id) DO UPDATE SET
                use_count = use_count + 1,
                last_used = excluded.last_used
        """, (user_id, model_id, time.time()))
        conn.commit()
        conn.close()


# 全局单例
_global_quota_tracker: Optional[ModelQuotaTracker] = None


def get_quota_tracker() -> ModelQuotaTracker:
    """获取全局额度追踪器"""
    global _global_quota_tracker
    if _global_quota_tracker is None:
        _global_quota_tracker = ModelQuotaTracker()
    return _global_quota_tracker


__all__ = [
    'AdaptiveConfigManager',
    'AdaptiveProvider',
    'ConfigVar',
    'ConfigKeys',
    'ConfigChangeType',
    'ModelQuotaTracker',
    'get_config_manager',
    'get_quota_tracker'
]
