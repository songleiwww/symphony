#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Symphony Memory Visualization
演示：交响记忆可视化
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("Demo: Symphony Memory Visualization")
print("演示：交响记忆可视化")
print("=" * 80)

# Create core and add sample memories
from symphony_core import create_symphony_core

print("\n[1/3] Creating Symphony Core with sample memories...")
core = create_symphony_core("demo_memory.json")

# Add sample memories
memories = [
    ("Phase 1 Complete: Quick Wins - QUICKSTART guide, examples/, model_reporter", 
     "long_term", 0.9, ["phase1", "quick-wins", "success"], "project"),
    ("Phase 2 Complete: Quality & Reliability - RELEASE_CHECKLIST, quality_check.py",
     "long_term", 0.9, ["phase2", "quality", "success"], "project"),
    ("Phase 3 In Progress: Core Foundation - Memory Integration & Visualization",
     "short_term", 0.8, ["phase3", "memory", "core"], "project"),
    ("12-model Deep Improvement Workshop - identified 20+ weaknesses",
     "long_term", 0.8, ["workshop", "improvement", "planning"], "discussion"),
    ("User preference: bilingual communication (Chinese + English)",
     "long_term", 0.7, ["preference", "language", "user"], "user"),
    ("Weather Station example created - multi-model weather reporting",
     "long_term", 0.6, ["example", "weather", "demo"], "example"),
    ("Tianji Broadcast example created - news broadcast system",
     "long_term", 0.6, ["example", "news", "demo"], "example"),
]

for content, mem_type, importance, tags, category in memories:
    core.add_memory(content, mem_type, importance, tags, category)

# Set preferences
core.set_preference("language", "bilingual")
core.set_preference("model_reporting", "detailed")
core.set_preference("theme", "light")

print("OK: Sample memories added")

# Show stats
stats = core.get_stats()
print(f"\n[2/3] Memory stats:")
print(f"  Total memories: {stats['total_memories']}")
print(f"  Long-term: {stats['long_term']}")
print(f"  Short-term: {stats['short_term']}")
print(f"  Preferences: {stats['total_preferences']}")

# Visualize memory
print("\n[3/3] Memory Visualization:")
from memory_visualizer import MemoryVisualizer

viz = MemoryVisualizer("demo_memory.json")
viz.render_ascii_dashboard()

# Clean up
if Path("demo_memory.json").exists():
    Path("demo_memory.json").unlink()

print("\n" + "=" * 80)
print("Demo Complete!")
print("演示完成！")
print("=" * 80)
