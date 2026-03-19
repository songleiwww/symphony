#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统v3.3.0 - 多模型协调器
MultiModelCoordinator: 检测在线 → 准备模型 → 调度执行
遵循序境总则第32条: 数据库优先，定期同步，禁止固化记忆
"""
import sqlite3
import time
import asyncio
import json
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import httpx

class ModelStatus(Enum):
    """模型状态"""
    UNKNOWN = "unknown"
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"

@dataclass
class ModelInfo:
    """模型信息"""
    id: int
    name: str
    api_address: str
    api_key: str
    provider: str
    status: ModelStatus = ModelStatus.UNKNOWN
    last_check: Optional[str] = None
    latency: float = 0.0
    error_msg: Optional[str] = None

@dataclass
class CoordinatorConfig:
    """协调器配置"""
    timeout: float = 5.0           # 检测超时秒数
    max_retries: int = 2            # 最大重试次数
    cache_ttl: int = 300            # 缓存TTL秒数
    min_online_models: int = 1      # 最少需要在线模型数


class ModelOnlineDetector:
    """模型在线检测器
    
    遵循序境总则第32条:
    1. 数据库优先 - 每次从数据库读取模型配置
    2. 定期同步 - 状态缓存有TTL，过期自动刷新
    3. 禁止固化 - 不长期固化配置，每次从数据库加载
    """
    
    def __init__(self, db_path: str, config: CoordinatorConfig = None):
        self.db_path = db_path
        self.config = config or CoordinatorConfig()
        # 状态缓存(仅用于状态，配置始终从数据库读取)
        self.status_cache: Dict[int, Dict] = {}
    
    def get_models_by_provider(self, provider: str) -> List[ModelInfo]:
        """获取指定服务商的所有模型
        数据库优先: 每次都从数据库重新读取，不缓存配置
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT id, 模型名称, API地址, API密钥, 服务商
            FROM 模型配置表
            WHERE 服务商 = ?
            ORDER BY id
        """, (provider,))
        
        models = []
        for row in c.fetchall():
            models.append(ModelInfo(
                id=row[0],
                name=row[1],
                api_address=row[2],
                api_key=row[3],
                provider=row[4]
            ))
        
        conn.close()
        return models
    
    def check_model_online(self, model: ModelInfo) -> ModelInfo:
        """检测单个模型是否在线"""
        # 检查状态缓存
        cache_key = model.id
        if cache_key in self.status_cache:
            cached = self.status_cache[cache_key]
            cache_time = cached.get('timestamp', 0)
            if time.time() - cache_time < self.config.cache_ttl:
                model.status = cached['status']
                model.last_check = cached.get('last_check')
                model.latency = cached.get('latency', 0)
                return model
        
        # 实际检测
        start_time = time.time()
        try:
            # 构造简单的health check请求
            api_base = model.api_address.rstrip('/')
            if '/v1/' in api_base:
                health_url = api_base.replace('/v1/chat/completions', '/v1/models')
            else:
                health_url = api_base + '/v1/models'
            
            headers = {
                'Authorization': f'Bearer {model.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = httpx.get(
                health_url, 
                headers=headers, 
                timeout=self.config.timeout
            )
            
            model.latency = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                model.status = ModelStatus.ONLINE
                model.last_check = datetime.now().isoformat()
            else:
                model.status = ModelStatus.OFFLINE
                model.error_msg = f"HTTP {response.status_code}"
                
        except asyncio.TimeoutError:
            model.status = ModelStatus.ERROR
            model.error_msg = "Timeout"
        except Exception as e:
            model.status = ModelStatus.ERROR
            model.error_msg = str(e)
        
        # 更新状态缓存(仅缓存状态，不缓存配置)
        self.status_cache[cache_key] = {
            'status': model.status,
            'last_check': model.last_check,
            'latency': model.latency,
            'timestamp': time.time()
        }
        
        return model
    
    def detect_provider_models(self, provider: str) -> List[ModelInfo]:
        """检测指定服务商的所有模型在线状态"""
        models = self.get_models_by_provider(provider)
        online_models = []
        
        for model in models:
            checked = self.check_model_online(model)
            if checked.status == ModelStatus.ONLINE:
                online_models.append(checked)
        
        return online_models
    
    def get_all_providers(self) -> List[str]:
        """获取所有服务商列表"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT DISTINCT 服务商 FROM 模型配置表")
        providers = [row[0] for row in c.fetchall()]
        conn.close()
        return providers


