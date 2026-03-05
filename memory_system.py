#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Memory System
=======================
Provides:
- Automated memory management
- Context persistence
- Long-term memory
- Long-term learning

Created by multi-model collaboration in Symphony.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MemoryEntry:
    """Single memory entry"""
    id: str
    content: str
    timestamp: str
    importance: float = 0.5
    tags: List[str] = field(default_factory=list)
    source: str = "system"
    access_count: int = 0
    last_access: Optional[str] = None


class MemoryManager:
    """
    Symphony Memory Manager
    Handles: automated memory management, context memory, long-term memory
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("symphony_memory")
        self.storage_path.mkdir(exist_ok=True)
        
        self.short_term: List[MemoryEntry] = []
        self.long_term: List[MemoryEntry] = []
        
        self._load_memory()
    
    def _get_memory_file(self, memory_type: str) -> Path:
        return self.storage_path / f"{memory_type}_memory.json"
    
    def _load_memory(self):
        """Load memory from disk"""
        for mem_type in ["short_term", "long_term"]:
            mem_file = self._get_memory_file(mem_type)
            if mem_file.exists():
                with open(mem_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    memory_list = self.short_term if mem_type == "short_term" else self.long_term
                    memory_list.clear()
                    for entry_data in data:
                        memory_list.append(MemoryEntry(**entry_data))
    
    def _save_memory(self, memory_type: str):
        """Save memory to disk"""
        mem_file = self._get_memory_file(memory_type)
        memory_list = self.short_term if memory_type == "short_term" else self.long_term
        
        data = []
        for entry in memory_list:
            data.append({
                "id": entry.id,
                "content": entry.content,
                "timestamp": entry.timestamp,
                "importance": entry.importance,
                "tags": entry.tags,
                "source": entry.source,
                "access_count": entry.access_count,
                "last_access": entry.last_access
            })
        
        with open(mem_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_memory(
        self,
        content: str,
        memory_type: str = "short_term",
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        source: str = "system"
    ) -> str:
        """Add a new memory"""
        entry = MemoryEntry(
            id=f"mem_{int(time.time() * 1000)}",
            content=content,
            timestamp=datetime.now().isoformat(),
            importance=importance,
            tags=tags or [],
            source=source
        )
        
        memory_list = self.short_term if memory_type == "short_term" else self.long_term
        memory_list.append(entry)
        self._save_memory(memory_type)
        
        return entry.id
    
    def retrieve_memory(
        self,
        query: str,
        memory_type: str = "both",
        limit: int = 5,
        min_importance: float = 0.0
    ) -> List[MemoryEntry]:
        """Retrieve relevant memories"""
        candidates = []
        
        if memory_type in ["both", "short_term"]:
            candidates.extend(self.short_term)
        if memory_type in ["both", "long_term"]:
            candidates.extend(self.long_term)
        
        # Filter by importance
        filtered = [m for m in candidates if m.importance >= min_importance]
        
        # Simple relevance scoring (keyword matching)
        query_lower = query.lower()
        scored = []
        for mem in filtered:
            score = 0.0
            content_lower = mem.content.lower()
            
            if query_lower in content_lower:
                score += 1.0
            for tag in mem.tags:
                if tag.lower() in query_lower:
                    score += 0.5
            
            score += mem.importance * 0.3
            score += min(mem.access_count * 0.1, 0.5)
            
            scored.append((score, mem))
        
        # Sort and limit
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [mem for (score, mem) in scored[:limit]]
        
        # Update access stats
        for mem in results:
            mem.access_count += 1
            mem.last_access = datetime.now().isoformat()
        
        return results
    
    def promote_to_long_term(self, memory_id: str) -> bool:
        """Promote a memory from short-term to long-term"""
        for i, mem in enumerate(self.short_term):
            if mem.id == memory_id:
                self.short_term.pop(i)
                self.long_term.append(mem)
                self._save_memory("short_term")
                self._save_memory("long_term")
                return True
        return False
    
    def auto_manage_memory(self):
        """
        Automated memory management
        - Moves important memories to long-term
        - Cleans up old, low-importance memories
        """
        # Promote high-importance memories
        promoted = 0
        for mem in list(self.short_term):
            if mem.importance > 0.7 and mem.access_count >= 3:
                self.promote_to_long_term(mem.id)
                promoted += 1
        
        # Cleanup old low-importance memories
        cleaned = 0
        cutoff = time.time() - (7 * 24 * 60 * 60)  # 1 week
        
        self.short_term = [
            mem for mem in self.short_term
            if mem.importance > 0.3 or 
               datetime.fromisoformat(mem.timestamp).timestamp() > cutoff
        ]
        
        self._save_memory("short_term")
        self._save_memory("long_term")
        
        return {
            "promoted_to_long_term": promoted,
            "cleaned_short_term": cleaned
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "total_count": len(self.short_term) + len(self.long_term),
            "storage_path": str(self.storage_path.absolute())
        }


class LongTermLearning:
    """
    Symphony Long-Term Learning
    Tracks patterns, preferences, and improvements over time
    """
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.patterns: Dict[str, int] = {}
        self.preferences: Dict[str, Any] = {}
        self.improvements: List[Dict] = []
    
    def record_interaction(self, context: str, outcome: str, tags: Optional[List[str]] = None):
        """Record an interaction for learning"""
        content = f"Interaction: {context[:100]}... Outcome: {outcome}"
        self.memory.add_memory(
            content=content,
            memory_type="long_term",
            importance=0.6,
            tags=tags or ["learning", "interaction"],
            source="learning"
        )
        
        # Update patterns
        for tag in (tags or []):
            self.patterns[tag] = self.patterns.get(tag, 0) + 1
    
    def record_preference(self, key: str, value: Any):
        """Record a user preference"""
        self.preferences[key] = value
        content = f"Preference: {key} = {value}"
        self.memory.add_memory(
            content=content,
            memory_type="long_term",
            importance=0.8,
            tags=["preference", key],
            source="preference"
        )
    
    def record_improvement(self, description: str, before: Any, after: Any):
        """Record an improvement"""
        improvement = {
            "description": description,
            "before": before,
            "after": after,
            "timestamp": datetime.now().isoformat()
        }
        self.improvements.append(improvement)
        
        content = f"Improvement: {description} - {before} -> {after}"
        self.memory.add_memory(
            content=content,
            memory_type="long_term",
            importance=0.9,
            tags=["improvement"],
            source="improvement"
        )
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get a summary of what has been learned"""
        return {
            "patterns": dict(sorted(self.patterns.items(), key=lambda x: x[1], reverse=True)[:10]),
            "preferences": self.preferences,
            "improvement_count": len(self.improvements),
            "recent_improvements": self.improvements[-5:]
        }


