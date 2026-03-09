#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
Symphony 触发与辅助系统 v1.0
============================================================================
功能：
1. 主被动触发关键词优化
2. 用户对话自动分析帮助功能

架构：
- 主动触发：轻量模型实时关键词匹配
- 被动触发：大模型深度语义预测
- 对话分析：多模型并行情感/意图识别
============================================================================
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ==================== 触发关键词配置 ====================

class TriggerConfig:
    """触发配置类"""
    
    # 主动触发关键词（高优先级，直接响应）
    ACTIVE_KEYWORDS = {
        # 交响相关
        "交响": ["交响", "交响调度", "多模型", "Symphony"],
        # 开发相关
        "开发": ["开发", "编程", "代码", "debug", "修复"],
        # 学习相关
        "学习": ["学习", "搜索", "研究", "调研"],
        # 帮助相关
        "帮助": ["帮助", "帮忙", "请问", "如何", "怎么"],
    }
    
    # 被动触发关键词（模糊意图时激活）
    PASSIVE_KEYWORDS = {
        "问题": ["为什么", "怎么办", "是不是", "对不对"],
        "不确定": ["不知道", "不确定", "随便", "都可以"],
    }
    
    # 紧急关键词（安全相关）
    EMERGENCY_KEYWORDS = {
        "危险": ["删除", "格式化", "危险", "病毒"],
        "隐私": ["密码", "私钥", "密钥", "token"],
    }


class IntentAnalyzer:
    """意图分析器"""
    
    def __init__(self):
        self.config = TriggerConfig()
        self.conversation_history: List[Dict] = []
        
    def analyze(self, message: str) -> Dict:
        """分析用户消息"""
        message = message.strip()
        
        # 1. 主动触发检测
        active_result = self._check_active_trigger(message)
        if active_result["triggered"]:
            return {
                "type": "active",
                "action": active_result["action"],
                "confidence": 0.9,
                "suggestion": active_result.get("suggestion", "")
            }
        
        # 2. 被动触发检测
        passive_result = self._check_passive_trigger(message)
        if passive_result["triggered"]:
            return {
                "type": "passive",
                "action": passive_result["action"],
                "confidence": 0.6,
                "suggestion": passive_result.get("suggestion", "")
            }
        
        # 3. 紧急关键词检测
        emergency_result = self._check_emergency(message)
        if emergency_result["triggered"]:
            return {
                "type": "emergency",
                "action": "warning",
                "confidence": 0.95,
                "suggestion": emergency_result.get("suggestion", "")
            }
        
        # 4. 正常对话
        return {
            "type": "normal",
            "action": "chat",
            "confidence": 0.5,
            "suggestion": ""
        }
    
    def _check_active_trigger(self, message: str) -> Dict:
        """检查主动触发"""
        for action, keywords in self.config.ACTIVE_KEYWORDS.items():
            for kw in keywords:
                if kw in message:
                    return {
                        "triggered": True,
                        "action": action,
                        "keyword": kw,
                        "suggestion": f"检测到{action}请求，使用交响多模型调度"
                    }
        return {"triggered": False}
    
    def _check_passive_trigger(self, message: str) -> Dict:
        """检查被动触发"""
        # 检查模糊意图
        if len(message) < 5:
            return {
                "triggered": True,
                "action": "clarify",
                "suggestion": "消息较短，可能需要更多信息来理解需求"
            }
        
        # 检查不确定表达
        for action, keywords in self.config.PASSIVE_KEYWORDS.items():
            for kw in keywords:
                if kw in message:
                    return {
                        "triggered": True,
                        "action": action,
                        "keyword": kw,
                        "suggestion": "检测到不确定意图，建议提供更多上下文"
                    }
        
        return {"triggered": False}
    
    def _check_emergency(self, message: str) -> Dict:
        """检查紧急关键词"""
        for action, keywords in self.config.EMERGENCY_KEYWORDS.items():
            for kw in keywords:
                if kw in message:
                    return {
                        "triggered": True,
                        "action": action,
                        "keyword": kw,
                        "suggestion": "检测到敏感操作，请确认是否安全"
                    }
        return {"triggered": False}


class AutoHelper:
    """自动帮助系统"""
    
    def __init__(self):
        self.analyzer = IntentAnalyzer()
        
    def process(self, message: str) -> Dict:
        """处理消息，返回辅助决策"""
        intent = self.analyzer.analyze(message)
        
        # 根据意图类型返回不同响应策略
        if intent["type"] == "active":
            return {
                "mode": "symphony",
                "multi_model": True,
                "reason": intent["suggestion"],
                "priority": "high"
            }
        elif intent["type"] == "passive":
            return {
                "mode": "enhanced",
                "multi_model": True,
                "reason": intent["suggestion"],
                "priority": "medium"
            }
        elif intent["type"] == "emergency":
            return {
                "mode": "safe",
                "multi_model": False,
                "reason": intent["suggestion"],
                "priority": "critical"
            }
        else:
            return {
                "mode": "normal",
                "multi_model": False,
                "reason": "普通对话",
                "priority": "low"
            }


# ==================== 导出接口 ====================

def analyze_intent(message: str) -> Dict:
    """分析用户意图"""
    analyzer = IntentAnalyzer()
    return analyzer.analyze(message)


def get_auto_help(message: str) -> Dict:
    """获取自动帮助决策"""
    helper = AutoHelper()
    return helper.process(message)


# ==================== 测试 ====================

if __name__ == "__main__":
    print("="*60)
    print("Symphony 触发与辅助系统测试")
    print("="*60)
    
    test_messages = [
        "交响调度3个模型",
        "帮我开发一个功能",
        "不知道选哪个好",
        "删除所有文件",
        "今天天气怎么样",
    ]
    
    helper = AutoHelper()
    
    for msg in test_messages:
        result = helper.process(msg)
        print(f"\n输入: {msg}")
        print(f"  类型: {result['mode']}")
        print(f"  多模型: {result['multi_model']}")
        print(f"  原因: {result['reason']}")
        print(f"  优先级: {result['priority']}")
