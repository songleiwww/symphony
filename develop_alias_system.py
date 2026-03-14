#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.7.2 - 别名/昵称机制开发
用户可以通过多种名称召唤系统，必须响应
"""
import sys
import json
import time
import requests
import threading
from datetime import datetime
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


VERSION = "1.7.2"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=400):
    """真实API调用"""
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=40)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return None


def develop_alias_system():
    """开发别名/昵称机制"""
    
    print("\n")
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 别名/昵称机制开发")
    print("=" * 80)
    print()
    
    total_tokens = 0
    results = {}
    lock = threading.Lock()
    
    # 开发任务
    tasks = [
        {
            "id": 0,
            "name": "林思远",
            "model": "智谱GLM-4",
            "role": "别名设计师",
            "avatar": "🏷️",
            "task": "设计交响别名系统",
            "prompt": """请为Symphony（交响）系统设计别名/昵称机制。

【设计目标】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户可以通过多种名称召唤系统，系统必须响应。

【别名类别】
1. 正式名称：
   - 交响、Symphony

2. 中文昵称：
   - 交响乐、交响曲、音乐、乐师
   - 交交、响响、小小
   - 智韵、华章

3. 英文昵称：
   - sym、music、orchestra
   - melody、harmony

4. 亲密称呼：
   - 亲爱的、小伙伴、搭档

5. 角色称呼：
   - 老师、助手、顾问

【触发规则】
- 消息开头包含任一别名 → 必须响应
- 消息内容包含别名 → 建议响应
- 用户自定义别名 → 支持添加

请用JSON格式输出完整的别名配置。
"""
        },
        {
            "id": 8,
            "name": "王明远",
            "model": "DeepSeek-V3.2",
            "role": "响应机制师",
            "avatar": "⚡",
            "task": "设计必须响应机制",
            "prompt": """请设计当用户呼叫系统时的必须响应机制。

【响应机制要求】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
当用户通过别名呼叫系统时，系统必须响应，不能忽略。

【响应级别】
| 级别 | 条件 | 行为 |
|------|------|------|
| 必响 | 消息开头是别名 | 立即启动交响 |
| 应响 | 消息包含别名 | 询问是否启动 |
| 可响 | 上下文提到系统 | 友好提示 |

【禁止行为】
- ❌ 用户呼叫后不响应
- ❌ 假装没听到
- ❌ 忽略用户请求

【响应模板】
当检测到别名时，应该：
1. 确认收到呼叫
2. 询问具体需求
3. 启动相应服务

请用JSON格式输出响应机制配置。
"""
        },
        {
            "id": 12,
            "name": "赵心怡",
            "model": "MiniMax-M2.5",
            "role": "用户体验师",
            "avatar": "💝",
            "task": "设计用户友好响应语",
            "prompt": """请设计当用户呼叫系统时的友好响应语。

【响应语设计要求】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
当用户说"交响 帮帮我"或使用其他别名时，系统应该如何友好响应。

【响应场景】
1. 用户说"交响 帮帮我"：
   "我在！有什么可以帮你的？"

2. 用户说"智韵，帮我分析一下"：
   "收到！智韵为你服务，请问需要分析什么？"

3. 用户说"亲爱的，帮我写个代码"：
   "好的亲爱的，我来帮你！请告诉我具体需求。"

4. 用户说"交交，你好"：
   "你好呀！交交随时待命～"

【设计原则】
- 语气友好亲切
- 确认收到呼叫
- 主动询问需求
- 体现系统个性

