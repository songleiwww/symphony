# -*- coding: utf-8 -*-
"""
分层模型缓存 - L1/L2/L3 三层架构
================================
L1: 热点模型（LRU, max 10个） - 最热门的模??L2: 温点模型（TTL, 5分钟, max 100个） - 近期使用过的模型
L3: 冷点模型（磁盘缓存） - 所有已缓存的模型信??
目标: 热点模型缓存命中率从60%提升??5%
"""

import json
import os
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

# 缓存配置
L1_MAX_SIZE = 10          # L1 热点模型最大数??L2_MAX_SIZE = 100         # L2 温点模型最大数??L2_TTL_SECONDS = 300      # L2 TTL 5分钟
L3_CACHE_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/model_cache'
L3_DISK_MAX_AGE = 3600    # L3 磁盘缓存最大保留时间（秒）

# 确保缓存目录存在
os.makedirs(L3_CACHE_DIR, exist_ok=True)


@dataclass
class CacheEntry:
    """缓存条目"""
    data: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    
    def is_expired(self, ttl: float) -> bool:
        """检查是否过??"""
        return (time.time() - self.created_at) > ttl
    
    def touch(self):
        """更新访问时间"""
        self.last_accessed = time.time()
        self.access_count += 1


class L1Cache:
    """L1 热点缓存 - LRU策略，最??0个模??"""
    
    def __init__(self, max_size: int = L1_MAX_SIZE):
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存，如果存在则移到末尾(LRU)"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                # 移到末尾（最新使用）
                self._cache.move_to_end(key)
                entry.touch()
                self._hits += 1
                return entry.data
            self._misses += 1
            return None
    
    def put(self, key: str, value: Any):
        """放入缓存，如果超容量则移除最旧的"""
        with self._lock:
            if key in self._cache:
                self._cache[key].data = value
                self._cache[key].touch()
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self.max_size:
                    # 移除最旧的条目
                    self._cache.popitem(last=False)
                
                now = time.time()
                self._cache[key] = CacheEntry(
                    data=value,
                    created_at=now,
                    last_accessed=now
                )
    
    def remove(self, key: str) -> bool:
        """移除缓存条目"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def promote_to_l1(self, key: str, data: Any):
        """从L2提升到L1"""
        self.put(key, data)
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                'hits': self._hits,
                'misses': self._misses,
                'size': len(self._cache),
                'hit_rate': hit_rate
            }


class L2Cache:
    """L2 温点缓存 - TTL策略，最??00个模型，5分钟过期"""
    
    def __init__(self, max_size: int = L2_MAX_SIZE, ttl: float = L2_TTL_SECONDS):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存，检查TTL"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_expired(self.ttl):
                    # 已过期，移除
                    del self._cache[key]
                    self._misses += 1
                    return None
                # 移到末尾
                self._cache.move_to_end(key)
                entry.touch()
                self._hits += 1
                return entry.data
            self._misses += 1
            return None
    
    def put(self, key: str, value: Any):
        """放入缓存"""
        with self._lock:
            if key in self._cache:
                self._cache[key].data = value
                self._cache[key].touch()
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self.max_size:
                    # 移除最旧的条目
                    self._cache.popitem(last=False)
                
                now = time.time()
                self._cache[key] = CacheEntry(
                    data=value,
                    created_at=now,
                    last_accessed=now
                )
    
    def remove(self, key: str) -> bool:
        """移除缓存条目"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def cleanup_expired(self):
        """清理所有过期条??"""
        with self._lock:
            expired_keys = [
                k for k, v in self._cache.items() 
                if v.is_expired(self.ttl)
            ]
            for key in expired_keys:
                del self._cache[key]
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                'hits': self._hits,
                'misses': self._misses,
                'size': len(self._cache),
                'hit_rate': hit_rate
            }


