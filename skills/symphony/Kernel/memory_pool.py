# -*- coding: utf-8 -*-
"""
序境系统 - 内存池复用模??v4.5.0
================================
目标: 内存占用减少20-30%，GC暂停减少50%

核心优化:
1. 对象池复??- 减少内存分配/释放循环
2. __slots__ - 减少对象内存开销
3. 批量预分??- 降低运行时分配频??
作?? 少府监·翰林学??版本: 4.5.0
"""

import threading
from typing import Dict, List, Optional, Any, TypeVar, Type, Callable

T = TypeVar('T')

# ==================== 内存池核??====================

class MemoryPool:
    """
    通用对象内存??    
    使用类变量存储各类型的对象池，实现对象的复用与回收??    配合 __slots__ 使用效果更佳??    
    使用示例:
        # 定义带池化的??        @dataclass
        class TaskInfo:
            __slots__ = ('id', 'prompt', 'task_type', 'complexity', 'priority', 'timeout', 
                        'preferred_providers', 'dependencies')
            
            id: str
            prompt: str
            task_type: str
            complexity: Any
            priority: int
            timeout: int
            preferred_providers: List
            dependencies: List
            
            def __post_init__(self):
                self.id = id
                ...
        
        # 使用内存??        pool = MemoryPool()
        obj = pool.alloc(TaskInfo, 'task_001', 'prompt', 'code', ...)
        pool.release(TaskInfo, obj)
    """
    
    _pools: Dict[str, List[Any]] = {}
    _pool_locks: Dict[str, threading.Lock] = {}
    _factory_methods: Dict[str, Callable] = {}
    _max_pool_size: Dict[str, int] = {}
    _default_max_size: int = 100
    
    @classmethod
    def _get_lock(cls, type_name: str) -> threading.Lock:
        """获取类型对应的锁"""
        if type_name not in cls._pool_locks:
            cls._pool_locks[type_name] = threading.Lock()
        return cls._pool_locks[type_name]
    
    @classmethod
    def register_type(cls, type_name: str, factory: Callable[[], Any] = None, 
                      max_size: int = None) -> None:
        """
        注册类型到内存池
        
        Args:
            type_name: 类型名称（唯一标识??            factory: 对象工厂函数，用于创建新对象
            max_size: 池最大容??        """
        if type_name not in cls._pools:
            cls._pools[type_name] = []
        if factory:
            cls._factory_methods[type_name] = factory
        if max_size is not None:
            cls._max_pool_size[type_name] = max_size
        else:
            cls._max_pool_size[type_name] = cls._default_max_size
    
    @classmethod
    def alloc(cls, type_name: str, *args, **kwargs) -> Optional[Any]:
        """
        从池中分配对??        
        Args:
            type_name: 类型名称
            *args, **kwargs: 传递给工厂方法或对象初始化的参??            
        Returns:
            对象实例，或None（池为空且无工厂??        """
        lock = cls._get_lock(type_name)
        
        with lock:
            pool = cls._pools.get(type_name, [])
            
            # 尝试从池中获??            if pool:
                obj = pool.pop()
                # 使用工厂方法重置对象状??                if type_name in cls._factory_methods:
                    try:
                        cls._factory_methods[type_name](obj, *args, **kwargs)
                    except TypeError:
                        try:
                            cls._factory_methods[type_name](obj)
                        except TypeError:
                            # 工厂方法是创建新对象的，忽略重置
                            pass
                return obj
            
            # 池为空，返回None（调用方需自行创建??            return None
    
    @classmethod
    def try_alloc(cls, type_name: str, factory: Callable[[], Any],
                  *args, **kwargs) -> Any:
        """
        尝试分配对象（优先从池获取，池空时使用工厂创建）
        
        Args:
            type_name: 类型名称
            factory: 对象工厂函数
            *args, **kwargs: 工厂参数
            
        Returns:
            对象实例
        """
        obj = cls.alloc(type_name, *args, **kwargs)
        if obj is None:
            obj = factory(*args, **kwargs)
        return obj
    
    @classmethod
    def release(cls, type_name: str, obj: Any) -> bool:
        """
        将对象释放回??        
        Args:
            type_name: 类型名称
            obj: 对象实例
            
        Returns:
            是否成功入池
        """
        if obj is None:
            return False
            
        lock = cls._get_lock(type_name)
        
        with lock:
            if type_name not in cls._pools:
                cls._pools[type_name] = []
            
            pool = cls._pools[type_name]
            max_size = cls._max_pool_size.get(type_name, cls._default_max_size)
            
            # 超过容量则不回收，直接丢??            if len(pool) >= max_size:
                return False
            
            pool.append(obj)
            return True
    
    @classmethod
    def prewarm(cls, type_name: str, factory: Callable[[], Any], 
                count: int = 10) -> int:
        """
        预热??- 提前创建对象
        
        Args:
            type_name: 类型名称
            factory: 对象工厂函数
            count: 预创建数??            
        Returns:
            实际预创建数??        """
        lock = cls._get_lock(type_name)
        created = 0
        
        with lock:
            if type_name not in cls._pools:
                cls._pools[type_name] = []
            
            pool = cls._pools[type_name]
            max_size = cls._max_pool_size.get(type_name, cls._default_max_size)
            
            available = max_size - len(pool)
            to_create = min(count, available)
            
            for _ in range(to_create):
                try:
                    obj = factory()
                    pool.append(obj)
                    created += 1
                except Exception:
                    break
        
        return created
    
    @classmethod
    def clear(cls, type_name: str = None) -> None:
        """
        清空??        
        Args:
            type_name: 类型名称，None表示清空所有池
        """
        if type_name:
            lock = cls._get_lock(type_name)
            with lock:
                if type_name in cls._pools:
                    cls._pools[type_name].clear()
        else:
            # 清空所有池
            for name in list(cls._pools.keys()):
                lock = cls._get_lock(name)
                with lock:
                    cls._pools[name].clear()
    
    @classmethod
    def get_stats(cls, type_name: str = None) -> Dict[str, Any]:
        """
        获取池统计信??        
        Args:
            type_name: 类型名称，None表示获取所有统??            
        Returns:
            统计信息字典
        """
        if type_name:
            lock = cls._get_lock(type_name)
            with lock:
                pool = cls._pools.get(type_name, [])
                return {
                    "type": type_name,
                    "pooled": len(pool),
                    "max_size": cls._max_pool_size.get(type_name, cls._default_max_size),
                    "factory_registered": type_name in cls._factory_methods
                }
        else:
            stats = {}
            for name in cls._pools:
                stats[name] = cls.get_stats(name)
            return stats
    
    @classmethod
    def get_pool_size(cls, type_name: str) -> int:
        """获取池中对象数量"""
        lock = cls._get_lock(type_name)
        with lock:
            return len(cls._pools.get(type_name, []))


# ==================== 便捷函数 ====================

_pool_instance = MemoryPool()

def alloc(type_name: str, *args, **kwargs) -> Optional[Any]:
    """从默认池分配对象"""
    return _pool_instance.alloc(type_name, *args, **kwargs)

def release(type_name: str, obj: Any) -> bool:
    """释放对象到默认池"""
    return _pool_instance.release(type_name, obj)

def register_type(type_name: str, factory: Callable = None, max_size: int = None) -> None:
    """注册类型到默认池"""
    return _pool_instance.register_type(type_name, factory, max_size)

def prewarm(type_name: str, factory: Callable, count: int = 10) -> int:
    """预热默认??"""
    return _pool_instance.prewarm(type_name, factory, count)


# ==================== 导出的名??====================

__all__ = [
    "MemoryPool",
    "alloc", 
    "release", 
    "register_type", 
    "prewarm",
    "_pool_instance"
]

