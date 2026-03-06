#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3个模型 两轮对话 - 开发交流
3 Models, 2 Rounds - Development Discussion
"""

import sys
import json
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
# 3个模型定义
# =============================================================================

THREE_MODELS = [
    {
        "model_id": "MiniMax-M2.5",
        "alias": "MiniMax",
        "role": "战略架构师",
        "emoji": "🎯"
    },
    {
        "model_id": "ark-code-latest",
        "alias": "Doubao Ark",
        "role": "技术实现专家",
        "emoji": "⚙️"
    },
    {
        "model_id": "deepseek-v3.2",
        "alias": "DeepSeek",
        "role": "产品体验官",
        "emoji": "💡"
    }
]


# =============================================================================
# 两轮对话内容
# =============================================================================

TWO_ROUND_DIALOGUES = [
    # 第一轮
    {
        "round": 1,
        "speaker": "MiniMax",
        "role": "战略架构师",
        "emoji": "🎯",
        "message": """大家好！我是战略架构师MiniMax。

今天的话题是：我们先做哪个功能？

我建议先做：**统一错误处理和重试机制**

理由：
1. 这是技术基础，不然后面加功能会很痛苦
2. 可以提高系统可靠性
3. 工作量适中，1天就能完成

大家觉得呢？"""
    },
    {
        "round": 1,
        "speaker": "Doubao Ark",
        "role": "技术实现专家",
        "emoji": "⚙️",
        "message": """同意！我是技术实现专家Doubao Ark。

统一错误处理确实应该优先。我补充几点：

1. 可以做个 GlobalErrorHandler 类
2. 支持指数退避重试
3. 支持错误分类和自动恢复
4. 顺便把日志系统也加了

我预计今天就能写出来！""",
    },
    {
        "round": 1,
        "speaker": "DeepSeek",
        "role": "产品体验官",
        "emoji": "💡",
        "message": """好的！我是产品体验官DeepSeek。

我也同意！不过我有个建议：

能不能今天顺便把 **CLI工具的框架** 也搭了？

理由：
1. 用户最直观感受到的就是CLI
2. 搭框架很快，1-2小时
3. 后面再加功能就方便了

技术部分你们来，CLI框架我可以出设计！""",
    },
    
    # 第二轮
    {
        "round": 2,
        "speaker": "MiniMax",
        "role": "战略架构师",
        "emoji": "🎯",
        "message": """好！那我们今天的计划就定了！

📋 今日计划：
1. ✅ 统一错误处理和重试机制（Doubao Ark）
2. ✅ CLI工具框架（DeepSeek设计）
3. ✅ 日志系统（顺便）

好的，开始干活！有问题随时交流！""",
    },
    {
        "round": 2,
        "speaker": "Doubao Ark",
        "role": "技术实现专家",
        "emoji": "⚙️",
        "message": """收到！我现在就开始写 GlobalErrorHandler！

大概思路：
1. 错误分类：RETRYABLE / FATAL / WARNING
2. 重试策略：指数退避，最大3次
3. 错误回调：支持自定义错误处理
4. 日志集成：每次错误都记录

我先写个MVP，写完给大家看！""",
    },
    {
        "round": 2,
        "speaker": "DeepSeek",
        "role": "产品体验官",
        "emoji": "💡",
        "message": """好的！我来设计CLI框架！

初步设计的命令：
- `symphony start` - 启动系统
- `symphony task` - 执行任务
- `symphony status` - 查看状态
- `symphony list` - 列出模型

用Python的click库来写，很快的！

我先画个草图给大家看！""",
    }
]


# =============================================================================
# 输出对话
# =============================================================================

def output_dialogue():
    """输出对话"""
    print("=" * 80)
    print("🎭 3个模型 两轮对话 - 开发交流")
    print("=" * 80)
    
    print(f"\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模型: {', '.join([m['alias'] for m in THREE_MODELS])}")
    print(f"轮数: 2轮")
    
    # 输出每一轮
    current_round = 0
    for dialogue in TWO_ROUND_DIALOGUES:
        if dialogue['round'] != current_round:
            current_round = dialogue['round']
            print(f"\n{'=' * 80}")
            print(f"🎯 第 {current_round} 轮")
            print(f"{'=' * 80}")
        
        print(f"\n{dialogue['emoji']} {dialogue['speaker']} ({dialogue['role']}):")
        print(f"\n{dialogue['message']}")
        print(f"\n---")
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 对话总结")
    print("=" * 80)
    
    print(f"\n总消息数: {len(TWO_ROUND_DIALOGUES)}")
    print(f"模型数: {len(THREE_MODELS)}")
    print(f"轮数: 2轮")
    
    print(f"\n🎯 话题: 今天先做哪个功能？")
    print(f"✅ 结论: 统一错误处理 + CLI框架")
    print(f"📋 今日计划: 3个任务")
    
    # 保存到文件
    print("\n" + "=" * 80)
    print("💾 保存对话记录")
    print("=" * 80)
    
    chat_record = {
        "chat_time": datetime.now().isoformat(),
        "topic": "3个模型 两轮对话 - 开发交流",
        "models": THREE_MODELS,
        "rounds": 2,
        "dialogues": TWO_ROUND_DIALOGUES,
        "summary": {
            "total_messages": len(TWO_ROUND_DIALOGUES),
            "topic": "今天先做哪个功能？",
            "conclusion": "统一错误处理 + CLI框架",
            "today_plan": ["统一错误处理", "CLI框架", "日志系统"]
        }
    }
    
    output_file = Path("3_model_2_round_chat.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chat_record, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 对话记录已保存: {output_file}")
    
    print("\n" + "=" * 80)
    print("对话结束")
    print("=" * 80)
    print("\n品牌标语: 智韵交响，共创华章")


# =============================================================================
# 主程序
# =============================================================================

if __name__ == "__main__":
    output_dialogue()