class L3Cache:
    """L3 冷点缓存 - 磁盘缓存"""
    
    def __init__(self, cache_dir: str = L3_CACHE_DIR, max_age: int = L3_DISK_MAX_AGE):
        self.cache_dir = cache_dir
        self.max_age = max_age
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        self._hits = 0
        self._misses = 0
        
        # 确保目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_file_path(self, key: str) -> str:
        """获取缓存文件路径"""
        # 使用哈希避免文件名问??        import hashlib
        hashed = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """从磁盘获取缓??"""
        with self._lock:
            file_path = self._get_file_path(key)
            
            if not os.path.exists(file_path):
                self._misses += 1
                return None
            
            try:
                # 检查文件年??                file_age = time.time() - os.path.getmtime(file_path)
                if file_age > self.max_age:
                    os.remove(file_path)
                    self._misses += 1
                    return None
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self._hits += 1
                return data
            except (json.JSONDecodeError, IOError, OSError):
                self._misses += 1
                return None
    
    def put(self, key: str, value: Any):
        """写入磁盘缓存"""
        with self._lock:
            file_path = self._get_file_path(key)
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(value, f, ensure_ascii=False, indent=2, default=str)
            except (IOError, OSError):
                pass  # 忽略写入失败
    
    def remove(self, key: str) -> bool:
        """删除磁盘缓存"""
        with self._lock:
            file_path = self._get_file_path(key)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    return True
                except OSError:
                    return False
            return False
    
    def cleanup_old(self) -> int:
        """清理过期文件"""
        with self._lock:
            removed = 0
            current_time = time.time()
            
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    if current_time - os.path.getmtime(file_path) > self.max_age:
                        os.remove(file_path)
                        removed += 1
                except OSError:
                    continue
            
            return removed
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            file_count = len([f for f in os.listdir(self.cache_dir) if f.endswith('.json')]) if os.path.exists(self.cache_dir) else 0
            return {
                'hits': self._hits,
                'misses': self._misses,
                'files': file_count,
                'hit_rate': hit_rate
            }


