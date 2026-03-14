#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed Symphony Memory System with important project information
Creates long-term memory for multi-model collaboration
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("Seeding Symphony Memory System")
print("=" * 80)

try:
    from memory_system import MemoryManager, LongTermLearning, create_memory_system
    
    # Create memory system
    memory, learning = create_memory_system("symphony_long_term_memory")
    
    print(f"\nMemory system created at: {memory.storage_path.absolute()}")
    
    # =========================================================================
    # Seed project information (high importance)
    # =========================================================================
    print("\nAdding project information to long-term memory...")
    
    # Project basics
    memory.add_memory(
        "Symphony项目名称：交响（中文）、Symphony（英文/代码）。品牌标语：智韵交响，共创华章。",
        "long_term",
        1.0,
        ["project", "name", "branding"],
        "seed"
    )
    
    memory.add_memory(
        "Symphony GitHub仓库：https://github.com/songleiwww/symphony。唯一仓库，不创建重复仓库。",
        "long_term",
        1.0,
        ["project", "github", "repository"],
        "seed"
    )
    
    memory.add_memory(
        "Symphony本地路径：C:\\Users\\Administrator\\.openclaw\\workspace\\multi_agent_demo。",
        "long_term",
        1.0,
        ["project", "path", "local"],
        "seed"
    )
    
    # Model configuration
    memory.add_memory(
        "Symphony模型配置：17个模型，4个提供商。cherry-doubao 5个，cherry-minimax 1个，cherry-nvidia 10个，cherry-modelscope 2个。",
        "long_term",
        0.9,
        ["project", "models", "configuration"],
        "seed"
    )
    
    memory.add_memory(
        "Symphony主模型：cherry-doubao/ark-code-latest（Doubao Ark Code）。",
        "long_term",
        0.9,
        ["project", "models", "primary"],
        "seed"
    )
    
    # Important conventions
    memory.add_memory(
        "每次使用交响都要详细报告模型调度情况：使用了哪个模型、故障转移过程、最终使用的模型、问题报告。",
        "long_term",
        1.0,
        ["convention", "reporting", "models"],
        "seed"
    )
    
    memory.add_memory(
        "安全规则：发布前必须检查并移除所有敏感信息。模型Key只能用户自己使用，GitHub发布版绝对不能包含任何Key、密码、Token。",
        "long_term",
        1.0,
        ["convention", "security", "sensitive"],
        "seed"
    )
    
    # Memory system itself
    memory.add_memory(
        "Symphony记忆系统功能：MemoryManager（核心）、ShortTermMemory（短期）、LongTermMemory（长期）、AutomatedMemoryManagement（自动化管理）、ContextPersistence（上下文持久化）、LongTermLearning（长期学习）。",
        "long_term",
        0.9,
        ["memory", "system", "features"],
        "seed"
    )
    
    memory.add_memory(
        "记忆自动化规则：晋升条件（重要性>0.7 + 访问次数>=3），清理条件（重要性<=0.3 + 年龄>1周）。",
        "long_term",
        0.9,
        ["memory", "automation", "rules"],
        "seed"
    )
    
    # User information
    memory.add_memory(
        "用户信息：飞书用户ID ou_9fdef2dd0c9dfd043d5c5ddb2f66d2b7，GitHub账号 songleiwww（songlei_www@qq.com）。",
        "long_term",
        0.8,
        ["user", "information", "identity"],
        "seed"
    )
    
    # Core files
    memory.add_memory(
        "Symphony核心文件：config.py（17个模型）、model_manager.py（模型管理）、fault_tolerance.py（故障处理）、skill_manager.py（技能管理）、mcp_manager.py（MCP工具）、symphony_core.py（统一调度）、memory_system.py（记忆系统）、openclaw_config_loader.py（配置加载器）。",
        "long_term",
        0.8,
        ["project", "files", "core"],
        "seed"
    )
    
    # =========================================================================
    # Seed preferences and learning
    # =========================================================================
    print("\nSeeding preferences and learning...")
    
    learning.record_preference("response_style", "detailed")
    learning.record_preference("model_reporting", "always_detailed")
    learning.record_preference("security_check", "before_release")
    learning.record_preference("repository", "single_only")
    
    learning.record_interaction(
        "Developed Symphony Memory System with multi-model collaboration",
        "success",
        ["memory", "development", "success", "multi-model"]
    )
    
    learning.record_interaction(
        "Fixed Windows encoding issues in multiple test files",
        "success",
        ["bug", "fix", "encoding", "windows"]
    )
    
    learning.record_improvement(
        "Memory system development",
        "no memory system",
        "complete memory system with learning"
    )
    
    learning.record_improvement(
        "Model configuration",
        "two separate configs",
        "auto-loading from OpenClaw"
    )
    
    # =========================================================================
    # Verify and show stats
    # =========================================================================
    print("\nVerifying memory...")
    
    stats = memory.get_stats()
    print(f"\nMemory System Stats:")
    print(f"  Total memories: {stats['total_count']}")
    print(f"  Long-term: {stats['long_term_count']}")
    print(f"  Short-term: {stats['short_term_count']}")
    
    print(f"\nLearning Summary:")
    summary = learning.get_learning_summary()
    print(f"  Preferences: {list(summary['preferences'].keys())}")
    print(f"  Patterns: {list(summary['patterns'].keys())}")
    print(f"  Improvements: {summary['improvement_count']}")
    
    print("\n" + "=" * 80)
    print("Symphony Long-Term Memory Seeded Successfully!")
    print("=" * 80)
    print("\nThis memory is now available for multi-model collaboration!")
    print("\nTo use:")
    print("  from memory_system import create_memory_system")
    print("  memory, learning = create_memory_system('symphony_long_term_memory')")
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
