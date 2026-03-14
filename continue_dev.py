#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.4.1 - 继续开发：中间件层 + 可视化面板
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


VERSION = "1.4.1"


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
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return None


def continue_development():
    """继续开发中间件和可视化面板"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 继续开发")
    print("=" * 80)
    print("\n📋 任务: 实现中间件层 + 可视化面板")
    print("=" * 80)
    
    total_tokens = 0
    results = {}
    lock = threading.Lock()
    
    # ============ Phase 2: 实现中间件层 ============
    print("\n" + "=" * 80)
    print("[Phase 2] 实现中间件层")
    print("=" * 80)
    
    tasks = [
        {
            "id": 10,
            "name": "Qwen3-235B",
            "role": "中间件开发工程师",
            "task": "实现中间件层代码",
            "prompt": """请实现Symphony系统的中间件层Python代码。

要求：
1. ModelAdapter类 - 模型适配器基类
2. MessageRouter类 - 消息路由器
3. DataTransformer类 - 数据转换器
4. 包含完整的错误处理

请直接输出可运行的Python代码，用```python包裹。"""
        },
        {
            "id": 12,
            "name": "MiniMax-M2.5",
            "role": "前端开发工程师",
            "task": "实现可视化任务面板代码",
            "prompt": """请实现Symphony系统的可视化任务面板Python代码。

要求：
1. TaskPanel类 - 任务面板主类
2. ModelSelector类 - 模型选择器
3. ProgressTracker类 - 进度追踪器
4. 包含状态展示方法

请直接输出可运行的Python代码，用```python包裹。"""
        },
        {
            "id": 0,
            "name": "智谱GLM-4",
            "role": "测试工程师",
            "task": "编写集成测试代码",
            "prompt": """请为Symphony系统编写集成测试代码。

要求：
1. 测试中间件层功能
2. 测试任务面板功能
3. 测试模型协作流程
4. 包含assert断言

请直接输出可运行的Python测试代码，用```python包裹。"""
        }
    ]
    
    def develop_module(task):
        print(f"\n🔧 [{task['name']} ({task['role']})] 开发中: {task['task']}...")
        
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
                print(f"   ✅ 完成 - {result['tokens']} tokens")
            else:
                results[task["name"]] = {
                    "role": task["role"],
                    "task": task["task"],
                    "content": f"失败: {result.get('error', '未知') if result else '无响应'}",
                    "tokens": 0,
                    "success": False
                }
                print(f"   ❌ 失败")
    
    # 并行开发
    threads = []
    for task in tasks:
        t = threading.Thread(target=develop_module, args=(task,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # ============ Phase 3: 保存代码文件 ============
    print("\n" + "=" * 80)
    print("[Phase 3] 保存代码文件")
    print("=" * 80)
    
    # 提取并保存代码
    def save_code_file(content, filename, task_name):
        """从响应中提取代码并保存"""
        try:
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
# 开发者: {task_name}
# 生成时间: {datetime.now().isoformat()}
# 版本: {VERSION}

'''
            full_code = header + code
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(full_code)
            
            print(f"   ✅ {filename} 已保存")
            return True
        except Exception as e:
            print(f"   ❌ {filename} 保存失败: {e}")
            return False
    
    # 保存各模块
    for name, data in results.items():
        if data["success"]:
            if "中间件" in data["task"]:
                save_code_file(data["content"], "middleware.py", name)
            elif "面板" in data["task"]:
                save_code_file(data["content"], "task_panel.py", name)
            elif "测试" in data["task"]:
                save_code_file(data["content"], "test_integration.py", name)
    
    # ============ 最终报告 ============
    print("\n" + "=" * 80)
    print("📋 继续开发报告")
    print("=" * 80)
    
    total_tokens = sum(r["tokens"] for r in results.values())
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony v{VERSION} 继续开发
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 参与开发: {len(tasks)}位专家

📊 开发任务完成:
""")
    
    for task in tasks:
        status = "✅" if results.get(task["name"], {}).get("success") else "❌"
        tokens = results.get(task["name"], {}).get("tokens", 0)
        print(f"  {status} [{task['role']}] {task['name']}: {task['task']} ({tokens} tokens)")
    
    print(f"""
📁 生成的文件:
  • middleware.py - 中间件层
  • task_panel.py - 任务面板
  • test_integration.py - 集成测试

💰 总Token消耗: {total_tokens}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "tasks": tasks,
        "results": results,
        "total_tokens": total_tokens
    }


if __name__ == "__main__":
    report = continue_development()
    
    with open("continue_dev_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: continue_dev_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
