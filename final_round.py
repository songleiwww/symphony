#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终优化轮次 - 第3轮
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from subagent_manager import SubAgentManager

TASKS = [
    {"expert": "林最终", "provider": "cherry-doubao", 
     "prompt": "最终代码审查 - 确保每个模块都是生产级别质量。"},
    {"expert": "张最终", "provider": "cherry-doubao", 
     "prompt": "性能调优 - 优化关键路径，提升响应速度。"},
    {"expert": "王最终", "provider": "cherry-doubao", 
     "prompt": "安全审查 - 确保无安全漏洞。"},
    {"expert": "陈最终", "provider": "cherry-doubao", 
     "prompt": "最终集成测试 - 确保所有模块协同工作。"},
    {"expert": "赵最终", "provider": "cherry-doubao", 
     "prompt": "用户体验优化 - 确保易用性。"},
    {"expert": "吴最终", "provider": "cherry-doubao", 
     "prompt": "文档最终审阅 - 确保无遗漏。"},
]

def main():
    print("=" * 70)
    print("🎼 最终优化轮次 - 第3轮")
    print("=" * 70)
    
    manager = SubAgentManager()
    results = manager.execute_parallel(TASKS)
    
    success = sum(1 for r in results if r["result"].get("success"))
    tokens = sum(r["result"].get("total_tokens", 0) for r in results)
    
    for r in results:
        status = "✅" if r["result"].get("success") else "❌"
        print(f"{status} {r['expert']}")
    
    print(f"\n📈 总计: {success}/{len(TASKS)} ({100*success/len(TASKS):.0f}%)")
    print(f"📊 总Token: {tokens}")
    
    print("\n" + "=" * 70)
    print("🎉 所有优化轮次完成!")
    print("=" * 70)

if __name__ == "__main__":
    main()
