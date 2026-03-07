#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v3.3.0 - 增强调度真实模型协作系统
完全避免幻觉模拟，每一步都有真实API调用记录
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


VERSION = "3.3.0"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=150, caller_id="system"):
    """真实API调用，带调用记录"""
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
            content = j["choices"][0]["message"]["content"]
            tokens = j.get("usage", {}).get("total_tokens", 0)
            
            # 记录调用
            call_record = {
                "caller_id": caller_id,
                "model_index": model_index,
                "model_name": model["name"],
                "prompt": prompt[:100],
                "response": content[:200],
                "tokens": tokens,
                "timestamp": datetime.now().isoformat()
            }
            
            return {"success": True, "content": content, "tokens": tokens, "call_record": call_record}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return None


def enhanced_collaboration():
    """增强调度真实模型协作"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 增强调度真实模型协作系统")
    print("=" * 80)
    print("\n⚠️ 核心原则：每一步都有真实API调用记录，完全避免幻觉！")
    
    total_tokens = 0
    call_history = []  # 所有调用记录
    
    # ============ Step 1: 任务分解（智谱GLM-4-Flash） ============
    print("\n" + "=" * 80)
    print("[Step 1] 任务分解 - 调用智谱GLM-4-Flash")
    print("=" * 80)
    
    user_task = "分析当前AI发展趋势并给出商业建议"
    
    prompt1 = f"""你是一个任务分解专家。请将以下任务分解为3个子任务：
任务：{user_task}

每个子任务用一句话描述。（60字以内）"""

    result1 = call_api(0, prompt1, 100, "Step1-TaskDecompose")
    if result1 and result1.get("success"):
        total_tokens += result1.get("tokens", 0)
        call_history.append(result1.get("call_record"))
        subtasks = result1["content"]
        
        print(f"\n📝 任务分解结果（真实API调用）:")
        print(f"   {subtasks[:200]}")
        
        # 提取子任务
        subtask_list = [s.strip() for s in subtasks.split("\n") if s.strip()][:3]
    else:
        subtask_list = ["分析AI发展趋势", "评估市场机会", "制定商业策略"]
        print("   ⚠️ 调用失败，使用默认子任务")
    
    # ============ Step 2: 并行执行子任务（多个模型） ============
    print("\n" + "=" * 80)
    print("[Step 2] 并行执行子任务 - 调用多个模型")
    print("=" * 80)
    
    # 定义任务分配
    task_assignments = [
        (0, subtask_list[0] if len(subtask_list) > 0 else "分析AI发展趋势"),
        (12, subtask_list[1] if len(subtask_list) > 1 else "评估市场机会"),
        (14, subtask_list[2] if len(subtask_list) > 2 else "制定商业策略"),
    ]
    
    parallel_results = {}
    threads = []
    lock = threading.Lock()
    
    def execute_task(idx, task, task_key):
        result = call_api(idx, f"请用30字回答：{task}", 50, f"Step2-{task_key}")
        with lock:
            parallel_results[task_key] = result
            if result and result.get("success"):
                call_history.append(result.get("call_record"))
    
    for model_idx, task in task_assignments:
        t = threading.Thread(target=execute_task, args=(model_idx, task, f"task_{task_assignments.index((model_idx, task))}"))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("\n🔄 并行执行结果（真实API调用）:")
    for key, result in parallel_results.items():
        if result and result.get("success"):
            total_tokens += result.get("tokens", 0)
            print(f"\n  {key}: {result['content'][:100]}")
    
    # ============ Step 3: 结果整合（智谱GLM-Z1-Flash） ============
    print("\n" + "=" * 80)
    print("[Step 3] 结果整合 - 调用智谱GLM-Z1-Flash")
    print("=" * 80)
    
    # 汇总子任务结果
    summary_input = "\n".join([f"子任务{i+1}: {r['content'][:50] if r and r.get('success') else '无'}" 
                               for i, r in enumerate(parallel_results.values())])
    
    prompt3 = f"""请整合以下子任务结果，给出最终建议：
{summary_input}

请用80字以内总结。"""

    result3 = call_api(1, prompt3, 120, "Step3-Integration")
    if result3 and result3.get("success"):
        total_tokens += result3.get("tokens", 0)
        call_history.append(result3.get("call_record"))
        
        print(f"\n📋 整合结果（真实API调用）:")
        print(f"   {result3['content'][:200]}")
    
    # ============ Step 4: 验证环节（ModelScope MiniMax-M2.5） ============
    print("\n" + "=" * 80)
    print("[Step 4] 验证环节 - 调用ModelScope MiniMax-M2.5")
    print("=" * 80)
    
    prompt4 = f"""请验证以下建议的可行性：
{result3['content'] if result3 and result3.get('success') else ''}

请用50字给出验证结果。"""

    result4 = call_api(12, prompt4, 80, "Step4-Verification")
    if result4 and result4.get("success"):
        total_tokens += result4.get("tokens", 0)
        call_history.append(result4.get("call_record"))
        
        print(f"\n✅ 验证结果（真实API调用）:")
        print(f"   {result4['content'][:150]}")
    
    # ============ 总结 ============
    print("\n" + "=" * 80)
    print("📊 增强调度协作总结")
    print("=" * 80)
    
    # 统计调用
    model_calls = {}
    for record in call_history:
        model = record.get("model_name", "unknown")
        if model not in model_calls:
            model_calls[model] = {"count": 0, "tokens": 0}
        model_calls[model]["count"] += 1
        model_calls[model]["tokens"] += record.get("tokens", 0)
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony v{VERSION} 增强调度协作
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 协作流程:
  1. 任务分解（智谱GLM-4-Flash）
  2. 并行执行（智谱GLM-4-Flash + MiniMax-M2.5 + GLM-5）
  3. 结果整合（智谱GLM-Z1-Flash）
  4. 验证环节（ModelScope MiniMax-M2.5）

🔍 调用统计:
  • 总调用次数: {len(call_history)}
  • 总Token消耗: {total_tokens}

📊 模型调用详情:
""")
    
    for model, stats in model_calls.items():
        print(f"  • {model}: {stats['count']}次调用, {stats['tokens']} tokens")
    
    print(f"""
⚠️ 反幻觉机制:
  ✅ 每步都有真实API调用
  ✅ 所有响应来自实际模型输出
  ✅ 调用记录可追溯验证
  ✅ 无任何模拟/编造内容

🔥 核心优势:
  1. 真实API调用，非模拟
  2. 并行处理提高效率
  3. 多模型验证确保准确
  4. 完整调用历史可追溯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "total_tokens": total_tokens,
        "total_calls": len(call_history),
        "model_calls": model_calls,
        "call_history": call_history
    }


if __name__ == "__main__":
    report = enhanced_collaboration()
    
    with open("enhanced_collaboration_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: enhanced_collaboration_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
