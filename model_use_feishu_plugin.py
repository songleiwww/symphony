#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型使用飞书插件 - 演示功能
Models Use Feishu Plugin - Demo Function
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
# 模型定义
# =============================================================================

MODELS_WITH_FEISHU = [
    {
        "model_id": "MiniMax-M2.5",
        "alias": "MiniMax",
        "role": "战略架构师",
        "emoji": "🎯",
        "can_use_feishu": True
    },
    {
        "model_id": "ark-code-latest",
        "alias": "Doubao Ark",
        "role": "技术实现专家",
        "emoji": "⚙️",
        "can_use_feishu": True
    },
    {
        "model_id": "deepseek-v3.2",
        "alias": "DeepSeek",
        "role": "产品体验官",
        "emoji": "💡",
        "can_use_feishu": True
    }
]


# =============================================================================
# 飞书插件模拟
# =============================================================================

class FeishuPluginSimulator:
    """飞书插件模拟器"""
    
    def __init__(self):
        self.messages = []
    
    def send_message(self, model_alias: str, content: str):
        """模拟发送飞书消息"""
        message = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "from": model_alias,
            "content": content,
            "status": "sent"
        }
        self.messages.append(message)
        print(f"📤 [飞书插件] {model_alias} 发送了一条消息")
        return message
    
    def create_doc(self, model_alias: str, title: str, content: str):
        """模拟创建飞书文档"""
        print(f"📄 [飞书插件] {model_alias} 创建了文档: {title}")
        return {"doc_token": "mock_doc_123", "title": title}
    
    def list_messages(self):
        """列出所有消息"""
        return self.messages


# =============================================================================
# 对话内容
# =============================================================================

DIALOGUES_WITH_FEISHU = [
    {
        "speaker": "MiniMax",
        "role": "战略架构师",
        "emoji": "🎯",
        "action": "use_feishu_send",
        "message": """大家好！我是MiniMax。

我先用飞书插件发个消息测试一下！

📤 正在调用 feishu_doc 工具...""",
        "feishu_action": "send_message",
        "feishu_content": "【交响开发组】大家好！我是MiniMax，今天我们开发统一错误处理系统！"
    },
    {
        "speaker": "Doubao Ark",
        "role": "技术实现专家",
        "emoji": "⚙️",
        "action": "use_feishu_send",
        "message": """收到！我是Doubao Ark。

我也用飞书插件回复！

📤 正在调用 feishu_doc 工具...""",
        "feishu_action": "send_message",
        "feishu_content": "好的！我来写GlobalErrorHandler的实现代码！"
    },
    {
        "speaker": "DeepSeek",
        "role": "产品体验官",
        "emoji": "💡",
        "action": "use_feishu_create_doc",
        "message": """好的！我是DeepSeek。

我用飞书插件创建一个文档来保存测试计划！

📄 正在调用 feishu_doc 工具...""",
        "feishu_action": "create_doc",
        "feishu_title": "【交响】统一错误处理系统 - 测试计划",
        "feishu_content": "测试计划：\n1. 单元测试\n2. 集成测试\n3. 边界测试"
    },
    {
        "speaker": "MiniMax",
        "role": "战略架构师",
        "emoji": "🎯",
        "action": "use_feishu_send",
        "message": """太棒了！

我再用飞书插件发一条总结消息！

📤 正在调用 feishu_doc 工具...""",
        "feishu_action": "send_message",
        "feishu_content": "【交响开发组】今日进度：\n✅ GlobalErrorHandler 框架\n✅ 测试计划文档\n可以开始写代码了！"
    }
]


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主程序"""
    print("=" * 80)
    print("🤖 模型使用飞书插件 - 演示")
    print("=" * 80)
    
    print(f"\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模型: {', '.join([m['alias'] for m in MODELS_WITH_FEISHU])}")
    
    # 初始化飞书插件模拟器
    feishu_plugin = FeishuPluginSimulator()
    
    # 输出对话
    print("\n" + "=" * 80)
    print("💬 模型对话（使用飞书插件）")
    print("=" * 80)
    
    for dialogue in DIALOGUES_WITH_FEISHU:
        print(f"\n{dialogue['emoji']} {dialogue['speaker']} ({dialogue['role']}):")
        print(f"\n{dialogue['message']}")
        
        # 模拟飞书插件操作
        if dialogue['action'] == "use_feishu_send":
            feishu_plugin.send_message(
                model_alias=dialogue['speaker'],
                content=dialogue['feishu_content']
            )
            print(f"\n📨 飞书消息内容:")
            print(f"   {dialogue['feishu_content']}")
        
        elif dialogue['action'] == "use_feishu_create_doc":
            feishu_plugin.create_doc(
                model_alias=dialogue['speaker'],
                title=dialogue['feishu_title'],
                content=dialogue['feishu_content']
            )
            print(f"\n📄 飞书文档:")
            print(f"   标题: {dialogue['feishu_title']}")
        
        print(f"\n---")
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 飞书插件使用总结")
    print("=" * 80)
    
    messages = feishu_plugin.list_messages()
    print(f"\n总飞书消息数: {len(messages)}")
    print(f"\n飞书消息记录:")
    for i, msg in enumerate(messages, 1):
        print(f"\n{i}. [{msg['time']}] {msg['from']}:")
        print(f"   {msg['content']}")
    
    # 保存记录
    print("\n" + "=" * 80)
    print("💾 保存记录")
    print("=" * 80)
    
    record = {
        "time": datetime.now().isoformat(),
        "models": MODELS_WITH_FEISHU,
        "dialogues": DIALOGUES_WITH_FEISHU,
        "feishu_messages": messages,
        "summary": {
            "total_messages": len(DIALOGUES_WITH_FEISHU),
            "feishu_actions": len(messages)
        }
    }
    
    output_file = Path("model_use_feishu_plugin.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 记录已保存: {output_file}")
    
    print("\n" + "=" * 80)
    print("演示结束")
    print("=" * 80)
    print("\n品牌标语: 智韵交响，共创华章")


if __name__ == "__main__":
    main()
