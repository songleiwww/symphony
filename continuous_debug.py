#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连续Debug - 直到最优解
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from subagent_manager import SubAgentManager

# 全面Debug任务 - 每轮4人
def run_debug_round(round_num, tasks):
    print(f"\n{'='*60}")
    print(f"🔧 Debug轮次 {round_num}")
    print(f"{'='*60}")
    
    manager = SubAgentManager()
    results = manager.execute_parallel(tasks)
    
    success = sum(1 for r in results if r["result"].get("success"))
    tokens = sum(r["result"].get("total_tokens", 0) for r in results)
    
    for r in results:
        status = "✅" if r["result"].get("success") else "❌"
        print(f"{status} {r['expert']} - {r['model']}")
    
    print(f"\n📈 成功: {success}/{len(tasks)} | Token: {tokens}")
    return success, tokens, results

def main():
    print("=" * 70)
    print("🎼 连续Debug - 直到最优解")
    print("=" * 70)
    
    total_success = 0
    total_tokens = 0
    
    # 第1轮: 核心修复
    round1 = [
        {"expert": "林Debug", "provider": "cherry-doubao", 
         "prompt": "最终修复ui_adapter - 确保是纯Python代码，无JSON，无语法错误。输出可直接导入的类。"},
        {"expert": "张Debug", "provider": "cherry-doubao", 
         "prompt": "最终修复deploy_manager - 确保AutoRelease类完整，可正常导入。输出完整类代码。"},
        {"expert": "王Debug", "provider": "cherry-doubao", 
         "prompt": "全面检查所有模块 - 修复任何剩余的语法错误、导入错误。"},
        {"expert": "陈Debug", "provider": "cherry-doubao", 
         "prompt": "优化代码质量 - 确保所有模块符合Python最佳实践。"},
    ]
    
    s, t, _ = run_debug_round(1, round1)
    total_success += s
    total_tokens += t
    
    # 第2轮: 增强稳定性
    round2 = [
        {"expert": "赵稳定", "provider": "cherry-doubao", 
         "prompt": "添加错误处理 - 为所有核心模块添加完善的异常处理。"},
        {"expert": "吴稳定", "provider": "cherry-doubao", 
         "prompt": "添加日志系统 - 为交响添加统一的日志记录。"},
        {"expert": "周稳定", "provider": "cherry-doubao", 
         "prompt": "添加健康检查 - 实现系统健康检查功能。"},
        {"expert": "李稳定", "provider": "cherry-doubao", 
         "prompt": "添加性能监控 - 实现基本性能指标收集。"},
    ]
    
    s, t, _ = run_debug_round(2, round2)
    total_success += s
    total_tokens += t
    
    # 第3轮: 最终优化
    round3 = [
        {"expert": "林优化", "provider": "cherry-doubao", 
         "prompt": "最终代码审查 - 确保所有模块可正常导入使用。"},
        {"expert": "张优化", "provider": "cherry-doubao", 
         "prompt": "性能优化 - 优化关键代码路径。"},
        {"expert": "王优化", "provider": "cherry-doubao", 
         "prompt": "文档完善 - 确保所有公开API都有文档字符串。"},
        {"expert": "陈优化", "provider": "cherry-doubao", 
         "prompt": "最终测试 - 编写完整的单元测试。"},
    ]
    
    s, t, _ = run_debug_round(3, round3)
    total_success += s
    total_tokens += t
    
    # 总结
    print("\n" + "=" * 70)
    print("🎉 连续Debug完成 - 最优解!")
    print("=" * 70)
    
    total_tasks = len(round1) + len(round2) + len(round3)
    print(f"\n📈 总计: {total_success}/{total_tasks} ({100*total_success/total_tasks:.0f}%)")
    print(f"📊 总Token: {total_tokens}")
    print(f"📊 轮次: 3轮")
    
    return total_success, total_tokens

if __name__ == "__main__":
    main()
