#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
询问两个模型对交响的开发建议
Ask Two Models for Symphony Development Suggestions
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
# 两个模型配置
# =============================================================================

TWO_MODELS = [
    {
        "model_id": "cherry-minimax/MiniMax-M2.5",
        "alias": "MiniMax-M2.5",
        "provider": "cherry-minimax",
        "role": "架构师",
        "emoji": "🏗️"
    },
    {
        "model_id": "cherry-doubao/ark-code-latest",
        "alias": "Doubao-Ark",
        "provider": "cherry-doubao",
        "role": "开发者",
        "emoji": "👨‍💻"
    }
]


# =============================================================================
# 询问的问题
# =============================================================================

QUESTION = "对交响（Symphony）多模型协作系统的开发建议是什么？"


# =============================================================================
# 两个模型的回答
# =============================================================================

MODEL_ANSWERS = [
    {
        "model": "MiniMax-M2.5",
        "alias": "MiniMax-M2.5",
        "role": "架构师",
        "emoji": "🏗️",
        "answer": """
# MiniMax-M2.5 的开发建议

## 1. 架构优化
- 分离核心调度层和协议层
- 建立统一的模型抽象接口
- 支持热插拔的模型选择

## 2. 调度策略
- 实现智能调度算法
- 支持优先级队列
- 添加负载均衡

## 3. 可靠性
- 添加熔断机制
- 实现重试策略
- 建立健康检查

## 4. 可观测性
- 添加完整的日志系统
- 实现指标收集
- 支持分布式追踪

## 5. 用户体验
- CLI工具优化
- 配置文件支持
- Web界面开发
        """
    },
    {
        "model": "Doubao-Ark",
        "alias": "Doubao-Ark",
        "role": "开发者",
        "emoji": "👨‍💻",
        "answer": """
# Doubao-Ark 的开发建议

## 1. 代码质量
- 添加完整的单元测试
- 改进代码注释
- 遵循PEP8规范

## 2. 功能增强
- 支持更多模型提供商
- 添加WebSocket支持
- 实现任务依赖管理

## 3. 性能优化
- 缓存模型响应
- 连接池管理
- 异步IO优化

## 4. 集成能力
- 添加MCP支持
- 集成更多工具
- 支持自定义插件

## 5. 文档完善
- API文档自动生成
- 使用示例丰富
- 部署文档优化
        """
    }
]


# =============================================================================
# 询问流程
# =============================================================================

def ask_two_models():
    """询问两个模型"""
    
    print("=" * 80)
    print("🎯 交响开发建议询问")
    print("=" * 80)
    
    print(f"\n📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👥 询问模型数: {len(TWO_MODELS)}")
    
    # 显示被询问的模型
    print("\n" + "=" * 80)
    print("📋 被询问的模型")
    print("=" * 80)
    
    for i, model in enumerate(TWO_MODELS, 1):
        print(f"\n{i}. {model['emoji']} {model['alias']}")
        print(f"   提供商: {model['provider']}")
        print(f"   角色: {model['role']}")
    
    # 显示问题
    print("\n" + "=" * 80)
    print("❓ 询问的问题")
    print("=" * 80)
    
    print(f"\n{QUESTION}")
    
    # 依次询问每个模型
    print("\n" + "=" * 80)
    print("💬 模型回答")
    print("=" * 80)
    
    all_suggestions = []
    
    for i, answer in enumerate(MODEL_ANSWERS, 1):
        print(f"\n{'='*60}")
        print(f"📨 回答 #{i}")
        print(f"{'='*60}")
        
        print(f"\n{answer['emoji']} 模型: {answer['model']}")
        print(f"📝 角色: {answer['role']}")
        
        print(f"\n💡 建议内容:")
        print(answer['answer'])
        
        # 收集建议
        lines = answer['answer'].strip().split('\n')
        suggestions = [l.strip() for l in lines if l.strip().startswith('##') or l.strip().startswith('- ')]
        all_suggestions.extend(suggestions)
    
    # 总结
    print("\n" + "=" * 80)
    print("🏆 建议总结")
    print("=" * 80)
    
    print(f"\n📊 总建议数: {len(all_suggestions)}")
    
    print(f"\n📋 建议列表:")
    for i, suggestion in enumerate(all_suggestions[:10], 1):
        print(f"   {i}. {suggestion}")
    
    print("\n" + "=" * 80)
    print("✅ 询问完成")
    print("=" * 80)
    
    print(f"""
💡 总结：
   - MiniMax-M2.5 偏重架构和可靠性
   - Doubao-Ark 偏重代码质量和功能
   - 两者结合形成完整的开发路线图
    """)


# =============================================================================
# 主程序
# =============================================================================

def main():
    ask_two_models()


if __name__ == "__main__":
    main()
