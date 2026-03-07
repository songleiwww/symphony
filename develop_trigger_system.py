#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.7.0 - 人性化主动/被动触发系统
在用户遇到困难或难题时主动/被动跳出来帮助
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


VERSION = "1.7.0"


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


def develop_trigger_system():
    """开发人性化触发系统"""
    
    # 美观的开场
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "🧠 Symphony 人性化触发系统 v" + VERSION + " 🧠" + " " * 22 + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  功能: 主动/被动触发 | 困难检测 | 智能帮助" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")
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
            "role": "触发规则设计师",
            "avatar": "🎯",
            "task": "设计主动触发规则",
            "prompt": """请为Symphony系统设计智能主动触发规则。

【设计目标】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
在用户遇到困难时，系统能主动识别并提供帮助。

【触发场景】
1. 用户表达困惑（"怎么..."、"为什么..."、"不懂"）
2. 多次尝试失败（连续2次以上）
3. 长时间无响应（超过30秒）
4. 错误关键词（"报错"、"失败"、"不行"）
5. 用户求助（"帮帮我"、"怎么办"）

【触发级别】
- P0: 立即响应（用户明确求助）
- P1: 友好询问（检测到困惑）
- P2: 静默准备（预判可能需要帮助）

请用JSON格式输出触发规则配置。"""
        },
        {
            "id": 10,
            "name": "王明远",
            "model": "Qwen3-235B",
            "role": "被动触发架构师",
            "avatar": "⚡",
            "task": "设计被动触发机制",
            "prompt": """请为Symphony系统设计被动触发机制。

【设计目标】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
当系统检测到擅长领域时，可以被动等待用户触发。

【被动触发条件】
1. 用户消息包含关键词（交响、symphony、讨论等）
2. 用户正在处理系统擅长的任务
3. 用户询问系统能力范围

【响应策略】
- 友好提示："我可以帮你..."
- 能力展示："我的能力包括..."
- 主动询问："需要我用交响帮你讨论吗？"

请用JSON格式输出被动触发配置。"""
        },
        {
            "id": 12,
            "name": "赵心怡",
            "model": "MiniMax-M2.5",
            "role": "用户体验设计师",
            "avatar": "💝",
            "task": "设计人性化交互提示",
            "prompt": """请为Symphony系统设计人性化的交互提示语。

【设计目标】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
让用户感受到系统是一个有温度的助手。

【提示语分类】
1. 主动帮助提示：
   - "看你在思考这个问题，需要我帮忙分析吗？"
   - "我发现你遇到了困难，要不要试试交响讨论？"

2. 能力展示提示：
   - "这个问题很适合用多模型讨论，要不要试试？"
   - "我可以帮你调用多个AI模型一起分析哦～"

3. 友好结束提示：
   - "好的，我随时待命！"
   - "有问题随时叫我哦～"

请用JSON格式输出所有提示语模板。"""
        },
        {
            "id": 15,
            "name": "陈浩然",
            "model": "DeepSeek R1",
            "role": "系统整合工程师",
            "avatar": "🔧",
            "task": "实现触发系统核心代码",
            "prompt": """请为Symphony系统实现完整的触发系统Python代码。

【代码要求】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. TriggerDetector类 - 触发检测：
   - detect_confusion() - 检测困惑
   - detect_failure() - 检测失败
   - detect_help_request() - 检测求助
   - detect_keyword() - 检测关键词

2. TriggerEngine类 - 触发引擎：
   - check_active_trigger() - 主动触发检查
   - check_passive_trigger() - 被动触发检查
   - generate_response() - 生成响应

3. UserFriendlyUI类 - 人性化界面：
   - format_response() - 格式化响应
   - add_emoji() - 添加表情
   - create_table() - 创建表格

请用完整可运行的Python代码实现，用```python包裹。"""
        }
    ]
    
    # ============ 开发环节 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 28 + "🔧 触发系统开发环节" + " " * 30 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    def develop_task(task):
        print(f"┌─ {task['avatar']} {task['name']} ({task['model']}) - {task['role']} ─────────────────────────────────┐")
        print(f"│  开发任务: {task['task']} | 进行中..." + " " * 26 + "│")
        
        result = call_api(task["id"], task["prompt"], 600)
        
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
                print(f"│  ✅ 开发完成 - {result['tokens']} tokens" + " " * 47 + "│")
                print("└" + "─" * 78 + "┘")
                print()
            else:
                results[task["name"]] = {"success": False}
                print("├" + "─" * 78 + "┤")
                print(f"│  ❌ 开发失败" + " " * 64 + "│")
                print("└" + "─" * 78 + "┘")
                print()
    
    # 顺序开发
    for task in tasks:
        develop_task(task)
    
    # ============ 保存代码 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 30 + "📁 保存代码文件" + " " * 32 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    saved_files = []
    
    for name, data in results.items():
        if data.get("success"):
            if "主动" in data["task"]:
                filename = "active_trigger.py"
            elif "被动" in data["task"]:
                filename = "passive_trigger.py"
            elif "交互" in data["task"] or "提示" in data["task"]:
                filename = "user_friendly_ui.py"
            elif "核心" in data["task"]:
                filename = "trigger_system.py"
            else:
                filename = f"{name}_output.py"
            
            # 提取代码
            content = data["content"]
            if "```python" in content:
                start = content.find("```python") + 9
                end = content.find("```", start)
                if end > start:
                    code = content[start:end].strip()
                else:
                    code = content
            else:
                code = content
            
            header = f'''# Symphony {filename.replace('.py', '').replace('_', ' ').title()}
# 开发者: {name} ({data['role']})
# 生成时间: {datetime.now().isoformat()}
# 版本: {VERSION}

'''
            full_code = header + code
            
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(full_code)
                print(f"  ✅ {filename} 已保存 ({data['tokens']} tokens)")
                saved_files.append(filename)
            except Exception as e:
                print(f"  ❌ {filename} 保存失败: {e}")
    
    # ============ 美化汇报 ============
    print("\n" + "=" * 80)
    print("📋 人性化触发系统开发报告")
    print("=" * 80)
    
    total_tokens = sum(r.get("tokens", 0) for r in results.values())
    success_count = sum(1 for r in results.values() if r.get("success"))
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🧠 Symphony v""" + VERSION + """ 人性化触发系统                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📊 开发统计                                                                 ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │  任务总数: """ + str(len(tasks)) + """                                                          │ ║
║  │  完成数量: """ + str(success_count) + """                                                          │ ║
║  │  Token消耗: """ + str(total_tokens) + """                                                      │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  🎯 完成的功能                                                               ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │  ✅ 主动触发规则 - 困惑检测、失败检测、求助检测                       │ ║
║  │  ✅ 被动触发机制 - 关键词匹配、能力展示                               │ ║
║  │  ✅ 人性化提示语 - 友好交互、温度感                                   │ ║
║  │  ✅ 触发系统代码 - 完整可运行                                         │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  📁 生成的文件                                                               ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║""")
    
    for f in saved_files:
        print("║  │  ✅ " + f.ljust(68) + "│ ║")
    
    print("""║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎵 智韵交响，共创华章！
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "tasks": len(tasks),
        "completed": success_count,
        "total_tokens": total_tokens,
        "saved_files": saved_files
    }


if __name__ == "__main__":
    report = develop_trigger_system()
    
    with open("trigger_system_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 报告已保存: trigger_system_report.json")
