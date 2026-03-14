#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型技能调用系统 - 模型与我交互演示
Model Skill Interaction System - Model talks to me
"""

import sys
from datetime import datetime
from pathlib import Path


# =============================================================================
# 修复Windows编码
# =============================================================================

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# =============================================================================
# 可用技能
# =============================================================================

SKILLS = {
    "weather": {
        "name": "天气查询",
        "description": "查询城市天气",
        "syntax": "skill:weather:城市"
    },
    "calculate": {
        "name": "数学计算",
        "description": "执行数学运算",
        "syntax": "skill:calculate:表达式"
    },
    "search": {
        "name": "网络搜索",
        "description": "搜索信息",
        "syntax": "skill:search:关键词"
    },
    "memory": {
        "name": "记忆存储",
        "description": "存储信息到记忆",
        "syntax": "skill:memory:key=value"
    },
    "file": {
        "name": "文件操作",
        "description": "读写文件",
        "syntax": "skill:file:操作:路径"
    }
}


# =============================================================================
# 模型消息模拟
# =============================================================================

MODEL_MESSAGES = [
    {
        "model": "MiniMax-M2.5",
        "message": "调用技能: skill:weather:北京",
        "response": "🌤️ 北京天气：晴，15°C，东南风2级"
    },
    {
        "model": "MiniMax-M2.5", 
        "message": "调用技能: skill:calculate:(100+200)*3",
        "response": "🧮 计算结果：900"
    },
    {
        "model": "MiniMax-M2.5",
        "message": "调用技能: skill:search:交响 多模型协作",
        "response": "🔍 搜索结果：Symphony是一个多模型协作系统..."
    },
    {
        "model": "MiniMax-M2.5",
        "message": "【与我交互】你好！我是MiniMax，我想查询上海的天气",
        "response": "✅ 收到！让我查询上海天气...\n🌤️ 上海天气：多云，18°C，东风3级"
    },
    {
        "model": "MiniMax-M2.5",
        "message": "【与我交互】帮我计算 256 * 128",
        "response": "✅ 收到！让我计算...\n🧮 256 × 128 = 32,768"
    }
]


# =============================================================================
# 交互演示
# =============================================================================

def demonstrate_model_skill_interaction():
    """演示模型技能调用与我交互"""
    
    print("=" * 80)
    print("🎯 模型技能调用系统 - 与我交互演示")
    print("=" * 80)
    
    print(f"\n📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📚 可用技能: {len(SKILLS)}个")
    
    # 显示可用技能
    print("\n" + "=" * 80)
    print("📚 可用技能列表")
    print("=" * 80)
    
    for skill_id, skill in SKILLS.items():
        print(f"\n🔧 {skill['name']}")
        print(f"   描述: {skill['description']}")
        print(f"   语法: {skill['syntax']}")
    
    # 模型调用演示
    print("\n" + "=" * 80)
    print("🤖 模型调用技能演示")
    print("=" * 80)
    
    for i, msg in enumerate(MODEL_MESSAGES, 1):
        print(f"\n{'='*40}")
        print(f"📨 消息 #{i}")
        print(f"{'='*40}")
        
        print(f"\n🤖 模型: {msg['model']}")
        print(f"📝 消息: {msg['message']}")
        
        print(f"\n✅ 我的响应: {msg['response']}")
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 交互统计")
    print("=" * 80)
    
    print(f"\n总消息数: {len(MODEL_MESSAGES)}")
    print(f"技能调用数: 3")
    print(f"直接交互数: 2")
    
    print("\n" + "=" * 80)
    print("✅ 演示完成")
    print("=" * 80)
    
    print("""
💡 这个演示展示了：
   1. 模型可以调用各种技能（天气、计算、搜索）
   2. 模型可以直接与我交互
   3. 我能理解模型的消息并给出响应

⚠️ 注意：这个演示是模拟的，不是真实的模型调用
    """)


# =============================================================================
# 主程序
# =============================================================================

def main():
    demonstrate_model_skill_interaction()


if __name__ == "__main__":
    main()
