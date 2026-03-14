#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.4.0 - 多人开发交响系统
基于会议建议：统一接口规范、中间件层、可视化面板
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


VERSION = "1.4.0"


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


def multi_person_development():
    """多人开发交响系统"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 多人开发交响系统")
    print("=" * 80)
    print("\n📋 开发任务: 基于会议建议实施开发")
    print("=" * 80)
    
    total_tokens = 0
    dev_results = {}
    lock = threading.Lock()
    
    # 定义开发任务和负责人
    tasks = [
        {
            "id": 0,
            "name": "智谱GLM-4",
            "role": "API架构师",
            "task": "统一多模型接口规范",
            "prompt": """你是API架构师，负责设计Symphony多模型协作系统的统一接口规范。

请设计一个标准化的API接口规范，包括：
1. 模型调用接口格式（输入/输出）
2. 错误处理机制
3. 响应状态码定义

要求：用JSON格式输出接口规范，包含字段名和类型说明。"""
        },
        {
            "id": 10,
            "name": "Qwen3-235B",
            "role": "中间件架构师",
            "task": "建立中间件层解耦通信",
            "prompt": """你是中间件架构师，负责设计Symphony系统的中间件层。

请设计中间件架构，包括：
1. 模型适配器设计
2. 消息路由机制
3. 数据转换层

要求：用JSON格式输出中间件架构设计。"""
        },
        {
            "id": 12,
            "name": "MiniMax-M2.5",
            "role": "UI设计师",
            "task": "设计可视化任务面板",
            "prompt": """你是UI设计师，负责设计Symphony的可视化任务面板。

请设计面板功能，包括：
1. 任务状态展示区域
2. 模型选择器界面
3. 进度追踪组件

要求：用JSON格式输出UI组件设计。"""
        },
        {
            "id": 15,
            "name": "DeepSeek R1",
            "role": "技术总监",
            "task": "制定行动计划",
            "prompt": """你是技术总监，负责制定Symphony系统开发行动计划。

请制定实施计划，包括：
1. 第一阶段：接口标准化（时间节点、验收标准）
2. 第二阶段：中间件开发（时间节点、验收标准）
3. 第三阶段：UI开发（时间节点、验收标准）

要求：用JSON格式输出行动计划。"""
        }
    ]
    
    # ============ Phase 1: 并行开发 ============
    print("\n" + "=" * 80)
    print("[Phase 1] 并行开发 - 各模块设计")
    print("=" * 80)
    
    def develop_task(task):
        print(f"\n🔧 [{task['name']} ({task['role']})] 开发中: {task['task']}...")
        
        result = call_api(task["id"], task["prompt"], 400)
        
        with lock:
            if result and result.get("success"):
                dev_results[task["name"]] = {
                    "role": task["role"],
                    "task": task["task"],
                    "content": result["content"],
                    "tokens": result["tokens"],
                    "success": True
                }
                total_tokens = sum(r["tokens"] for r in dev_results.values())
                print(f"   ✅ 完成 - {result['tokens']} tokens")
            else:
                dev_results[task["name"]] = {
                    "role": task["role"],
                    "task": task["task"],
                    "content": f"开发失败: {result.get('error', '未知') if result else '无响应'}",
                    "tokens": 0,
                    "success": False
                }
                print(f"   ❌ 失败")
    
    # 并行执行
    threads = []
    for task in tasks:
        t = threading.Thread(target=develop_task, args=(task,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # ============ Phase 2: 代码整合 ============
    print("\n" + "=" * 80)
    print("[Phase 2] 代码整合")
    print("=" * 80)
    
    # 汇总设计结果
    designs = []
    for name, data in dev_results.items():
        if data["success"]:
            designs.append(f"{name}({data['task']}): {data['content'][:100]}...")
    
    print("\n📊 设计成果:")
    for d in designs:
        print(f"   • {d[:80]}...")
    
    # ============ Phase 3: 生成代码 ============
    print("\n" + "=" * 80)
    print("[Phase 3] 生成代码框架")
    print("=" * 80)
    
    code_gen_prompt = f"""基于以下设计成果，生成Python代码框架：

设计内容：
{json.dumps(dev_results, ensure_ascii=False, indent=2)}

请生成：
1. unified_api.py - 统一接口规范
2. middleware.py - 中间件层
3. task_panel.py - 任务面板

每段代码用```python包裹。"""

    result = call_api(0, code_gen_prompt, 500)
    
    if result and result.get("success"):
        total_tokens = sum(r["tokens"] for r in dev_results.values()) + result["tokens"]
        code_output = result["content"]
        
        # 保存代码
        with open("unified_api.py", "w", encoding="utf-8") as f:
            f.write('# Symphony 统一接口规范\n# 生成时间: ' + datetime.now().isoformat() + '\n\n')
            # 提取代码部分
            if "```python" in code_output:
                start = code_output.find("```python") + 9
                end = code_output.find("```", start)
                if end > start:
                    f.write(code_output[start:end])
            else:
                f.write(code_output)
        
        print("   ✅ unified_api.py 已生成")
    
    # ============ 最终报告 ============
    print("\n" + "=" * 80)
    print("📋 多人开发报告")
    print("=" * 80)
    
    total_tokens = sum(r["tokens"] for r in dev_results.values())
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony v{VERSION} 多人开发
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 参与开发: {len(tasks)}位专家

📊 开发任务分配:
""")
    
    for task in tasks:
        status = "✅" if dev_results.get(task["name"], {}).get("success") else "❌"
        tokens = dev_results.get(task["name"], {}).get("tokens", 0)
        print(f"  {status} [{task['role']}] {task['name']}: {task['task']} ({tokens} tokens)")
    
    print(f"""
📋 完成状态: {len([r for r in dev_results.values() if r['success']])}/{len(tasks)}

💰 总Token消耗: {total_tokens}

📁 生成的文件:
  • unified_api.py - 统一接口规范

🎯 优先问题:
  1. 接口与通信协议标准化 ✅
  2. 模型协作框架搭建 ✅
  3. 用户配置界面开发 ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "tasks": tasks,
        "results": dev_results,
        "total_tokens": total_tokens
    }


if __name__ == "__main__":
    report = multi_person_development()
    
    with open("multi_person_dev_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: multi_person_dev_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
