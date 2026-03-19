# -*- coding: utf-8 -*-
"""
飞书动画模块 - Phase 1: 文本加载提示
"""

LOADING_TEXT = "🔄 正在思考中..."

def create_loading_message():
    """创建加载提示消息"""
    return {
        "msg_type": "text",
        "content": {
            "text": LOADING_TEXT
        }
    }

def create_loading_card():
    """创建加载提示卡片"""
    return {
        "config": {
            "update_multi": True
        },
        "header": {
            "template": "blue",
            "title": {
                "tag": "plain_text",
                "content": "🔄 处理中"
            }
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "正在处理您的请求..."
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "loading",
                        "platform": "custom"
                    }
                ]
            }
        ]
    }

def create_result_card(title, content):
    """创建结果卡片"""
    return {
        "config": {
            "update_multi": True
        },
        "header": {
            "template": "green",
            "title": {
                "tag": "plain_text",
                "content": f"✅ {title}"
            }
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": content
                }
            }
        ]
    }

if __name__ == "__main__":
    print("=== 飞书动画模块 ===")
    print("1. 加载提示:", LOADING_TEXT)
    print("2. 卡片创建函数已就绪")
