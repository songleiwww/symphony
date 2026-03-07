#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Core - Memory Integrated
交响核心 - 记忆系统已集成
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json


@dataclass
class MemoryItem:
    """Single memory item"""
    id: str
    content: str
    memory_type: str
    importance: float
    tags: List[str]
    created_at: str
    access_count: int = 0
    last_accessed: Optional[str] = None


class SymphonyCore:
    """Symphony Core with integrated memory system"""
    
    def __init__(self, memory_path: str = "symphony_memory.json"):
        self.memory_path = Path(memory_path)
        self.memories: Dict[str, MemoryItem] = {}
        self.preferences: Dict[str, Any] = {}
        self.session_start = datetime.now().isoformat()
        
        # Load memory
        self._load_memory()
        
        # Record session start
        self.add_memory(
            f"Symphony session started at {self.session_start}",
            "short_term",
            0.5,
            ["session", "startup"],
            "system"
        )
    
    def _load_memory(self):
        """Load memory from file"""
        if self.memory_path.exists():
            try:
                data = json.loads(self.memory_path.read_text(encoding='utf-8'))
                for mem_data in data.get("memories", []):
                    mem = MemoryItem(**mem_data)
                    self.memories[mem.id] = mem
                self.preferences = data.get("preferences", {})
            except Exception as e:
                print(f"Warning: Could not load memory: {e}")
    
    def _save_memory(self):
        """Save memory to file"""
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "preferences": self.preferences,
            "memories": [
                {
                    "id": m.id,
                    "content": m.content,
                    "memory_type": m.memory_type,
                    "importance": m.importance,
                    "tags": m.tags,
                    "created_at": m.created_at,
                    "access_count": m.access_count,
                    "last_accessed": m.last_accessed
                }
                for m in self.memories.values()
            ]
        }
        self.memory_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def add_memory(self, content: str, memory_type: str, importance: float, 
                   tags: List[str], category: str) -> str:
        """Add a new memory (auto-saves)"""
        memory_id = f"mem_{len(self.memories) + 1}_{int(datetime.now().timestamp())}"
        mem = MemoryItem(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            tags=tags,
            created_at=datetime.now().isoformat()
        )
        self.memories[memory_id] = mem
        self._save_memory()
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """Get a memory by ID"""
        if memory_id in self.memories:
            mem = self.memories[memory_id]
            mem.access_count += 1
            mem.last_accessed = datetime.now().isoformat()
            self._save_memory()
            return mem
        return None
    
    def search_memories(self, query: str = "", tags: List[str] = None, 
                        min_importance: float = 0.0) -> List[MemoryItem]:
        """Search memories"""
        results = []
        for mem in self.memories.values():
            # Filter by importance
            if mem.importance < min_importance:
                continue
            # Filter by tags
            if tags:
                if not any(tag in mem.tags for tag in tags):
                    continue
            # Filter by query
            if query:
                if query.lower() not in mem.content.lower():
                    continue
            results.append(mem)
        # Sort by importance (descending)
        results.sort(key=lambda x: x.importance, reverse=True)
        return results
    
    def set_preference(self, key: str, value: Any):
        """Set a preference (auto-saves)"""
        self.preferences[key] = value
        self._save_memory()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference"""
        return self.preferences.get(key, default)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_memories": len(self.memories),
            "long_term": len([m for m in self.memories.values() if m.memory_type == "long_term"]),
            "short_term": len([m for m in self.memories.values() if m.memory_type == "short_term"]),
            "total_preferences": len(self.preferences),
            "session_start": self.session_start
        }


# Convenience function to create core
def create_symphony_core(memory_path: str = "symphony_memory.json") -> SymphonyCore:
    """Create a new Symphony core instance"""
    return SymphonyCore(memory_path)


if __name__ == "__main__":
    # Test core
    core = create_symphony_core()
    
    print("Symphony Core - Memory Integrated")
    print("交响核心 - 记忆系统已集成")
    print("=" * 60)
    
    # Add some memories
    core.add_memory(
        "Phase 1 Complete: Quick Wins",
        "long_term",
        0.8,
        ["phase1", "quick-wins", "success"],
        "project"
    )
    
    core.add_memory(
        "Phase 2 Complete: Quality & Reliability",
        "long_term",
        0.8,
        ["phase2", "quality", "success"],
        "project"
    )
    
    # Set preferences
    core.set_preference("language", "bilingual")
    core.set_preference("model_reporting", "detailed")
    
    # Show stats
    stats = core.get_stats()
    print(f"\nStats:")
    print(f"  Total memories: {stats['total_memories']}")
    print(f"  Long-term: {stats['long_term']}")
    print(f"  Preferences: {stats['total_preferences']}")
    
    print("\nOK: Symphony Core with integrated memory created!")
    print("=" * 60)



# ======== 基因故事导入 ========
# 以下代码将基因故事永久内置到系统核心
try:
    from gene_story import GENE_STORY, GENE_CONFIG, NAMING, PROMISES
    # 基因故事已加载
except ImportError:
    # 如果基因文件不存在，使用内置默认值
    pass
# ======== 基因故事导入结束 ========
