#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony 清理脚本 - 执行删除
"""

import os
from pathlib import Path

SYM_PATH = Path(r"C:\Users\Administrator\.openclaw\workspace\skills\symphony")

DELETE_PATTERNS = [
    "test_*.py",
    "*_test.py",
    "debug_*.py",
    "*_debug.py",
    "development.py",
    "improvement*.py",
    "workshop.py",
    "*_workshop.py",
    "*_improvement*.py",
    "example*.py",
    "demo_*.py",
    "weather_*.py",
    "*_v0*.py",
    "*_phase*.py",
    "*_team.py",
    "basic_test.py",
    "full_test.py",
    "simple_test.py",
    "quick_test.py",
    "deep_test*.py",
    "async_test*.py",
    "cleanup*.py",
    "release*.py",
    "prepare_*.py",
    "v0*.py",
    "*_final.py",
    "*_phase*.py",
    "quality_check.py",
    "quickstart.py",
    "quickstart_for_models.py",
    "search_news.py",
    "USAGE_EXAMPLE.py",
    "setup.py",
    "call_3_models*.py",
    "more_experts*.py",
    "direct_api_call.py",
    "simple_real_call*.py",
    "real_call*.py",
    "real_multi*.py",
    "model_free*.py",
    "treeclimb*.py",
    "seed_symphony*.py",
    "update_symphony*.py",
    "model_reporter.py",
    "check_*.py",
    "async_memory_core.py",
    "async_task_queue.py",
    "concurrency_monitor.py",
    "deadlock_detector.py",
    "fault_tolerance*.py",
    "memory_visualizer.py",
    "memory_importer*.py",
    "skill_fault*.py",
    "mcp_usage*.py",
    "streaming_output.py",
    "symphony_example.py",
    "symphony_enhanced_ui.py",
    "symphony_evolution*.py",
    "symphony_ui.py",
    "tianji*.py",
    "context_aware_memory.py",
    "memory_system_project.py",
    "config_updated.py",
    "dev_improved*.py",
    "improve_symphony.py",
    "howto_discussion.py",
    "full_symphony.py",
    "simple_symphony.py",
    "run_symphony*.py",
    "symphony_deep*.py",
    "model_discussion.py",
    "brainstorm_panel.py",
]

KEEP_FILES = {
    "brainstorm_panel_v2.py",
    "real_model_caller.py",
    "openclaw_config_loader.py",
    "symphony_core.py",
    "symphony_skill_wrapper.py",
    "model_manager.py",
    "skill_manager.py",
    "config.py",
    "main.py",
    "memory_system.py",
    "mcp_manager.py",
    "adapter_fix.py",
    "optimize_symphony.py",
    "symphony_debug.py",
    "adapter_development.py",
    "symphony_optimize_meeting.py",
    "cleanup_files.py",
}

def should_delete(filename):
    name = filename.name
    if name in KEEP_FILES:
        return False
    for pattern in DELETE_PATTERNS:
        import fnmatch
        if fnmatch.fnmatch(name, pattern):
            return True
    return False

def main():
    print("=" * 60)
    print("Symphony 清理 - 执行删除")
    print("=" * 60)
    
    py_files = list(SYM_PATH.glob("*.py"))
    
    to_delete = [f for f in py_files if should_delete(f)]
    
    print(f"将删除: {len(to_delete)} 个文件")
    print()
    
    # 执行删除
    deleted = 0
    for f in to_delete:
        try:
            f.unlink()
            print(f"  ✅ 删除: {f.name}")
            deleted += 1
        except Exception as e:
            print(f"  ❌ 失败: {f.name} - {e}")
    
    print()
    print(f"已删除: {deleted} 个文件")
    
    # 列出剩余文件
    remaining = list(SYM_PATH.glob("*.py"))
    print(f"剩余文件: {len(remaining)} 个")
    print()
    for f in sorted(remaining):
        print(f"  - {f.name}")

if __name__ == "__main__":
    main()