# Convenience function to create the system
def create_memory_system(storage_path: Optional[str] = None):
    """
    Create a complete Symphony memory system
    
    Returns:
        (memory_manager, learning_system)
    """
    memory = MemoryManager(storage_path)
    learning = LongTermLearning(memory)
    return memory, learning


if __name__ == "__main__":
    # Simple test
    print("Symphony Memory System")
    print("=" * 50)
    
    memory, learning = create_memory_system()
    
    # Test adding memory
    print("\nAdding test memory...")
    mem_id = memory.add_memory(
        "User prefers detailed explanations with examples",
        "short_term",
        0.9,
        ["preference", "user", "examples"],
        "user"
    )
    print(f"OK: Added memory {mem_id}")
    
    # Test retrieval
    print("\nRetrieving memory...")
    retrieved = memory.retrieve_memory("examples", limit=1)
    if retrieved:
        print(f"OK: Found: {retrieved[0].content[:50]}...")
    
    # Test auto-management
    print("\nRunning auto-memory-management...")
    result = memory.auto_manage_memory()
    print(f"OK: {result}")
    
    # Test learning
    print("\nRecording learning...")
    learning.record_preference("response_style", "detailed")
    learning.record_interaction("Helped user with code", "success", ["code", "success"])
    
    # Get stats
    print("\nSystem stats:")
    stats = memory.get_stats()
    print(f"  Total memories: {stats['total_count']}")
    print(f"  Storage: {stats['storage_path']}")
    
    print("\n" + "=" * 50)
    print("Memory system test complete!")