class ModelPreparer:
    """模型准备器
    
    遵循序境总则第32条:
    - 不固化预热模型，每次调度重新验证
    - 保留最近成功预热记录以优化性能
    """
    
    def __init__(self, detector: ModelOnlineDetector):
        self.detector = detector
        # 仅缓存最近成功的预热记录，不保留完整配置
        # 完整配置始终从数据库读取
        self.warmed_cache: Dict[str, Dict] = {}
    
    def prepare_models(self, provider: str, count: int = 2) -> List[ModelInfo]:
        """准备模型 - 预热并验证"""
        # 先检测在线模型
        online_models = self.detector.detect_provider_models(provider)
        
        if not online_models:
            return []
        
        # 选择延迟最低的模型
        sorted_models = sorted(online_models, key=lambda m: m.latency)
        
        # 预热前N个模型
        prepared = []
        for model in sorted_models[:count]:
            warmed = self._warm_model(model)
            if warmed:
                prepared.append(warmed)
                # 只缓存预热成功状态，配置仍然从数据库读取
                self.warmed_cache[f"{provider}_{model.id}"] = {
                    "model_id": model.id,
                    "last_success": time.time(),
                    "latency": model.latency
                }
        
        return prepared
    
    def _warm_model(self, model: ModelInfo) -> Optional[ModelInfo]:
        """预热模型 - 发送简单请求验证"""
        try:
            api_base = model.api_address.rstrip('/')
            
            # 根据不同API构造请求
            if 'nvidia' in api_base.lower():
                # 英伟达API
                payload = {
                    "model": "meta/llama-3.1-8b-instruct",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                }
            elif 'volces' in api_base.lower():
                # 火山引擎
                payload = {
                    "model": "doubao-lite-4k",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                }
            elif 'bigmodel' in api_base.lower():
                # 智谱
                payload = {
                    "model": "glm-4-flash",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                }
            elif 'siliconflow' in api_base.lower():
                # 硅基流动
                payload = {
                    "model": "Qwen/Qwen2-7B-Instruct",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                }
            elif 'modelscope' in api_base.lower():
                # 魔搭
                payload = {
                    "model": "qwen/Qwen2-7B-Instruct",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                }
            else:
                # 默认
                payload = {
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                }
            
            headers = {
                'Authorization': f'Bearer {model.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = httpx.post(
                f"{api_base}/chat/completions",
                json=payload,
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code in (200, 201):
                model.status = ModelStatus.ONLINE
                return model
            else:
                model.error_msg = f"HTTP {response.status_code}"
                return None
                
        except Exception as e:
            model.error_msg = str(e)
            return None
    
    def get_warmed_model(self, provider: str, model_id: int = None) -> Optional[ModelInfo]:
        """获取已预热的模型
        
        数据库优先: 即使有缓存，也从数据库重新读取配置
        只使用缓存的状态信息优化检测顺序
        """
        if not model_id:
            # 找该服务商最近成功的模型
            candidates = [
                (k, v) for k, v in self.warmed_cache.items()
                if k.startswith(f"{provider}_")
            ]
            if not candidates:
                return None
            # 选最近成功的
            candidates.sort(key=lambda x: x[1]["last_success"], reverse=True)
            model_id = candidates[0][1]["model_id"]
        
        # 数据库优先: 从数据库重新读取配置
        models = self.detector.get_models_by_provider(provider)
        for model in models:
            if model.id == model_id:
                # 重新验证在线状态
                checked = self.detector.check_model_online(model)
                if checked.status == ModelStatus.ONLINE:
                    return checked
                else:
                    # 从缓存移除失败的
                    key = f"{provider}_{model_id}"
                    if key in self.warmed_cache:
                        del self.warmed_cache[key]
                    return None
        
        return None


class ModelScheduler:
    """模型调度器 - 增强fallback逻辑"""
    
    def __init__(self, detector: ModelOnlineDetector, preparer: ModelPreparer):
        self.detector = detector
        self.preparer = preparer
    
    def schedule_with_fallback(self, provider: str, primary_model_id: int = None) -> Optional[ModelInfo]:
        """
        调度模型，失败时自动fallback到同服务商其他模型
        
        Args:
            provider: 服务商名称
            primary_model_id: 主用模型ID（可选）
        
        Returns:
            可用的模型信息
        
        遵循序境总则第32条: 数据库优先 - 每次从数据库重新读取
        """
        # 数据库优先: 获取同服务商所有在线模型，每次从数据库重新读取
        online_models = self.detector.detect_provider_models(provider)
        
        if not online_models:
            return None
        
        # 按延迟排序
        sorted_models = sorted(online_models, key=lambda m: m.latency)
        
        # 如果指定了主模型，优先使用
        if primary_model_id:
            for m in sorted_models:
                if m.id == primary_model_id:
                    return m
        
        # 否则返回最优模型
        return sorted_models[0] if sorted_models else None
    
    def get_fallback_chain(self, provider: str, failed_model_id: int) -> List[ModelInfo]:
        """获取fallback链 - 同服务商其他可用模型
        数据库优先: 每次从数据库重新读取模型列表
        """
        online_models = self.detector.detect_provider_models(provider)
        
        # 排除失败模型，返回其他可用模型
        return [m for m in online_models if m.id != failed_model_id]


class MultiModelCoordinator:
    """多模型协调器 - 主控制器
    
    遵循序境总则第32条: 数据库优先，定期同步，禁止固化记忆
    1. 数据库优先 - 每次获取模型配置都从数据库读取
    2. 定期同步 - 后台线程定期清空过期缓存，强制从数据库重新加载
    3. 禁止固化 - 不在内存中长期缓存完整配置，避免固化
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
        
        self.db_path = db_path
        self.config = CoordinatorConfig()
        
        # 初始化子模块
        self.detector = ModelOnlineDetector(db_path, self.config)
        self.preparer = ModelPreparer(self.detector)
        self.scheduler = ModelScheduler(self.detector, self.preparer)
        
        # 定期同步机制 - 后台线程定期清理缓存
        self._sync_thread: Optional[threading.Thread] = None
        self._stop_sync = threading.Event()
        self._sync_interval = 300  # 定期同步间隔(秒)，默认5分钟
    
    def initialize(self):
        """初始化协调器"""
        print(f"[多模型协调器] 初始化完成")
        print(f"  数据库: {self.db_path}")
        print(f"  遵循序境总则第32条: 数据库优先，定期同步，禁止固化记忆")
        
        # 列出所有服务商
        providers = self.detector.get_all_providers()
        print(f"  发现 {len(providers)} 个服务商")
        
        # 启动定期同步后台线程
        self._start_periodic_sync()
        
        return self
    
    def _start_periodic_sync(self):
        """启动定期同步"""
        def sync_worker():
            """后台同步工作线程"""
            while not self._stop_sync.is_set():
                # 等待间隔或停止信号
                if self._stop_sync.wait(timeout=self._sync_interval):
                    break
                
                # 定期同步: 清理过期缓存，强制下次从数据库加载
                self._sync_from_database()
        
        self._sync_thread = threading.Thread(target=sync_worker, daemon=True)
        self._sync_thread.start()
        print(f"[多模型协调器] 定期同步已启动，间隔: {self._sync_interval}秒")
    
    def _sync_from_database(self):
        """从数据库同步 - 清理过期缓存
        
        根据序境总则第32条:
        - 定期清空过期缓存
        - 强制下次访问从数据库重新加载
        - 避免内存固化
        """
        # 清空状态缓存中过期的条目
        expired_count = 0
        current_time = time.time()
        
        # 清理检测器状态缓存
        expired_keys = []
        for key, cache in self.detector.status_cache.items():
            if current_time - cache.get('timestamp', 0) > self.config.cache_ttl:
                expired_keys.append(key)
                expired_count += 1
        
        for key in expired_keys:
            del self.detector.status_cache[key]
        
        # 清理预热缓存中超时的条目(超过1小时无访问)
        expired_warm_keys = []
        for key, cache in self.preparer.warmed_cache.items():
            if current_time - cache.get('last_success', 0) > 3600:  # 1小时
                expired_warm_keys.append(key)
                expired_count += 1
        
        for key in expired_warm_keys:
            del self.preparer.warmed_cache[key]
        
        if expired_count > 0:
            print(f"[定期同步] 清理了 {expired_count} 个过期缓存条目，下次将从数据库重新加载")
    
    def stop_periodic_sync(self):
        """停止定期同步"""
        if self._sync_thread:
            self._stop_sync.set()
            self._sync_thread.join(timeout=1.0)
    
    async def prepare_for_task(self, provider: str, count: int = 2) -> List[ModelInfo]:
        """
        为任务准备模型
        
        Args:
            provider: 服务商
            count: 准备模型数量
        
        Returns:
            准备好的模型列表
        """
        print(f"[多模型协调器] 为 {provider} 准备 {count} 个模型...")
        
        prepared = self.preparer.prepare_models(provider, count)
        
        print(f"[多模型协调器] 准备完成: {len(prepared)} 个模型在线")
        for m in prepared:
            print(f"  - {m.name} (ID:{m.id}, 延迟:{m.latency:.0f}ms)")
        
        return prepared
    
    async def execute_with_fallback(self, provider: str, task_func: Callable, 
                                     primary_model_id: int = None, *args, **kwargs) -> Any:
        """
        执行任务，失败时自动fallback
        
        Args:
            provider: 服务商
            task_func: 任务函数
            primary_model_id: 主用模型ID
            *args, **kwargs: 任务函数参数
        
        Returns:
            任务结果
        """
        # 获取fallback链
        fallback_chain = self.scheduler.get_fallback_chain(provider, primary_model_id or 0)
        
        if not fallback_chain:
            raise Exception(f"服务商 {provider} 没有可用模型")
        
        # 依次尝试
        last_error = None
        for model in fallback链:
            try:
                print(f"[多模型协调器] 尝试模型: {model.name} (ID:{model.id})")
                result = await task_func(model, *args, **kwargs)
                return result
            except Exception as e:
                print(f"[多模型协调器] 模型 {model.name} 失败: {e}")
                last_error = e
                continue
        
        raise Exception(f"所有模型都失败: {last_error}")
    
    def get_provider_status(self, provider: str) -> Dict:
        """获取服务商状态"""
        online_models = self.detector.detect_provider_models(provider)
        
        return {
            "provider": provider,
            "total_online": len(online_models),
            "models": [
                {
                    "id": m.id,
                    "name": m.name,
                    "status": m.status.value,
                    "latency": m.latency
                }
                for m in online_models
            ]
        }
    
    def get_all_status(self) -> Dict:
        """获取所有服务商状态"""
        providers = self.detector.get_all_providers()
        
        return {
            "providers": {
                p: self.get_provider_status(p)
                for p in providers
            },
            "timestamp": datetime.now().isoformat()
        }


# 测试代码
if __name__ == "__main__":
    coordinator = MultiModelCoordinator()
    coordinator.initialize()
    
    # 测试检测在线
    print("\n=== 检测各服务商在线模型 ===")
    for provider in ["英伟达", "火山引擎", "智谱", "硅基流动", "魔搭"]:
        status = coordinator.get_provider_status(provider)
        print(f"{provider}: {status['total_online']} 个在线")
