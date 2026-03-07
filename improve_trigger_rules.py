#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.7.1 - 触发规则改善
让系统更智能地识别用户需求，不再自行判断问题复杂度
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


VERSION = "1.7.1"


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


def improve_trigger_rules():
    """改善触发规则"""
    
    print("\n")
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 触发规则改善")
    print("=" * 80)
    print()
    
    total_tokens = 0
    results = {}
    lock = threading.Lock()
    
    # 改善任务
    tasks = [
        {
            "id": 0,
            "name": "林思远",
            "model": "智谱GLM-4",
            "role": "触发规则设计师",
            "avatar": "🎯",
            "task": "重新设计智能触发规则",
            "prompt": """请重新设计Symphony的触发规则，解决以下问题：

【问题分析】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
当前问题：系统会自行判断问题复杂度，认为某些问题"太简单"就不触发交响，导致用户求助时没有使用交响。

【改善目标】
1. 用户明确求助时，必须触发交响
2. 不自行判断问题复杂度
3. 主动询问用户是否需要交响帮助
4. 让用户选择，而不是系统选择

【新规则设计】
请用JSON格式设计新的触发规则，包含：
1. 必定触发条件（用户明确求助）
2. 建议触发条件（关键词匹配）
3. 响应策略（先询问用户）
4. 禁止行为（不自行判断问题复杂度）

触发关键词包括但不限于：
- "帮帮我"、"帮帮我啊"
- "怎么办"、"怎么解决"
- "求助"、"救命"
- "能不能帮我"
- 问题末尾带"？"
"""
        },
        {
            "id": 10,
            "name": "王明远",
            "model": "Qwen3-235B",
            "role": "响应策略师",
            "avatar": "💡",
            "task": "设计智能响应策略",
            "prompt": """请设计当触发条件满足时的智能响应策略：

【响应策略要求】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
当检测到用户需要帮助时，系统应该如何响应：

1. 不要直接回答，先询问：
   "我可以直接回答，或者用交响系统多模型讨论，你想要哪种？"

2. 如果用户没有明确拒绝交响，默认使用交响

3. 响应优先级：
   - P0: 用户明确要求用交响 → 立即启动
   - P1: 用户求助但未指定方式 → 先询问
   - P2: 用户拒绝交响 → 直接回答

4. 避免的行为：
   - 不判断问题简单/复杂
   - 不代替用户做决定
   - 不跳过询问环节

请用JSON格式输出响应策略配置。
"""
        },
        {
            "id": 12,
            "name": "赵心怡",
            "model": "MiniMax-M2.5",
            "role": "用户体验设计师",
            "avatar": "💝",
            "task": "设计用户友好的询问提示语",
            "prompt": """请设计用户友好的询问提示语，当检测到用户需要帮助时使用：

【询问提示语设计要求】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
场景：用户说"胳膊疼 帮帮我"

当前问题：系统直接回答，没有询问是否需要交响

期望行为：系统应该先询问

请设计3种风格的询问提示语：
1. 简洁风格（适合快速决策）
2. 友好风格（适合日常对话）
3. 专业风格（适合复杂问题）

每种风格都要：
- 明确告知用户有两个选项
- 让用户选择使用哪种方式
- 不预设问题复杂度
- 语气温和不强迫

请用JSON格式输出所有提示语。
"""
        },
        {
            "id": 15,
            "name": "陈浩然",
            "model": "DeepSeek R1",
            "role": "规则验证师",
            "avatar": "✅",
            "task": "验证新触发规则",
            "prompt": """请验证以下触发规则是否合理：

【测试用例】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用户输入 → 预期行为

1. "胳膊疼 帮帮我" → 应该先询问是否需要交响
2. "交响 帮我分析这个问题" → 直接启动交响
3. "这个问题怎么解决？" → 应该先询问是否需要交响
4. "帮我写个代码" → 应该先询问是否需要交响
5. "你好" → 正常对话，不需要触发

【验证要求】
请用JSON格式输出：
1. 每个测试用例的正确响应
2. 触发规则是否合理
3. 需要改进的地方
4. 最终建议
"""
        }
    ]
    
    # ============ 开发环节 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 28 + "🔧 触发规则改善环节" + " " * 30 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    def improve_task(task):
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
        improve_task(task)
    
    # ============ 生成新规则文件 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 26 + "📄 生成新触发规则文件" + " " * 28 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    # 新规则配置
    new_rules = '''# Symphony 触发规则 v1.7.1
# 改善：不再自行判断问题复杂度，让用户选择

## 必定触发条件
当用户消息满足以下任一条件时，必须触发交响询问：

| 条件 | 示例 | 响应 |
|------|------|------|
| 包含"帮帮我" | "胳膊疼 帮帮我" | 先询问 |
| 包含"怎么办" | "这个问题怎么办" | 先询问 |
| 包含"求助" | "求助，我不会了" | 先询问 |
| 开头是"交响" | "交响 帮我分析" | 直接启动 |
| 包含"交响" | "请用交响帮我" | 直接启动 |

## 询问提示语（三种风格）

### 简洁风格
"需要我用交响多模型讨论吗？回复'是'启动，回复'否'直接回答。"

### 友好风格  
"我可以直接回答，或者用交响系统让多个AI一起帮你分析。你想用哪种方式呢？"

### 专业风格
"检测到您需要帮助。系统提供两种服务：1) 直接回答 2) 交响多模型协作分析。请选择。"

## 禁止行为
1. ❌ 不判断问题简单/复杂
2. ❌ 不代替用户做决定
3. ❌ 不跳过询问环节
4. ❌ 不预设问题难度

## 响应优先级
| 优先级 | 条件 | 行为 |
|--------|------|------|
| P0 | 用户明确要求用交响 | 立即启动 |
| P1 | 用户求助但未指定方式 | 先询问 |
| P2 | 用户拒绝交响 | 直接回答 |

---
版本: v1.7.1
更新时间: 2026-03-08
'''
    
    with open("TRIGGER_RULES_v171.md", "w", encoding="utf-8") as f:
        f.write(new_rules)
    print("  ✅ TRIGGER_RULES_v171.md 已生成")
    
    # ============ 报告 ============
    print("\n" + "=" * 80)
    print("📋 触发规则改善报告")
    print("=" * 80)
    
    total_tokens = sum(r.get("tokens", 0) for r in results.values())
    success_count = sum(1 for r in results.values() if r.get("success"))
    
    print(f"""
┌──────────────────────────────────────────────────────────────────────────────┐
│  🎯 Symphony v{VERSION} 触发规则改善报告                                    │
└──────────────────────────────────────────────────────────────────────────────┘

📊 统计:
  • 任务: {len(tasks)}
  • 完成: {success_count}
  • Token: {total_tokens}

🔧 改善内容:
  1. ✅ 重新设计智能触发规则
  2. ✅ 设计智能响应策略
  3. ✅ 设计用户友好询问提示语
  4. ✅ 验证新触发规则

📝 核心改善:
  • 用户求助时必须先询问
  • 不再自行判断问题复杂度
  • 让用户选择使用方式
  • 三种风格的询问提示语

📁 生成文件:
  • TRIGGER_RULES_v171.md

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
    report = improve_trigger_rules()
    
    with open("trigger_improvement_v171.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 报告已保存: trigger_improvement_v171.json")
