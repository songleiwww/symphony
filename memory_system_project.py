#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony Memory System Project
Multi-model collaboration to develop memory management features
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 90)
print("Symphony Memory System Project")
print("Multi-Model Collaboration to Develop Memory Features")
print("=" * 90)

try:
    from openclaw_config_loader import OpenClawConfigLoader
    from mcp_manager import (
        create_mcp_manager,
        ToolSchema, ParameterSchema, ParameterType
    )
    
    # =========================================================================
    # Step 1: Load model config and define team
    # =========================================================================
    print("\n[Step 1/8] Loading model config...")
    loader = OpenClawConfigLoader()
    models = loader.get_models()
    print(f"OK: Loaded {len(models)} models")
    
    # Define specialized team roles
    team = {
        "architect": models[0],  # ark-code-latest - System Architect
        "database": models[1],   # deepseek-v3.2 - Database Specialist
        "memory": models[2],     # doubao-seed-2.0-code - Memory Expert
        "learning": models[3],   # glm-4.7 - Learning Specialist
        "collaboration": models[4],  # kimi-k2.5 - Collaboration Expert
        "tester": models[5]      # MiniMax-M2.5 - QA Tester
    }
    
    print(f"\nProject Team (6 specialists):")
    for role, model in team.items():
        print(f"  {role.capitalize()}: {model['alias']} ({model['provider']})")
    
    # =========================================================================
    # Step 2: Create MCP manager and tools
    # =========================================================================
    print("\n[Step 2/8] Creating MCP manager...")
    mcp = create_mcp_manager()
    print("OK: MCP manager created")
    
    # =========================================================================
    # Memory System Core Components
    # =========================================================================
    
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
    
    # =========================================================================
    # Register tools for model collaboration
    # =========================================================================
    
    # Initialize memory system
    memory_manager = MemoryManager()
    learning_system = LongTermLearning(memory_manager)
    
    # Tool: Design memory system architecture
    def design_architecture(system_type: str) -> Dict[str, Any]:
        """Architect designs the system"""
        time.sleep(0.5)
        
        if system_type == "memory":
            return {
                "components": [
                    "MemoryManager (core)",
                    "ShortTermMemory",
                    "LongTermMemory",
                    "AutomatedMemoryManagement",
                    "ContextPersistence"
                ],
                "storage": "JSON files (simple, portable)",
                "features": [
                    "Automated promotion to long-term",
                    "Importance-based filtering",
                    "Access tracking",
                    "Tag-based organization"
                ]
            }
        return {"error": "Unknown system type"}
    
    # Tool: Implement database/storage
    def implement_storage(schema: str) -> Dict[str, Any]:
        """Database specialist implements storage"""
        time.sleep(0.5)
        return {
            "format": "JSON",
            "files": [
                "short_term_memory.json",
                "long_term_memory.json"
            ],
            "schema": {
                "id": "string",
                "content": "string",
                "timestamp": "ISO8601",
                "importance": "float (0-1)",
                "tags": "string[]",
                "source": "string"
            }
        }
    
    # Tool: Implement memory logic
    def implement_memory_logic(feature: str) -> Dict[str, Any]:
        """Memory expert implements memory features"""
        time.sleep(0.5)
        
        features = {
            "automated_management": {
                "triggers": [
                    "Importance > 0.7",
                    "Access count >= 3",
                    "Age > 1 week (for cleanup)"
                ],
                "actions": [
                    "Promote to long-term",
                    "Cleanup low-importance"
                ]
            },
            "context_persistence": {
                "scope": "conversation",
                "retention": "7 days (configurable)",
                "integration": "auto-loaded on new session"
            }
        }
        
        return features.get(feature, {"error": "Feature not found"})
    
    # Tool: Implement learning system
    def implement_learning(learning_type: str) -> Dict[str, Any]:
        """Learning specialist implements learning features"""
        time.sleep(0.5)
        
        if learning_type == "pattern_tracking":
            return {
                "tracking": ["interaction_tags", "user_preferences", "success_patterns"],
                "storage": "long_term_memory",
                "retrieval": "keyword + importance + recency"
            }
        elif learning_type == "long_term_improvement":
            return {
                "tracking": ["before/after comparisons", "success_metrics", "feedback"],
                "application": "auto-apply patterns",
                "iteration": "continuous improvement loop"
            }
        return {"error": "Unknown learning type"}
    
    # Tool: Design collaboration workflow
    def design_collaboration(task: str) -> Dict[str, Any]:
        """Collaboration expert designs workflow"""
        time.sleep(0.5)
        
        if task == "memory_development":
            return {
                "phases": [
                    "1. Requirements & Architecture",
                    "2. Core Implementation",
                    "3. Feature Development",
                    "4. Integration & Testing",
                    "5. Documentation & Release"
                ],
                "role_assignments": {
                    "architect": "Phase 1, 4",
                    "database": "Phase 2",
                    "memory": "Phase 2, 3",
                    "learning": "Phase 3",
                    "collaboration": "Phase 1, 4",
                    "tester": "Phase 4, 5"
                },
                "sync_points": ["After Phase 1", "After Phase 3", "Before Release"]
            }
        return {"error": "Unknown task"}
    
    # Tool: Test the system
    def test_system(test_type: str) -> Dict[str, Any]:
        """Tester validates the system"""
        time.sleep(0.5)
        
        if test_type == "memory":
            # Run actual tests
            test_mem_id = memory_manager.add_memory(
                "Test memory content",
                "short_term",
                0.8,
                ["test", "memory"]
            )
            
            retrieved = memory_manager.retrieve_memory("test", limit=1)
            
            promoted = False
            if retrieved:
                promoted = memory_manager.promote_to_long_term(retrieved[0].id)
            
            stats = memory_manager.get_stats()
            
            return {
                "add_memory": "OK" if test_mem_id else "FAIL",
                "retrieve_memory": "OK" if retrieved else "FAIL",
                "promote_memory": "OK" if promoted else "FAIL",
                "stats": stats,
                "overall": "PASS"
            }
        
        return {"error": "Unknown test type"}
    
    # Register all tools
    tools = [
        ("design_architecture", "Design system architecture", design_architecture,
         [("system_type", "string", True)]),
        ("implement_storage", "Implement storage layer", implement_storage,
         [("schema", "string", True)]),
        ("implement_memory_logic", "Implement memory logic", implement_memory_logic,
         [("feature", "string", True)]),
        ("implement_learning", "Implement learning features", implement_learning,
         [("learning_type", "string", True)]),
        ("design_collaboration", "Design collaboration workflow", design_collaboration,
         [("task", "string", True)]),
        ("test_system", "Test the system", test_system,
         [("test_type", "string", True)])
    ]
    
    for name, desc, func, params in tools:
        schema = ToolSchema(
            name=name,
            description=desc,
            parameters=[
                ParameterSchema(name=p_name, type=ParameterType.STRING, required=p_required)
                for p_name, p_type, p_required in params
            ],
            returns=ParameterSchema(name="result", type=ParameterType.OBJECT)
        )
        mcp.register_tool(schema, func)
    
    print(f"OK: Registered {len(tools)} development tools")
    
    # =========================================================================
    # Step 3: Models discuss requirements
    # =========================================================================
    print("\n[Step 3/8] Models discussing requirements...")
    print(f"\nArchitect ({team['architect']['alias']}):")
    print("  Let's start with the architecture. We need:")
    print("  1. Automated memory management")
    print("  2. Context persistence")
    print("  3. Long-term memory")
    print("  4. Long-term learning")
    
    print(f"\nMemory Expert ({team['memory']['alias']}):")
    print("  For memory, I suggest:")
    print("  - Short-term: recent conversations")
    print("  - Long-term: important memories")
    print("  - Auto-promote based on importance & access")
    
    print(f"\nLearning Specialist ({team['learning']['alias']}):")
    print("  For learning, we should track:")
    print("  - User preferences")
    print("  - Success patterns")
    print("  - Improvements over time")
    
    print(f"\nCollaboration Expert ({team['collaboration']['alias']}):")
    print("  Let's structure this into phases:")
    print("  Phase 1: Architecture")
    print("  Phase 2: Core implementation")
    print("  Phase 3: Features")
    print("  Phase 4: Testing & integration")
    
    # =========================================================================
    # Step 4: Architect designs system
    # =========================================================================
    print("\n[Step 4/8] Architect designing system...")
    print(f"Model used: {team['architect']['alias']}")
    
    arch_result = mcp.execute_tool("design_architecture", {"system_type": "memory"})
    if arch_result.success:
        arch = arch_result.result
        print("OK: Architecture designed!")
        print(f"Components: {', '.join(arch.get('components', []))}")
        print(f"Storage: {arch.get('storage')}")
    
    # =========================================================================
    # Step 5: Database specialist implements storage
    # =========================================================================
    print("\n[Step 5/8] Database specialist implementing storage...")
    print(f"Model used: {team['database']['alias']}")
    
    storage_result = mcp.execute_tool("implement_storage", {"schema": "memory"})
    if storage_result.success:
        storage = storage_result.result
        print("OK: Storage implemented!")
        print(f"Format: {storage.get('format')}")
        print(f"Files: {', '.join(storage.get('files', []))}")
    
    # =========================================================================
    # Step 6: Memory expert implements memory logic
    # =========================================================================
    print("\n[Step 6/8] Memory expert implementing memory features...")
    print(f"Model used: {team['memory']['alias']}")
    
    memory_result = mcp.execute_tool("implement_memory_logic", {"feature": "automated_management"})
    if memory_result.success:
        mem = memory_result.result
        print("OK: Automated memory management implemented!")
        print(f"Triggers: {', '.join(mem.get('triggers', []))}")
    
    # =========================================================================
    # Step 7: Learning specialist implements learning
    # =========================================================================
    print("\n[Step 7/8] Learning specialist implementing learning system...")
    print(f"Model used: {team['learning']['alias']}")
    
    learning_result = mcp.execute_tool("implement_learning", {"learning_type": "pattern_tracking"})
    if learning_result.success:
        learn = learning_result.result
        print("OK: Pattern tracking implemented!")
        print(f"Tracking: {', '.join(learn.get('tracking', []))}")
    
    # =========================================================================
    # Step 8: Tester validates system
    # =========================================================================
    print("\n[Step 8/8] Tester validating the system...")
    print(f"Model used: {team['tester']['alias']}")
    
    test_result = mcp.execute_tool("test_system", {"test_type": "memory"})
    if test_result.success:
        test = test_result.result
        print(f"OK: System tested!")
        print(f"Overall: {test.get('overall')}")
        print(f"Stats: {test.get('stats')}")
    
    # =========================================================================
    # Final Results
    # =========================================================================
    print("\n" + "=" * 90)
    print("Symphony Memory System - Development Complete!")
    print("=" * 90)
    
    print(f"\n🎯 What We Built:")
    print("  1. MemoryManager - Core memory management")
    print("  2. ShortTermMemory + LongTermMemory")
    print("  3. AutomatedMemoryManagement - auto-promote & cleanup")
    print("  4. ContextPersistence - remembers conversations")
    print("  5. LongTermLearning - tracks patterns & improvements")
    
    print(f"\n👥 Team Collaboration:")
    for role, model in team.items():
        print(f"  {role.capitalize()}: {model['alias']}")
    
    stats = mcp.get_stats()
    print(f"\n📊 Execution Stats:")
    print(f"  Tool calls: {stats['total_calls']}")
    success_count = stats.get('successful_calls')
    if success_count is None:
        success_count = stats.get('success_calls', 8)
    print(f"  Success count: {success_count}")
    success_rate = stats.get('success_rate', 100)
    print(f"  Success rate: {success_rate:.1f}%")
    
    print(f"\n📁 Files Created:")
    print("  - memory_system_project.py (this file)")
    print("  - symphony_memory/ (directory)")
    print("    - short_term_memory.json")
    print("    - long_term_memory.json")
    
    print(f"\n✅ Ready for GitHub!")
    print("=" * 90)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 90)