class LayeredModelCache:
    """
    分层模型缓存 - L1/L2/L3 三层架构
    =====================================
    
    访问流程:
    1. 先查L1（热点LRU），命中则返??    2. L1未命中，查L2（温点TTL），命中则提升到L1
    3. L2未命中，查L3（磁盘缓存），命中则提升到L2/L1
    4. 全部未命中，返回None
    
    写入流程:
    1. 同时写入L1/L2/L3
    
    目标: 热点模型缓存命中率从60%提升??5%
    """
    
    def __init__(self):
        self.l1 = L1Cache()
        self.l2 = L2Cache()
        self.l3 = L3Cache()
        self._total_hits = 0
        self._total_misses = 0
        self._promotions_l2_to_l1 = 0
        self._promotions_l3_to_l2 = 0
        self._lock = threading.Lock()
        
        # 定期清理任务
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """启动后台清理线程"""
        def cleanup_task():
            while True:
                time.sleep(60)  # 每分钟清理一??                try:
                    expired = self.l2.cleanup_expired()
                    old_files = self.l3.cleanup_old()
                    if expired > 0 or old_files > 0:
                        pass  # 日志可在此处添加
                except Exception:
                    pass
        
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()
    
    def get(self, model_id: str) -> Optional[Any]:
        """
        获取模型信息
        层级查找: L1 -> L2 -> L3 -> None
        
        Args:
            model_id: 模型ID
            
        Returns:
            模型信息字典，如果未找到返回None
        """
        # L1 查询
        data = self.l1.get(model_id)
        if data is not None:
            return data
        
        # L2 查询
        data = self.l2.get(model_id)
        if data is not None:
            # L2命中，提升到L1
            self.l1.promote_to_l1(model_id, data)
            with self._lock:
                self._promotions_l2_to_l1 += 1
            return data
        
        # L3 查询
        data = self.l3.get(model_id)
        if data is not None:
            # L3命中，提升到L2和L1
            self.l2.put(model_id, data)
            self.l1.promote_to_l1(model_id, data)
            with self._lock:
                self._promotions_l3_to_l2 += 1
                self._promotions_l2_to_l1 += 1
            return data
        
        with self._lock:
            self._total_misses += 1
        return None
    
    def put(self, model_id: str, info: Dict):
        """
        写入模型信息到所有层级缓??        
        Args:
            model_id: 模型ID
            info: 模型信息字典
        """
        # 同时写入三层缓存
        self.l1.put(model_id, info)
        self.l2.put(model_id, info)
        self.l3.put(model_id, info)
    
    def remove(self, model_id: str):
        """从所有层级移??"""
        self.l1.remove(model_id)
        self.l2.remove(model_id)
        self.l3.remove(model_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            包含各层命中率和总体命中率的统计字典
        """
        l1_stats = self.l1.get_stats()
        l2_stats = self.l2.get_stats()
        l3_stats = self.l3.get_stats()
        
        # 计算总体命中??        total_hits = l1_stats['hits'] + l2_stats['hits'] + l3_stats['hits']
        total_requests = total_hits + (self._total_misses if hasattr(self, '_total_misses') else 0)
        
        # 修正：直接用各层hit/miss统计
        total_h = l1_stats['hits'] + l2_stats['hits'] + l3_stats['hits']
        total_m = l1_stats['misses'] + l2_stats['misses'] + l3_stats['misses']
        overall_hit_rate = (total_h / (total_h + total_m) * 100) if (total_h + total_m) > 0 else 0
        
        return {
            'l1': l1_stats,
            'l2': l2_stats,
            'l3': l3_stats,
            'overall': {
                'hits': total_h,
                'misses': total_m,
                'hit_rate': overall_hit_rate,
                'promotions_l2_to_l1': self._promotions_l2_to_l1,
                'promotions_l3_to_l2': self._promotions_l3_to_l2,
            },
            'target_hit_rate': 85.0,
            'current_hit_rate': overall_hit_rate
        }
    
    def reset_stats(self):
        """重置统计"""
        # 重新初始化各层缓存的统计
        self.l1 = L1Cache()
        self.l2 = L2Cache()
        self.l3 = L3Cache()
        self._total_hits = 0
        self._total_misses = 0
        self._promotions_l2_to_l1 = 0
        self._promotions_l3_to_l2 = 0


# 全局缓存实例
_global_cache: Optional[LayeredModelCache] = None
_cache_lock = threading.Lock()


def get_layered_cache() -> LayeredModelCache:
    """获取全局分层缓存实例（单例）"""
    global _global_cache
    with _cache_lock:
        if _global_cache is None:
            _global_cache = LayeredModelCache()
        return _global_cache


# 测试代码
if __name__ == "__main__":
    cache = LayeredModelCache()
    
    print("=" * 60)
    print("分层模型缓存测试")
    print("=" * 60)
    
    # 测试写入
    test_models = [
        {"id": "model_001", "name": "DeepSeek V3", "provider": "英伟??, "status": "online"},
        {"id": "model_002", "name": "Llama3 70B", "provider": "英伟??, "status": "online"},
        {"id": "model_003", "name": "Qwen2.5 72B", "provider": "硅基流动", "status": "online"},
        {"id": "model_004", "name": "GLM-4 Flash", "provider": "智谱", "status": "online"},
    ]
    
    # 写入测试
    print("\n[测试1] 写入模型到缓??..")
    for model in test_models:
        cache.put(model["id"], model)
        print(f"  写入: {model['id']} - {model['name']}")
    
    # 测试读取
    print("\n[测试2] 测试缓存命中...")
    
    # 首次读取（应该从L1获取??    print("  首次读取 model_001:")
    result = cache.get("model_001")
    print(f"    结果: {result['name'] if result else 'None'}")
    
    # 再次读取（LRU测试??    print("  再次读取 model_001:")
    result = cache.get("model_001")
    print(f"    结果: {result['name'] if result else 'None'}")
    
    # 测试L3降级（清空L1/L2后从L3恢复??    print("\n[测试3] 测试L3降级恢复...")
    cache.l1.remove("model_001")
    cache.l2.remove("model_001")
    print("  清空L1/L2后读??model_001:")
    result = cache.get("model_001")
    print(f"    结果: {result['name'] if result else 'None'}")
    
    # 统计信息
    print("\n[测试4] 缓存统计信息:")
    stats = cache.get_stats()
    print(f"  L1 命中?? {stats['l1']['hit_rate']:.1f}% ({stats['l1']['hits']} hits / {stats['l1']['hits'] + stats['l1']['misses']} total)")
    print(f"  L2 命中?? {stats['l2']['hit_rate']:.1f}% ({stats['l2']['hits']} hits / {stats['l2']['hits'] + stats['l2']['misses']} total)")
    print(f"  L3 命中?? {stats['l3']['hit_rate']:.1f}% ({stats['l3']['hits']} hits / {stats['l3']['hits'] + stats['l3']['misses']} total)")
    print(f"  总体命中?? {stats['overall']['hit_rate']:.1f}%")
    print(f"  目标命中?? {stats['target_hit_rate']:.1f}%")
    print(f"  L2->L1 提升次数: {stats['overall']['promotions_l2_to_l1']}")
    print(f"  L3->L2 提升次数: {stats['overall']['promotions_l3_to_l2']}")
    
    # LRU驱逐测??    print("\n[测试5] LRU驱逐测??..")
    print(f"  L1当前大小: {stats['l1']['size']} / {L1_MAX_SIZE}")
    
    # 写入更多模型触发LRU
    for i in range(15):
        cache.put(f"model_new_{i}", {"id": f"model_new_{i}", "name": f"New Model {i}"})
    
    stats = cache.get_stats()
    print(f"  L1写入后大?? {stats['l1']['size']} / {L1_MAX_SIZE}")
    
    # 验证旧模型是否被驱??    old_model = cache.get("model_001")
    print(f"  model_001 是否仍在L1: {'?? if old_model else '??}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

