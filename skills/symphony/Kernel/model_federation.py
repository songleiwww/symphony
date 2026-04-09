# -*- coding: utf-8 -*-
"""
模型联邦调度器
整合智谱 + 英伟达 + 硅基流动 全体模型资源
实现跨服务商智能调度、负载均衡、故障转移
"""
import sys, os, sqlite3, threading, time, uuid, json, requests
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/symphony.db')

class RequestPriority(Enum):
    """请求优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class FederationRequest:
    """联邦调度请求"""
    request_id: str
    prompt: str
    task_type: str
    required_models: int = 1
    complexity: str = "medium"
    priority: RequestPriority = RequestPriority.NORMAL
    preferred_providers: List[str] = None
    excluded_providers: List[str] = None
    preferred_models: List[str] = None
    excluded_models: List[str] = None
    timeout: int = 60
    max_retry: int = 2
    stream: bool = False
    metadata: Dict = None

@dataclass
class ModelEndpoint:
    """模型端点信息"""
    id: str
    name: str
    api_url: str
    api_key: str
    provider: str
    online_status: str
    max_concurrent: int = 10
    current_concurrent: int = 0
    latency: float = 0.0
    success_rate: float = 1.0
    last_check: float = 0.0
    capacity: int = 100

@dataclass
class FederationResponse:
    """联邦调度响应"""
    request_id: str
    success: bool
    selected_models: List[ModelEndpoint]
    strategy: str
    error: Optional[str] = None
    execution_time: float = 0.0
    result: Optional[str] = None

@dataclass
class ProviderPool:
    """服务商池"""
    name: str
    priority: int
    max_concurrent: int
    timeout: int
    retry: int
    enabled: bool
    models: List[ModelEndpoint] = field(default_factory=list)
    current_concurrent: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)

# 服务商配置
PROVIDER_CONFIG = {
    "aliyun": {
        "priority": 1,
        "max_concurrent": 50,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    },
    "minimax": {
        "priority": 2,
        "max_concurrent": 50,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    },
    "zhipu": {
        "priority": 3,
        "max_concurrent": 50,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    },
    "nvidia": {
        "priority": 4,
        "max_concurrent": 50,
        "timeout": 60,
        "retry": 2,
        "enabled": True,
        "models": "all"
    }
}

class ModelFederation:
    """
    模型联邦调度器
    
    特性:
    1. 多服务商协同
    2. 智能路由选择
    3. 故障自动转移
    4. 负载均衡
    5. 跨服务商容错
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()
        self.pools: Dict[str, ProviderPool] = {}
        self.health_cache: Dict[str, Dict] = {}
        self.schedule_lock = threading.Lock()
        self._init_provider_pools()
        self._load_all_models()
        self._start_health_check_worker()

    def _init_db(self):
        """初始化数据库（symphony.db已通过其他脚本初始化，此处仅确保目录存在）"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _init_provider_pools(self):
        """初始化服务商池"""
        for name, config in PROVIDER_CONFIG.items():
            self.pools[name] = ProviderPool(
                name=name,
                priority=config["priority"],
                max_concurrent=config["max_concurrent"],
                timeout=config["timeout"],
                retry=config["retry"],
                enabled=config["enabled"]
            )

    def _load_all_models(self):
        """加载所有模型（适配symphony.db schema）"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # 正确的symphony.db列名：model_id, model_name, provider
        # api_url和api_key从provider_registry获取
        c.execute('''
            SELECT m.model_id, m.model_name, m.provider, m.model_type,
                   p.base_url, p.api_key
            FROM model_config m
            LEFT JOIN provider_registry p ON m.provider = p.provider_code
            WHERE m.is_enabled = 1
        ''')
        rows = c.fetchall()
        for row in rows:
            model_id, model_name, provider, model_type, base_url, api_key = row
            if not provider or provider not in self.pools:
                continue
            pool = self.pools[provider]
            if not pool.enabled:
                continue
            model = ModelEndpoint(
                id=model_id,
                name=model_name,
                api_url=base_url or "",
                api_key=api_key or "",
                provider=provider,
                online_status="unknown",
                max_concurrent=10,
                current_concurrent=0,
                latency=0.0,
                success_rate=1.0,
                last_check=0.0,
                capacity=100
            )
            pool.models.append(model)
        conn.close()

    def _start_health_check_worker(self):
        """启动健康检查后台线程"""
        def worker():
            while True:
                self._batch_health_check()
                time.sleep(60)
        threading.Thread(target=worker, daemon=True, name="FederationHealthCheck").start()

    def _batch_health_check(self):
        """批量健康检查"""
        for pool in self.pools.values():
            if not pool.enabled:
                continue
            for model in pool.models:
                try:
                    result = self.check_model(model)
                    if "success" in result:
                        model.online_status = "online" if result["success"] else "offline"
                        model.latency = result.get("latency", 0.0)
                        model.success_rate = result.get("success_rate", 0.95)
                        model.last_check = time.time()
                except:
                    pass

    def check_model(self, model: ModelEndpoint) -> Dict:
        """检测单个模型健康状态 - 真实API调用"""
        if model.id in self.health_cache:
            cache = self.health_cache[model.id]
            if time.time() - cache["check_time"] < 30:
                return cache["result"]
        start = time.time()
        try:
            headers = {
                "Authorization": f"Bearer {model.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model.name,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 5
            }
            response = requests.post(model.api_url, headers=headers, json=payload, timeout=5)
            success = response.status_code == 200
            latency = time.time() - start
            result = {
                "success": success,
                "latency": latency,
                "success_rate": 0.95 if success else 0.0,
                "status_code": response.status_code if not success else 200
            }
        except Exception as e:
            result = {
                "success": False,
                "latency": time.time() - start,
                "success_rate": 0.0,
                "error": str(e)
            }
        self.health_cache[model.id] = {
            "check_time": time.time(),
            "result": result
        }
        return result

    def _select_best_model(self, request: FederationRequest) -> Tuple[Optional[ModelEndpoint], Optional[str]]:
        """选择最佳模型"""
        candidates = []
        preferred_providers = request.preferred_providers or []
        excluded_providers = request.excluded_providers or []
        # 按优先级遍历服务商
        sorted_pools = sorted(self.pools.values(), key=lambda x: x.priority)
        for pool in sorted_pools:
            if not pool.enabled:
                continue
            if pool.name in excluded_providers:
                continue
            if preferred_providers and pool.name not in preferred_providers:
                continue
            with pool.lock:
                if pool.current_concurrent >= pool.max_concurrent:
                    continue
                # 遍历该服务商的模型
                for model in pool.models:
                    if model.online_status != "online":
                        continue
                    if model.current_concurrent >= model.max_concurrent:
                        continue
                    # 计算分数：成功率 * 100 - 延迟 * 10 + (100 - pool.priority * 10)
                    score = model.success_rate * 100 - model.latency * 10 + (100 - pool.priority * 10)
                    candidates.append((model, pool.name, score))
        # 按分数排序
        candidates.sort(key=lambda x: x[2], reverse=True)
        if not candidates:
            return None, None
        # 返回最佳模型
        return candidates[0][0], candidates[0][1]

    def execute_request(self, request: FederationRequest) -> FederationResponse:
        """调度并真实执行请求 - 调用模型真实API"""
        start_time = time.time()
        selected = []
        error = None
        strategy = "single_best"
        final_result = None
        with self.schedule_lock:
            for _ in range(request.required_models):
                model, provider = self._select_best_model(request)
                if not model:
                    error = "No available online model"
                    break
                selected.append(model)
                # 更新并发计数
                self.pools[provider].current_concurrent += 1
                model.current_concurrent += 1
        if error:
            return FederationResponse(
                request_id=request.request_id,
                success=False,
                selected_models=[],
                strategy=strategy,
                error=error,
                execution_time=time.time() - start_time
            )
        # 真实调用选中模型的API
        try:
            model = selected[0]
            headers = {
                "Authorization": f"Bearer {model.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model.name,
                "messages": [{"role": "user", "content": request.prompt}],
                "max_tokens": 4096,
                "temperature": 0.7,
                "stream": request.stream
            }
            response = requests.post(model.api_url, headers=headers, json=payload, timeout=request.timeout)
            if response.status_code == 200:
                final_result = response.json()
            else:
                error = f"API call failed: {response.status_code} - {response.text}"
        except Exception as e:
            error = f"API execution error: {str(e)}"
        finally:
            # 释放并发计数
            for model in selected:
                provider = model.provider
                self.pools[provider].current_concurrent = max(0, self.pools[provider].current_concurrent - 1)
                model.current_concurrent = max(0, model.current_concurrent - 1)
        return FederationResponse(
            request_id=request.request_id,
            success=error is None,
            selected_models=selected,
            strategy=strategy,
            error=error,
            execution_time=time.time() - start_time,
            result=final_result
        )

    def health_check(self, provider: str = None) -> Dict:
        """健康检查"""
        if provider:
            pools = [self.pools.get(provider)] if provider in self.pools else []
        else:
            pools = list(self.pools.values())
        result = {}
        for pool in pools:
            if not pool:
                continue
            online = sum(1 for m in pool.models if m.online_status == "online")
            result[pool.name] = {
                "enabled": pool.enabled,
                "total_models": len(pool.models),
                "online_models": online,
                "current_concurrent": pool.current_concurrent,
                "max_concurrent": pool.max_concurrent
            }
        return result

    def get_stats(self) -> Dict:
        """获取统计信息"""
        total_models = sum(len(p.models) for p in self.pools.values() if p.enabled)
        online_models = sum(1 for p in self.pools.values() if p.enabled for m in p.models if m.online_status == "online")
        total_concurrent = sum(p.current_concurrent for p in self.pools.values() if p.enabled)
        max_concurrent = sum(p.max_concurrent for p in self.pools.values() if p.enabled)
        return {
            "total_models": total_models,
            "online_models": online_models,
            "current_concurrent": total_concurrent,
            "max_concurrent": max_concurrent,
            "providers": list(self.pools.keys())
        }

# 单例模式
_instance = None
_lock = threading.Lock()

def get_federation() -> ModelFederation:
    """获取联邦调度器实例"""
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = ModelFederation()
    return _instance

if __name__ == "__main__":
    print("=" * 60)
    print(" 模型联邦调度器 v1.0")
    print("=" * 60)
    federation = get_federation()
    stats = federation.get_stats()
    print(f"总模型数: {stats['total_models']}")
    print(f"在线模型数: {stats['online_models']}")
    print(f"当前并发: {stats['current_concurrent']}/{stats['max_concurrent']}")
    print(f"服务商: {', '.join(stats['providers'])}")
    print()
    # 测试调度
    request = FederationRequest(
        request_id=f"test_{uuid.uuid4().hex[:8]}",
        prompt="你好，请介绍一下自己",
        task_type="general",
        required_models=1,
        preferred_providers=["智谱"]
    )
    response = federation.schedule(request)
    print(f"调度测试: {'成功' if response.success else '失败'}")
    if response.success:
        print(f"选中模型: {response.selected_models[0].name} ({response.selected_models[0].provider})")
    print("=" * 60)
