#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.3.0 - 多模型协作演示
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


VERSION = "1.3.0"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=150):
    """真实API调用"""
    enabled = get_enabled_models()
    if model_index >= len(enabled):
        return None
    
    model = enabled[model_index]
    url = model["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
    data = {"model": model["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return None


def multi_model_collaboration():
    """多模型协作"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 多模型协作演示")
    print("=" * 80)
    
    total_tokens = 0
    results = []
    
    # 定义任务
    task = "请用50字介绍人工智能的未来发展趋势"
    
    # 使用3个不同模型并行处理
    models = [
        (0, "智谱GLM-4-Flash", "技术视角"),
        (12, "MiniMax-M2.5", "应用视角"),
        (15, "DeepSeek R1", "推理视角")
    ]
    
    print(f"\n📋 任务: {task}")
    print(f"\n🔄 并行调用 {len(models)} 个模型...")
    
    # 并行调用
    threads = []
    lock = threading.Lock()
    parallel_results = {}
    
    def call_model(idx, name, perspective):
        print(f"\n   [{name}] 正在处理...")
        result = call_api(idx, task, 100)
        with lock:
            if result and result.get("success"):
                parallel_results[name] = {
                    "perspective": perspective,
                    "content": result["content"],
                    "tokens": result["tokens"]
                }
                total_tokens = sum(r["tokens"] for r in parallel_results.values())
            else:
                parallel_results[name] = {
                    "perspective": perspective,
                    "content": f"调用失败: {result.get('error', '未知') if result else '无响应'}",
                    "tokens": 0
                }
    
    for idx, name, perspective in models:
        t = threading.Thread(target=call_model, args=(idx, name, perspective))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # 显示结果
    print("\n" + "=" * 80)
    print("📊 多模型协作结果")
    print("=" * 80)
    
    for name, data in parallel_results.items():
        print(f"\n🤖 [{name}] ({data['perspective']}):")
        print(f"   {data['content'][:200]}")
    
    # 汇总
    total_tokens = sum(r["tokens"] for r in parallel_results.values())
    
    print("\n" + "=" * 80)
    print("📈 协作统计")
    print("=" * 80)
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony v{VERSION} 多模型协作
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 调用统计:
  • 调用模型: {len(models)}个
  • 成功: {len([r for r in parallel_results.values() if r['tokens'] > 0])}个
  • 总Token: {total_tokens}

🤖 参与模型:
""")
    
    for name, data in parallel_results.items():
        status = "✅" if data["tokens"] > 0 else "❌"
        print(f"  {status} {name}: {data['tokens']} tokens")
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "total_tokens": total_tokens,
        "results": parallel_results
    }


if __name__ == "__main__":
    report = multi_model_collaboration()
    
    with open("multi_model_demo_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: multi_model_demo_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
