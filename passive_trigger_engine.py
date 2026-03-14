#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
被动触发引擎 - Passive Trigger Engine
当用户消息匹配特定模式时，自动激活交响功能
"""

import re
from typing import List, Dict, Callable, Optional
from datetime import datetime


class PassiveTriggerEngine:
    """被动触发引擎"""
    
    def __init__(self):
        self.triggers = []
        self.activation_history = []
        
    def register_trigger(self, pattern: str, priority: int = 0, 
                        description: str = "") -> None:
        """注册触发器"""
        self.triggers.append({
            "pattern": pattern,
            "priority": priority,
            "description": description,
            "regex": re.compile(pattern, re.IGNORECASE)
        })
        # 按优先级排序
        self.triggers.sort(key=lambda x: x["priority"], reverse=True)
        
    def should_activate(self, user_input: str) -> tuple[bool, Optional[Dict]]:
        """检查是否应该激活"""
        for trigger in self.triggers:
            match = trigger["regex"].search(user_input)
            if match:
                self.activation_history.append({
                    "time": datetime.now().isoformat(),
                    "input": user_input,
                    "trigger": trigger["description"]
                })
                return True, trigger
        return False, None
        
    def get_activation_count(self) -> int:
        """获取激活次数"""
        return len(self.activation_history)


# =============================================================================
# 被动触发器配置
# =============================================================================

PASSIVE_TRIGGERS = [
    # P0 - 核心关键词（精确匹配）
    {
        "pattern": r"^(交响|symphony)\s*",
        "priority": 100,
        "description": "核心词开头"
    },
    {
        "pattern": r"\s*(交响|symphony)\s*$",
        "priority": 100,
        "description": "核心词结尾"
    },
    # P1 - 动作关键词
    {
        "pattern": r"(讨论|开会|协作|头脑风暴|辩论|会诊)\s*[:：]",
        "priority": 80,
        "description": "动作词+冒号"
    },
    {
        "pattern": r"(让|请|叫)\s*(\w+\s*)+模型",
        "priority": 75,
        "description": "让XX模型"
    },
    # P2 - 需求关键词（需要更多上下文）
    {
        "pattern": r"(多|几个|多个)\s*模型",
        "priority": 60,
        "description": "多模型需求"
    },
    {
        "pattern": r"(\w+)\s*和\s*(\w+)\s*(\w+)",
        "priority": 50,
        "description": "三方对话模式"
    },
    # P3 - 英文触发
    {
        "pattern": r"(brainstorm|debate|meeting|collab)\s*[:\s]",
        "priority": 70,
        "description": "英文动作词"
    },
    # P4 - 智能推断（高级）
    {
        "pattern": r"(帮我|请帮我|能不能).*(分析|评估|对比|推荐)",
        "priority": 40,
        "description": "智能推断-需要分析"
    },
]


def create_passive_engine() -> PassiveTriggerEngine:
    """创建被动触发引擎"""
    engine = PassiveTriggerEngine()
    for trigger in PASSIVE_TRIGGERS:
        engine.register_trigger(
            pattern=trigger["pattern"],
            priority=trigger["priority"],
            description=trigger["description"]
        )
    return engine


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    engine = create_passive_engine()
    
    test_inputs = [
        "交响讨论：如何优化系统",
        "symphony开会",
        "让GPT和Claude讨论一下",
        "多模型头脑风暴",
        "帮我分析这个方案怎么样",
        "模型1和模型2模型3开会",
        "brainstorm: AI未来",
        "今天天气不错",
    ]
    
    print("=" * 60)
    print("🎯 被动触发引擎测试")
    print("=" * 60)
    
    for text in test_inputs:
        should_act, trigger = engine.should_activate(text)
        status = "✅ 激活" if should_act else "❌ 跳过"
        trigger_info = f" → {trigger['description']}" if trigger else ""
        print(f"{status} | {text}{trigger_info}")
    
    print("=" * 60)
    print(f"📊 总激活次数: {engine.get_activation_count()}")
    print("=" * 60)
