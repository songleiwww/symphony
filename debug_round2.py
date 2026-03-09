#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
继续Debug优化 - 第2轮
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from subagent_manager import SubAgentManager

# 继续优化
TASKS = [
    # 第1组: 核心稳定
    {"expert": "林稳定", "provider": "cherry-doubao", 
     "prompt": "最终稳定测试 - 运行所有模块，确保零错误。输出测试报告。"},
    {"expert": "张稳定", "provider": "cherry-doubao", 
     "prompt": "导入测试 - 验证所有模块可正常导入。"},
    {"expert": "王稳定", "provider": "cherry-doubao", 
     "prompt": "性能压测 - 测试交响在高负载下的表现。"},
    {"expert": "陈稳定", "provider": "cherry-doubao", 
     "prompt": "内存测试 - 检查是否有内存泄漏。"},
    # 第2组: 文档完善
    {"expert": "赵文档", "provider": "cherry-doubao", 
     "prompt": "完善README - 添加完整的安装、配置、运行说明。"},
    {"expert": "吴文档", "provider": "cherry-doubao", 
     "prompt": "API文档补全 - 确保所有公开方法都有文档。"},
    {"expert": "周文档", "provider": "cherry-doubao", 
     "prompt": "示例代码 - 编写完整的使用示例。"},
    {"expert": "李文档", "provider": "cherry-doubao", 
     "prompt": "故障排除指南 - 常见问题和解决方案。"},
]

def main():
    print("=" * 70)
    print("🎼 Debug优化第2轮 - 稳定 + 文档")
    print("=" * 70)
    
    manager = SubAgentManager()
    
    # 第1组
    print("\n🔧 第一组: 稳定性测试 (4人)")
    group1 = TASKS[:4]
    results1 = manager.execute_parallel(group1)
    
    s1 = sum(1 for r in results1 if r["result"].get("success"))
    t1 = sum(r["result"].get("total_tokens", 0) for r in results1)
    
    for r in results1:
        status = "✅" if r["result"].get("success") else "❌"
        print(f"{status} {r['expert']}")
    
    print(f"\n📈 稳定测试: {s1}/{len(group1)} | Token: {t1}")
    
    # 第2组
    print("\n📝 第二组: 文档完善 (4人)")
    group2 = TASKS[4:]
    results2 = manager.execute_parallel(group2)
    
    s2 = sum(1 for r in results2 if r["result"].get("success"))
    t2 = sum(r["result"].get("total_tokens", 0) for r in results2)
    
    for r in results2:
        status = "✅" if r["result"].get("success") else "❌"
        print(f"{status} {r['expert']}")
    
    print(f"\n📈 文档: {s2}/{len(group2)} | Token: {t2}")
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 第2轮总结")
    print("=" * 70)
    
    total = len(TASKS)
    total_s = s1 + s2
    total_t = t1 + t2
    
    print(f"\n📈 总计: {total_s}/{total} ({100*total_s/total:.0f}%)")
    print(f"📊 总Token: {total_t}")

if __name__ == "__main__":
    main()
