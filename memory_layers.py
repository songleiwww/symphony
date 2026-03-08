#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
memory_layers.py - 四层记忆架构
实现短期记忆、长期记忆、工作记忆、情景记忆
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
import json


class MemoryType:
    """记忆类型"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING = "working"
    EPISODIC = "episodic"


class ShortTermMemory:
    """短期记忆 - 当前对话上下文"""
    
    def __init__(self, capacity: int = 10):
        """
        初始化短期记忆
        
        Args:
            capacity: 容量（保存最近N条）
        """
        self.capacity = capacity
        self.memory: deque = deque(maxlen=capacity)
    
    def add(self, content: str, role: str = "user") -> None:
        """添加记忆"""
        self.memory.append({
            "content": content,
            "role": role,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有记忆"""
        return list(self.memory)
    
    def get_recent(self, n: int = 5) -> List[Dict[str, Any]]:
        """获取最近N条记忆"""
        return list(self.memory)[-n:]
    
    def clear(self) -> None:
        """清空记忆"""
        self.memory.clear()


class LongTermMemory:
    """长期记忆 - 持久化知识存储"""
    
    def __init__(self, storage_file: str = "long_term_memory.json"):
        """
        初始化长期记忆
        
        Args:
            storage_file: 存储文件路径
        """
        self.storage_file = storage_file
        self.memory: Dict[str, Dict[str, Any]] = {}
        self._load()
    
    def _load(self) -> None:
        """从文件加载"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                self.memory = json.load(f)
        except:
            self.memory = {}
    
    def _save(self) -> None:
        """保存到文件"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def add(self, key: str, value: Any, category: str = "general") -> None:
        """添加记忆"""
        self.memory[key] = {
            "value": value,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }
        self._save()
    
    def get(self, key: str) -> Optional[Any]:
        """获取记忆"""
        if key in self.memory:
            self.memory[key]["access_count"] += 1
            self.memory[key]["last_accessed"] = datetime.now().isoformat()
            self._save()
            return self.memory[key]["value"]
        return None
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """搜索记忆"""
        results = []
        for key, data in self.memory.items():
            if query.lower() in key.lower() or query.lower() in str(data["value"]).lower():
                results.append({"key": key, **data})
        return results
    
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按类别获取记忆"""
        return [
            {"key": k, **v}
            for k, v in self.memory.items()
            if v.get("category") == category
        ]


class WorkingMemory:
    """工作记忆 - 当前任务相关"""
    
    def __init__(self):
        """初始化工作记忆"""
        self.current_task: Optional[str] = None
        self.task_context: Dict[str, Any] = {}
        self.related_memories: List[Dict[str, Any]] = []
    
    def set_task(self, task: str) -> None:
        """设置当前任务"""
        self.current_task = task
        self.task_context = {}
        self.related_memories = []
    
    def add_context(self, key: str, value: Any) -> None:
        """添加任务上下文"""
        self.task_context[key] = value
    
    def add_related_memory(self, memory: Dict[str, Any]) -> None:
        """添加相关记忆"""
        self.related_memories.append(memory)
    
    def get_context(self) -> Dict[str, Any]:
        """获取完整上下文"""
        return {
            "task": self.current_task,
            "context": self.task_context,
            "related_memories": self.related_memories
        }
    
    def clear(self) -> None:
        """清空工作记忆"""
        self.current_task = None
        self.task_context = {}
        self.related_memories = []


class EpisodicMemory:
    """情景记忆 - 特定事件和时间"""
    
    def __init__(self, capacity: int = 100):
        """
        初始化情景记忆
        
        Args:
            capacity: 容量
        """
        self.capacity = capacity
        self.episodes: List[Dict[str, Any]] = []
    
    def add_episode(
        self,
        event: str,
        participants: List[str],
        details: Dict[str, Any]
    ) -> None:
        """添加情景"""
        episode = {
            "event": event,
            "participants": participants,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "importance": details.get("importance", 1)
        }
        self.episodes.append(episode)
        
        # 超过容量时，删除重要性最低的
        if len(self.episodes) > self.capacity:
            self.episodes.sort(key=lambda x: x["importance"], reverse=True)
            self.episodes = self.episodes[:self.capacity]
    
    def get_by_event(self, event_query: str) -> List[Dict[str, Any]]:
        """按事件查询"""
        return [
            e for e in self.episodes
            if event_query.lower() in e["event"].lower()
        ]
    
    def get_by_participant(self, participant: str) -> List[Dict[str, Any]]:
        """按参与者查询"""
        return [
            e for e in self.episodes
            if participant in e["participants"]
        ]
    
    def get_by_date_range(
        self,
        start: datetime,
        end: datetime
    ) -> List[Dict[str, Any]]:
        """按日期范围查询"""
        return [
            e for e in self.episodes
            if start <= datetime.fromisoformat(e["timestamp"]) <= end
        ]


class MemorySystem:
    """四层记忆系统"""
    
    def __init__(self):
        """初始化记忆系统"""
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
    
    def add_conversation(self, content: str, role: str = "user") -> None:
        """添加对话记忆"""
        self.short_term.add(content, role)
    
    def remember(self, key: str, value: Any, category: str = "general") -> None:
        """记住重要信息"""
        self.long_term.add(key, value, category)
    
    def recall(self, key: str) -> Optional[Any]:
        """回忆信息"""
        return self.long_term.get(key)
    
    def set_current_task(self, task: str) -> None:
        """设置当前任务"""
        self.working.set_task(task)
    
    def record_episode(
        self,
        event: str,
        participants: List[str],
        details: Dict[str, Any]
    ) -> None:
        """记录事件"""
        self.episodic.add_episode(event, participants, details)
    
    def get_full_context(self) -> Dict[str, Any]:
        """获取完整上下文"""
        return {
            "short_term": self.short_term.get_recent(),
            "working": self.working.get_context(),
            "relevant_long_term": [],
            "recent_episodes": self.episodic.episodes[-5:]
        }


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("Memory System Test")
    print("=" * 60)
    
    # 创建记忆系统
    memory = MemorySystem()
    
    # 测试短期记忆
    print("\nTest 1: Short-term memory")
    memory.add_conversation("Hello, I'm user", "user")
    memory.add_conversation("Hi! How can I help?", "assistant")
    print(f"  Recent messages: {len(memory.short_term.get_all())}")
    
    # 测试长期记忆
    print("\nTest 2: Long-term memory")
    memory.remember("user_name", "Alice", "personal")
    memory.remember("user_preference", "Python", "preferences")
    name = memory.recall("user_name")
    print(f"  Recalled name: {name}")
    
    # 测试工作记忆
    print("\nTest 3: Working memory")
    memory.set_current_task("Help with Python")
    memory.working.add_context("language", "Python")
    memory.working.add_context("level", "beginner")
    print(f"  Current task: {memory.working.current_task}")
    
    # 测试情景记忆
    print("\nTest 4: Episodic memory")
    memory.record_episode(
        "First meeting",
        ["Alice", "Bob"],
        {"topic": "Python tutorial"}
    )
    print(f"  Episodes: {len(memory.episodic.episodes)}")
    
    # 获取完整上下文
    print("\nFull Context:")
    context = memory.get_full_context()
    print(f"  Short-term messages: {len(context['short_term'])}")
    print(f"  Working task: {context['working']['task']}")
    print(f"  Recent episodes: {len(context['recent_episodes'])}")
    
    print("\nTest completed!")
