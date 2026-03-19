# -*- coding: utf-8 -*-
"""
工作记忆层 - Working Memory
==========================
功能: LLM Context Window管理
特性: 高频访问、容量有限、时间衰减、快速检索

设计理念:
- 模拟人类工作记忆，用于当前推理过程
- 与LLM的Context Window紧密配合
- 支持Token预算管理和记忆压缩
"""

import time
import hashlib
from typing import Any, Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from collections import OrderedDict
from enum import Enum
import threading


class MemoryStatus(Enum):
    """记忆状态"""
    ACTIVE = "active"      # 活跃 - 正在使用
    INACTIVE = "inactive"  # 不活跃 - 可被淘汰
    ARCHIVED = "archived"  # 已归档 - 需要压缩


@dataclass
class WorkingMemoryItem:
    """工作记忆条目"""
    id: str
    content: str
    token_count: int
    timestamp: float
    last_access: float
    access_count: int = 0
    importance: float = 0.5
    status: MemoryStatus = MemoryStatus.ACTIVE
    role: str = "user"  # user/assistant/system
    metadata: Dict = field(default_factory=dict)
    
    def update_access(self):
        """更新访问"""
        self.last_access = time.time()
        self.access_count += 1
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "token_count": self.token_count,
            "timestamp": self.timestamp,
            "last_access": self.last_access,
            "access_count": self.access_count,
            "importance": self.importance,
            "status": self.status.value,
            "role": self.role,
            "metadata": self.metadata
        }


