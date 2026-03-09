#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继续修复剩余问题
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from subagent_manager import SubAgentManager

# 修复任务
TASKS = [
    {"expert": "林修复", "provider": "cherry-doubao", 
     "prompt": "修复user_friendly_ui.py - 移除JSON块，转换为标准Python字典。输出修复后的完整代码。"},
    {"expert": "张修复", "provider": "cherry-doubao", 
     "prompt": "修复auto_release.py - 添加AutoRelease类，实现完整的部署管理功能。输出完整代码。"},
]

def main():
    print("=" * 60)
    print("🔧 继续修复剩余问题")
    print("=" * 60)
    
    manager = SubAgentManager()
    results = manager.execute_parallel(TASKS)
    
    success = sum(1 for r in results if r["result"].get("success"))
    tokens = sum(r["result"].get("total_tokens", 0) for r in results)
    
    for r in results:
        status = "✅" if r["result"].get("success") else "❌"
        print(f"{status} {r['expert']} - {r['model']}")
    
    print(f"\n📈 成功: {success}/{len(TASKS)} | Token: {tokens}")

if __name__ == "__main__":
    main()
