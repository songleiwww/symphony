# -*- coding: utf-8 -*-
"""
内存缓存模块 - Memory Cache

利用内存高速存取提升序境系统性能

功能：
- 模型配置缓存
- 调度结果缓存
- 热点数据缓存
- LRU淘汰策略
"""
import time
import threading
from typing import Any, Optional, Dict, List
from dataclasses import dataclass
from collections import OrderedDict
import hashlib


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: float
    last_access: float
    hit_count: int = 0
    ttl: int = 3600  # 默认1小时


class LRUCache:
    """
    LRU缓存（最近最少使用）
    
    特点：
    - O(1)读写复杂度
    - 内存bounded
    - 自动淘汰
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # 统计
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_size": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        返回:
            缓存值，不存在返回None
        """
        with self._lock:
            if key not in self._cache:
                self.stats["misses"] += 1
                return None
            
            entry = self._cache[key]
            
            # 检查TTL
            if time.time() - entry.created_at > entry.ttl:
                del self._cache[key]
                self.stats["misses"] += 1
                return None
            
            # 更新访问时间
            entry.last_access = time.time()
            entry.hit_count += 1
            
            # 移到末尾（最近使用）
            self._cache.move_to_end(key)
            
            self.stats["hits"] += 1
            return entry.value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
        设置缓存
        
        参数:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
        """
        with self._lock:
            # 如果存在，先删除旧条目
            if key in self._cache:
                old_entry = self._cache[key]
                del self._cache[key]
            
            # 创建新条目
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                last_access=time.time(),
                ttl=ttl or self.default_ttl
            )
            
            # 添加到末尾
            self._cache[key] = entry
            
            # 如果超过最大size，淘汰最早的
            while len(self._cache) > self.max_size:
                first_key = next(iter(self._cache))
                del self._cache[first_key]
                self.stats["evictions"] += 1
            
            self.stats["total_size"] = len(self._cache)
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self.stats["total_size"] = len(self._cache)
                return True
            return False
    
    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self.stats["total_size"] = 0
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self._lock:
            total = self.stats["hits"] + self.stats["misses"]
            hit_rate = self.stats["hits"] / max(1, total)
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": f"{hit_rate*100:.1f}%",
                "evictions": self.stats["evictions"]
            }
    
    def keys(self) -> List[str]:
        """获取所有键"""
        return list(self._cache.keys())


class ModelCache:
    """
    模型缓存 - 专门用于缓存模型相关数据
    """
    
    def __init__(self):
        # 模型配置缓存
        self.model_config = LRUCache(max_size=200, default_ttl=1800)
        
        # 调度结果缓存
        self.dispatch_result = LRUCache(max_size=500, default_ttl=300)
        
        # 在线模型缓存
        self.online_models = LRUCache(max_size=100, default_ttl=60)
        
        # 热点prompt缓存
        self.prompt_cache = LRUCache(max_size=1000, default_ttl=600)
    
    def cache_model_config(self, model_id: str, config: Dict):
        """缓存模型配置"""
        key = f"model_config_{model_id}"
        self.model_config.set(key, config)
    
    def get_model_config(self, model_id: str) -> Optional[Dict]:
        """获取模型配置"""
        key = f"model_config_{model_id}"
        return self.model_config.get(key)
    
    def cache_dispatch_result(self, prompt: str, result: Any):
        """缓存调度结果"""
        # 使用prompt hash作为key
        key = hashlib.md5(prompt.encode()).hexdigest()
        self.dispatch_result.set(key, result)
    
    def get_dispatch_result(self, prompt: str) -> Optional[Any]:
        """获取调度结果"""
        key = hashlib.md5(prompt.encode()).hexdigest()
        return self.dispatch_result.get(key)
    
    def cache_online_models(self, models: List[Dict]):
        """缓存在线模型"""
        self.online_models.set("online_list", models)
    
    def get_online_models(self) -> Optional[List[Dict]]:
        """获取在线模型"""
        return self.online_models.get("online_list")
    
    def get_stats(self) -> Dict:
        """获取所有统计"""
        return {
            "model_config": self.model_config.get_stats(),
            "dispatch_result": self.dispatch_result.get_stats(),
            "online_models": self.online_models.get_stats(),
            "prompt_cache": self.prompt_cache.get_stats()
        }


# 全局缓存实例
_global_cache: Optional[ModelCache] = None
_cache_lock = threading.Lock()


def get_model_cache() -> ModelCache:
    """获取全局模型缓存"""
    global _global_cache
    with _cache_lock:
        if _global_cache is None:
            _global_cache = ModelCache()
        return _global_cache


# 测试
if __name__ == "__main__":
    print("=== 内存缓存测试 ===")
    
    cache = LRUCache(max_size=3)
    
    # 测试写入
    cache.set("a", "value_a")
    cache.set("b", "value_b")
    cache.set("c", "value_c")
    
    print("初始:", cache.keys())
    
    # 测试读取
    val = cache.get("a")
    print("读取a:", val)
    
    # 测试LRU
    cache.set("d", "value_d")
    print("写入d后:", cache.keys())
    
    # 统计
    stats = cache.get_stats()
    print("统计:", stats)
    
    print()
    print("=== 模型缓存测试 ===")
    model_cache = get_model_cache()
    print("ModelCache: OK")
    print("Stats:", model_cache.get_stats())