class WorkingMemoryManager:
    """
    工作记忆管理器
    
    职责:
    - 管理当前会话的上下文
    - 与LLM Context Window配合
    - 动态调整容量
    - 记忆淘汰与压缩
    """
    
    def __init__(
        self,
        max_tokens: int = 60000,
        max_items: int = 100,
        decay_factor: float = 0.95
    ):
        """
        初始化工作记忆管理器
        
        Args:
            max_tokens: 最大Token数 (约等于Context Window)
            max_items: 最大条目数
            decay_factor: 时间衰减因子
        """
        self.max_tokens = max_tokens
        self.max_items = max_items
        self.decay_factor = decay_factor
        
        self._storage: OrderedDict[str, WorkingMemoryItem] = OrderedDict()
        self._lock = threading.RLock()
        
        # 统计
        self._stats = {
            "total_items": 0,
            "total_tokens": 0,
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "compressions": 0
        }
    
    def add(
        self,
        content: str,
        role: str = "user",
        importance: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        添加工作记忆
        
        Args:
            content: 内容
            role: 角色 (user/assistant/system)
            importance: 重要性 0-1
            metadata: 附加元数据
            
        Returns:
            记忆ID
        """
        # 估算token数 (中文约1.5字符=1 token, 英文约4字符=1 token)
        token_count = self._estimate_tokens(content)
        
        # 生成ID
        timestamp = time.time()
        id_str = f"{content[:30]}{timestamp}"
        memory_id = hashlib.md5(id_str.encode()).hexdigest()
        
        item = WorkingMemoryItem(
            id=memory_id,
            content=content,
            token_count=token_count,
            timestamp=timestamp,
            last_access=timestamp,
            access_count=1,
            importance=importance,
            role=role,
            metadata=metadata or {}
        )
        
        with self._lock:
            # 检查容量，必要时淘汰
            self._ensure_capacity(token_count)
            
            # 添加到存储
            self._storage[memory_id] = item
            self._stats["total_items"] += 1
            self._stats["total_tokens"] += token_count
            
            # 移到末尾(最新)
            self._storage.move_to_end(memory_id)
        
        return memory_id
    
    def get(self, memory_id: str) -> Optional[WorkingMemoryItem]:
        """获取记忆"""
        with self._lock:
            if memory_id not in self._storage:
                self._stats["misses"] += 1
                return None
            
            item = self._storage[memory_id]
            item.update_access()
            self._storage.move_to_end(memory_id)
            self._stats["hits"] += 1
            
            return item
    
    def get_recent(self, count: int = 10) -> List[WorkingMemoryItem]:
        """获取最近N条记忆"""
        with self._lock:
            items = list(self._storage.values())
            return items[-count:][::-1]  # 最新的在前
    
    def get_context_window(
        self,
        max_tokens: Optional[int] = None
    ) -> Tuple[List[WorkingMemoryItem], int]:
        """
        获取当前Context Window可用的记忆
        
        Args:
            max_tokens: 最大token数限制
            
        Returns:
            (记忆列表, 总token数)
        """
        max_tokens = max_tokens or self.max_tokens
        
        with self._lock:
            context = []
            total_tokens = 0
            
            # 从最新到最旧选择
            items = list(self._storage.values())[::-1]
            
            for item in items:
                if total_tokens + item.token_count > max_tokens:
                    # 尝试压缩或跳过
                    if item.importance < 0.3:
                        continue  # 跳过低重要性
                    # 可以在这里实现压缩逻辑
                
                context.append(item)
                total_tokens += item.token_count
            
            return context, total_tokens
    
    def search(self, query: str, top_k: int = 5) -> List[WorkingMemoryItem]:
        """关键词搜索"""
        with self._lock:
            results = []
            query_lower = query.lower()
            
            for item in self._storage.values():
                if query_lower in item.content.lower():
                    score = self._calculate_score(item, query)
                    results.append((score, item))
            
            results.sort(key=lambda x: x[0], reverse=True)
            return [item for _, item in results[:top_k]]
    
    def _calculate_score(self, item: WorkingMemoryItem, query: str) -> float:
        """计算相关性分数"""
        score = 0.0
        
        # 关键词匹配
        if query.lower() in item.content.lower():
            score += 0.3
        
        # 访问频率
        score += min(item.access_count * 0.05, 0.2)
        
        # 重要性
        score += item.importance * 0.3
        
        # 时间衰减
        recency = 1.0 / (time.time() - item.last_access + 1)
        score += recency * 0.2
        
        return score
    
    def _estimate_tokens(self, text: str) -> int:
        """估算Token数"""
        # 简单估算: 中文约1.5字符/token, 英文约4字符/token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + english_chars / 4)
    
    def _ensure_capacity(self, new_tokens: int):
        """确保容量足够"""
        while (self._stats["total_tokens"] + new_tokens > self.max_tokens 
               or len(self._storage) >= self.max_items):
            if not self._storage:
                break
            self._evict_lru()
    
    def _evict_lru(self):
        """淘汰最少使用的记忆"""
        if not self._storage:
            return
        
        # 找到最应该淘汰的
        to_evict = None
        min_score = float('inf')
        
        for memory_id, item in self._storage.items():
            # 计算淘汰分数: 越久未访问、重要性越低，越应该淘汰
            recency = 1.0 / (time.time() - item.last_access + 1)
            evict_score = recency * (1.0 - item.importance + 0.1)
            
            if evict_score < min_score:
                min_score = evict_score
                to_evict = memory_id
        
        if to_evict:
            evicted = self._storage.pop(to_evict)
            self._stats["total_tokens"] -= evicted.token_count
            self._stats["total_items"] -= 1
            self._stats["evictions"] += 1
    
    def compress(self, target_tokens: int) -> int:
        """
        压缩工作记忆
        
        Args:
            target_tokens: 目标token数
            
        Returns:
            压缩后的token数
        """
        with self._lock:
            current_tokens = self._stats["total_tokens"]
            
            if current_tokens <= target_tokens:
                return current_tokens
            
            # 按重要性排序，保留高重要性
            items = sorted(
                self._storage.values(),
                key=lambda x: x.importance,
                reverse=True
            )
            
            new_storage = OrderedDict()
            new_tokens = 0
            
            for item in items:
                if new_tokens + item.token_count <= target_tokens:
                    new_storage[item.id] = item
                    new_tokens += item.token_count
            
            self._storage = new_storage
            self._stats["total_tokens"] = new_tokens
            self._stats["compressions"] += 1
            
            return new_tokens
    
    def clear(self):
        """清空工作记忆"""
        with self._lock:
            self._storage.clear()
            self._stats["total_items"] = 0
            self._stats["total_tokens"] = 0
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self._lock:
            total = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / max(1, total)
            
            return {
                "version": "3.2.0",
                "type": "working_memory",
                "current_items": len(self._storage),
                "current_tokens": self._stats["total_tokens"],
                "max_tokens": self.max_tokens,
                "max_items": self.max_items,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": f"{hit_rate*100:.1f}%",
                "evictions": self._stats["evictions"],
                "compressions": self._stats["compressions"]
            }
    
    def export_for_context(self) -> List[Dict]:
        """导出为Context格式"""
        items, _ = self.get_context_window()
        return [
            {
                "role": item.role,
                "content": item.content
            }
            for item in items
        ]


# 全局实例
_working_memory: Optional[WorkingMemoryManager] = None
_wm_lock = threading.Lock()


def get_working_memory(
    max_tokens: int = 60000,
    max_items: int = 100
) -> WorkingMemoryManager:
    """获取全局工作记忆实例"""
    global _working_memory
    with _wm_lock:
        if _working_memory is None:
            _working_memory = WorkingMemoryManager(
                max_tokens=max_tokens,
                max_items=max_items
            )
        return _working_memory


if __name__ == "__main__":
    print("=== 工作记忆测试 ===")
    
    wm = WorkingMemoryManager(max_tokens=1000, max_items=10)
    
    # 添加记忆
    wm.add("用户: 你好，我想了解序境系统", role="user", importance=0.8)
    wm.add("助手: 序境是一个AI Agent系统，包含多层架构", role="assistant", importance=0.9)
    wm.add("用户: 有什么特色功能？", role="user", importance=0.6)
    wm.add("助手: 序境3.2.0支持三层记忆系统: 工作记忆、短期记忆、长期记忆", role="assistant", importance=0.9)
    
    print(f"当前条目: {wm.get_stats()['current_items']}")
    print(f"当前Token: {wm.get_stats()['current_tokens']}")
    
    # 获取上下文
    context, tokens = wm.get_context_window()
    print(f"\nContext Window ({tokens} tokens):")
    for item in context:
        print(f"  [{item.role}] {item.content[:30]}...")
    
    # 搜索
    print("\n搜索'记忆':")
    results = wm.search("记忆")
    for item in results:
        print(f"  - {item.content[:40]}...")
    
    print("\n统计:", wm.get_stats())
