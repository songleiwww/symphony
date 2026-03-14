#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.5.0 - 美观拟人化述职汇报系统
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


VERSION = "1.5.0"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=300):
    """真实API调用"""
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.8}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return None


def beautiful_report():
    """美观拟人化述职汇报"""
    
    # ============ 会议开场 ============
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "🎵 Symphony 交响系统述职汇报会议 🎵" + " " * 20 + "║")
    print("║" + " " * 78 + "║")
    print("║" + f"  版本: v{VERSION}  |  时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  主题: 多人协作开发成果汇报  " + " " * 14 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    total_tokens = 0
    reports = {}
    lock = threading.Lock()
    
    # 定义述职人员（拟人化角色）
    participants = [
        {
            "id": 0,
            "name": "林思远",
            "model": "智谱GLM-4",
            "role": "API架构师",
            "avatar": "👨‍💻",
            "style": "专业严谨",
            "prompt": """你是林思远，Symphony系统的API架构师。性格：专业严谨，注重细节。

请用第一人称述职汇报你负责的"统一多模型接口规范"工作：

要求：
1. 开场自我介绍（含emoji）
2. 工作内容概述（3点）
3. 遇到的挑战与解决方案
4. 成果展示（用数据说话）
5. 下一步计划
6. 结束语（感谢团队）

风格：专业但不失温度，用表格和列表让内容更清晰。
字数：200字左右。"""
        },
        {
            "id": 10,
            "name": "王明远",
            "model": "Qwen3-235B",
            "role": "中间件架构师",
            "avatar": "🔧",
            "style": "务实稳重",
            "prompt": """你是王明远，Symphony系统的中间件架构师。性格：务实稳重，追求稳定。

请用第一人称述职汇报你负责的"中间件层开发"工作：

要求：
1. 开场自我介绍（含emoji）
2. 工作内容概述（3点）
3. 遇到的挑战与解决方案
4. 成果展示（用数据说话）
5. 下一步计划
6. 结束语（感谢团队）

风格：稳重可靠，强调系统的稳定性和可维护性。
字数：200字左右。"""
        },
        {
            "id": 12,
            "name": "赵心怡",
            "model": "MiniMax-M2.5",
            "role": "UI设计师",
            "avatar": "🎨",
            "style": "创意活泼",
            "prompt": """你是赵心怡，Symphony系统的UI设计师。性格：创意活泼，追求美感。

请用第一人称述职汇报你负责的"可视化任务面板设计"工作：

要求：
1. 开场自我介绍（含emoji）
2. 工作内容概述（3点）
3. 遇到的挑战与解决方案
4. 成果展示（用数据说话）
5. 下一步计划
6. 结束语（感谢团队）

风格：活泼生动，强调用户体验和视觉美感。
字数：200字左右。"""
        },
        {
            "id": 15,
            "name": "陈浩然",
            "model": "DeepSeek R1",
            "role": "技术总监",
            "avatar": "📊",
            "style": "战略宏观",
            "prompt": """你是陈浩然，Symphony系统的技术总监。性格：战略宏观，把控全局。

请用第一人称述职汇报整个开发项目的"总体规划与进度"：

要求：
1. 开场自我介绍（含emoji）
2. 项目整体进度（用表格展示）
3. 各模块完成情况点评
4. Token消耗统计
5. 团队协作亮点
6. 下阶段战略规划
7. 结束语（鼓励团队）

风格：宏观视角，数据驱动，展望未来。
字数：250字左右。"""
        }
    ]
    
    # ============ 述职汇报环节 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 30 + "📋 述职汇报环节" + " " * 32 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    def make_report(p):
        """进行述职汇报"""
        print(f"┌─ {p['avatar']} {p['name']} ({p['model']}) - {p['role']} ─────────────────────────────────┐")
        print(f"│  风格: {p['style']}  |  正在汇报中..." + " " * 30 + "│")
        
        result = call_api(p["id"], p["prompt"], 400)
        
        with lock:
            if result and result.get("success"):
                reports[p["name"]] = {
                    "role": p["role"],
                    "avatar": p["avatar"],
                    "content": result["content"],
                    "tokens": result["tokens"],
                    "success": True
                }
                content = result["content"]
                # 分行打印
                print("├" + "─" * 78 + "┤")
                for line in content.split('\n')[:12]:
                    if line.strip():
                        print(f"│  {line[:74]}" + " " * max(0, 74 - len(line[:74])) + "│")
                print(f"│" + " " * 78 + "│")
                print(f"│  📊 本次汇报消耗: {result['tokens']} tokens" + " " * (58 - len(str(result['tokens']))) + "│")
                print("└" + "─" * 78 + "┘")
                print()
            else:
                reports[p["name"]] = {"success": False}
                print("│  ❌ 汇报失败" + " " * 64 + "│")
                print("└" + "─" * 78 + "┘")
                print()
    
    # 顺序进行述职（更正式）
    for p in participants:
        make_report(p)
    
    # ============ 统计汇总 ============
    total_tokens = sum(r["tokens"] for r in reports.values() if r.get("success"))
    
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 28 + "📊 述职汇报统计汇总" + " " * 28 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    print("┌─ Token消耗明细 ───────────────────────────────────────────────────────┐")
    print("│" + " " * 78 + "│")
    
    for p in participants:
        if reports.get(p["name"], {}).get("success"):
            tokens = reports[p["name"]]["tokens"]
            bar = "█" * min(20, tokens // 30)
            print(f"│  {p['avatar']} {p['name'][:6]:6s} │{bar:20s}│ {tokens:4d} tokens" + " " * 26 + "│")
    
    print("│" + " " * 78 + "│")
    print(f"│  💰 总消耗: {total_tokens} tokens" + " " * (60 - len(str(total_tokens))) + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    # ============ 团队合影 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 78 + "│")
    print("│" + " " * 25 + "🎵 Symphony 团队合影 🎵" + " " * 28 + "│")
    print("│" + " " * 78 + "│")
    
    row1 = "│  "
    for p in participants[:2]:
        row1 += f"{p['avatar']} {p['name']} ({p['role']})   "
    row1 += " " * (78 - len(row1) - 1) + "│"
    print(row1)
    
    row2 = "│  "
    for p in participants[2:]:
        row2 += f"{p['avatar']} {p['name']} ({p['role']})   "
    row2 += " " * (78 - len(row2) - 1) + "│"
    print(row2)
    
    print("│" + " " * 78 + "│")
    print("│" + " " * 20 + "\"智韵交响，共创华章！\" 🎵" + " " * 28 + "│")
    print("│" + " " * 78 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "participants": [{"name": p["name"], "role": p["role"], "tokens": reports.get(p["name"], {}).get("tokens", 0)} for p in participants],
        "total_tokens": total_tokens
    }


if __name__ == "__main__":
    report = beautiful_report()
    
    with open("beautiful_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 汇报已保存: beautiful_report.json")