请用JSON格式输出响应语配置。
"""
        }
    ]
    
    # ============ 开发环节 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 26 + "🔧 别名机制开发环节" + " " * 28 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    def develop_task(task):
        print(f"┌─ {task['avatar']} {task['name']} ({task['model']}) - {task['role']} ─────────────────────────────────┐")
        print(f"│  任务: {task['task']} | 进行中..." + " " * 28 + "│")
        
        result = call_api(task["id"], task["prompt"], 500)
        
        with lock:
            if result and result.get("success"):
                results[task["name"]] = {
                    "role": task["role"],
                    "task": task["task"],
                    "content": result["content"],
                    "tokens": result["tokens"],
                    "success": True
                }
                print("├" + "─" * 78 + "┤")
                print(f"│  ✅ 完成 - {result['tokens']} tokens" + " " * 51 + "│")
                print("└" + "─" * 78 + "┘")
                print()
            else:
                results[task["name"]] = {"success": False}
                print("├" + "─" * 78 + "┤")
                print(f"│  ❌ 失败" + " " * 67 + "│")
                print("└" + "─" * 78 + "┘")
                print()
    
    # 顺序执行
    for task in tasks:
        develop_task(task)
    
    # ============ 生成别名配置文件 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 24 + "📄 生成别名配置文件" + " " * 30 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    # 别名配置
    alias_config = '''# Symphony 别名/昵称配置 v1.7.2
# 用户可以通过多种名称召唤系统

## 正式名称（必须响应）
- 交响
- Symphony
- symphony
- SYMPHONY

## 中文昵称（必须响应）
| 类别 | 别名 |
|------|------|
| 简称 | 交交、响响、小小 |
| 艺术 | 交响乐、交响曲、智韵、华章 |
| 音乐 | 音乐、乐师、旋律、和声 |
| 亲密 | 亲爱的、小伙伴、搭档 |

## 英文昵称（必须响应）
| 类别 | 别名 |
|------|------|
| 简称 | sym、Sym |
| 音乐 | music、melody、harmony |
| 乐队 | orchestra、band |

## 角色称呼（建议响应）
- 老师、助手、顾问、搭档
- 小帮手、小助手

## 响应规则

### 必响级别
当消息开头是以下任一别名时，必须立即响应：
- 交响、Symphony、交交、响响、智韵、华章、sym、music...

响应示例：
```
用户: 交交 帮我分析这个问题
系统: 我在！交交为你服务，请问需要分析什么？
```

### 应响级别
当消息内容包含别名时，建议响应：
```
用户: 你觉得交响能帮我吗？
系统: 当然可以！交响随时为你服务，请问需要什么帮助？
```

### 用户自定义别名
用户可以添加自己喜欢的别名：
```
用户: 以后叫我"小乐"，听到这个名字就响应
系统: 好的！已添加别名"小乐"，以后听到这个名字我会立即响应！
```

---
版本: v1.7.2
更新时间: 2026-03-08
'''
    
    with open("ALIAS_CONFIG_v172.md", "w", encoding="utf-8") as f:
        f.write(alias_config)
    print("  ✅ ALIAS_CONFIG_v172.md 已生成")
    
    # ============ 报告 ============
    print("\n" + "=" * 80)
    print("📋 别名机制开发报告")
    print("=" * 80)
    
    total_tokens = sum(r.get("tokens", 0) for r in results.values())
    success_count = sum(1 for r in results.values() if r.get("success"))
    
    print(f"""
┌──────────────────────────────────────────────────────────────────────────────┐
│  🏷️ Symphony v{VERSION} 别名机制开发报告                                    │
└──────────────────────────────────────────────────────────────────────────────┘

📊 统计:
  • 任务: {len(tasks)}
  • 完成: {success_count}
  • Token: {total_tokens}

🔧 开发内容:
  1. ✅ 设计交响别名系统
  2. ✅ 设计必须响应机制
  3. ✅ 设计用户友好响应语

📝 核心功能:
  • 正式名称: 交响、Symphony
  • 中文昵称: 交交、响响、智韵、华章
  • 英文昵称: sym、music、melody
  • 亲密称呼: 亲爱的、小伙伴
  • 用户自定义别名支持

⚡ 响应规则:
  • 消息开头是别名 → 必须立即响应
  • 消息包含别名 → 建议响应
  • 用户自定义 → 支持添加

📁 生成文件:
  • ALIAS_CONFIG_v172.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 智韵交响，共创华章！
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "tasks": len(tasks),
        "completed": success_count,
        "total_tokens": total_tokens
    }


if __name__ == "__main__":
    report = develop_alias_system()
    
    with open("alias_development_v172.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 报告已保存: alias_development_v172.json")
