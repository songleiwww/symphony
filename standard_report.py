#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v2.0.0 - 标准化汇报系统
任何对话必须回报：Tokens明细、真实模型检测、限流恢复报告
"""
import sys
import json
import time
import requests
import threading
import os
from datetime import datetime, timedelta
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


VERSION = "2.0.0"


class RateLimitManager:
    """限流管理器"""
    
    def __init__(self):
        self.rate_limits = {}
        self.retry_interval = 30
        
    def mark_rate_limit(self, model_index: int, model_name: str):
        now = time.time()
        if model_index not in self.rate_limits:
            self.rate_limits[model_index] = {
                "name": model_name,
                "first_429": now,
                "count": 1,
                "status": "limited"
            }
        else:
            self.rate_limits[model_index]["count"] += 1
        print(f"  ⚠️ {model_name} 触发限流")
        
    def analyze_recovery(self, model_index: int) -> dict:
        if model_index not in self.rate_limits:
            return {"recoverable": False, "reason": "无记录"}
        
        record = self.rate_limits[model_index]
        elapsed = time.time() - record["first_429"]
        estimated_wait = 30 * record["count"]
        
        return {
            "recoverable": True,
            "model_name": record["name"],
            "first_429_time": datetime.fromtimestamp(record["first_429"]).strftime("%H:%M:%S"),
            "elapsed_seconds": int(elapsed),
            "estimated_recovery": estimated_wait - int(elapsed) if elapsed < estimated_wait else 0,
            "should_retry": elapsed >= estimated_wait
        }


# 全局实例
rate_manager = RateLimitManager()


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def test_model_call(model_config, model_index: int, prompt: str = "测试") -> dict:
    url = model_config["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model_config["api_key"], "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": 30, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=8)
        
        if r.status_code == 200:
            j = r.json()
            return {
                "success": True,
                "model_index": model_index,
                "model_name": model_config.get("alias", model_config.get("name")),
                "provider": model_config.get("provider"),
                "tokens": j.get("usage", {}).get("total_tokens", 0),
                "status": "available"
            }
        elif r.status_code == 429:
            rate_manager.mark_rate_limit(model_index, model_config.get("alias", model_config.get("name")))
            analysis = rate_manager.analyze_recovery(model_index)
            return {
                "success": False,
                "model_index": model_index,
                "model_name": model_config.get("alias", model_config.get("name")),
                "status": "limited",
                "recovery": analysis
            }
        else:
            return {
                "success": False,
                "model_index": model_index,
                "model_name": model_config.get("alias", model_config.get("name")),
                "status": "error",
                "error": f"HTTP {r.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "model_index": model_index,
            "model_name": model_config.get("alias", model_config.get("name")),
            "status": "error",
            "error": str(e)[:50]
        }


def generate_standard_report(user_prompt: str = "测试"):
    """生成标准化汇报"""
    
    print("=" * 70)
    print(f"🎼 Symphony v{VERSION} - 标准化汇报系统")
    print("=" * 70)
    
    # 1. 检测所有模型真实状态
    print("\n📡 [1/4] 真实模型使用检测...")
    print("-" * 50)
    
    enabled = get_enabled_models()
    results = []
    
    for i, model in enumerate(enabled):
        print(f"  检测模型 {i}: {model.get('alias', model.get('name'))[:30]}")
        result = test_model_call(model, i, user_prompt)
        results.append(result)
        
        if result.get("success"):
            print(f"    ✅ 可用 - {result.get('tokens')} tokens")
        elif result.get("status") == "limited":
            recovery = result.get("recovery", {})
            print(f"    ❌ 限流 - 预计{recovery.get('estimated_recovery', '?')}秒恢复")
        else:
            print(f"    ⚠️ 错误 - {result.get('error', 'Unknown')}")
    
    # 2. Tokens明细汇总
    print("\n💰 [2/4] Tokens明细汇总")
    print("-" * 50)
    
    available_models = [r for r in results if r.get("success")]
    limited_models = [r for r in results if r.get("status") == "limited"]
    error_models = [r for r in results if r.get("status") == "error"]
    
    total_tokens = sum(r.get("tokens", 0) for r in available_models)
    
    print(f"\n📊 Tokens明细表:")
    print(f"| 序号 | 模型 | 状态 | Token |")
    print(f"|------|------|------|-------|")
    
    for r in results:
        idx = r.get("model_index")
        name = r.get("model_name", "N/A")[:20]
        status_emoji = "✅" if r.get("success") else ("❌" if r.get("status") == "limited" else "⚠️")
        status_text = "可用" if r.get("success") else ("限流" if r.get("status") == "limited" else "错误")
        tokens = r.get("tokens", 0)
        print(f"| {idx} | {name} | {status_emoji}{status_text} | {tokens} |")
    
    print(f"\n💵 总消耗: {total_tokens} tokens")
    print(f"✅ 可用模型: {len(available_models)}")
    print(f"❌ 限流模型: {len(limited_models)}")
    print(f"⚠️ 错误模型: {len(error_models)}")
    
    # 3. 限流恢复报告
    print("\n⏰ [3/4] 限流恢复报告")
    print("-" * 50)
    
    if limited_models:
        print(f"\n限流模型恢复预测:")
        for r in limited_models:
            recovery = r.get("recovery", {})
            model_name = recovery.get("model_name", r.get("model_name"))
            first_time = recovery.get("first_429_time", "N/A")
            elapsed = recovery.get("elapsed_seconds", 0)
            estimated = recovery.get("estimated_recovery", 0)
            
            if estimated > 0:
                recover_time = datetime.now() + timedelta(seconds=estimated)
                print(f"  • {model_name}")
                print(f"    首次限流: {first_time} | 已过: {elapsed}秒")
                print(f"    ⏱️ 预计恢复: {recover_time.strftime('%H:%M:%S')} (约{estimated}秒后)")
            else:
                print(f"  • {model_name} - 已可重试!")
    else:
        print("  ✅ 无需恢复 - 所有模型正常")
    
    # 4. 可用模型推荐
    print("\n🎯 [4/4] 可用模型推荐")
    print("-" * 50)
    
    if available_models:
        # 按Token消耗排序推荐
        sorted_available = sorted(available_models, key=lambda x: x.get("tokens", 0), reverse=True)
        print("\n推荐使用（按响应速度）:")
        for i, m in enumerate(sorted_available[:5], 1):
            print(f"  {i}. {m.get('model_name')} ({m.get('provider')})")
    else:
        print("  ⚠️ 暂无推荐 - 请稍后重试")
    
    # 总结
    print("\n" + "=" * 70)
    print("📋 标准化汇报汇总")
    print("=" * 70)
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony 汇报标准
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 检测模型总数: {len(results)}
  ✅ 可用: {len(available_models)}  |  ❌ 限流: {len(limited_models)}  |  ⚠️ 错误: {len(error_models)}
  💰 总Token消耗: {total_tokens}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "user_prompt": user_prompt,
        "total_models": len(results),
        "available": len(available_models),
        "limited": len(limited_models),
        "error": len(error_models),
        "total_tokens": total_tokens,
        "results": results,
        "limited_models": [
            {
                "name": r.get("recovery", {}).get("model_name", r.get("model_name")),
                "first_429": r.get("recovery", {}).get("first_429_time"),
                "estimated_recovery": r.get("recovery", {}).get("estimated_recovery", 0)
            }
            for r in limited_models
        ]
    }


if __name__ == "__main__":
    report = generate_standard_report()
    
    with open("standard_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: standard_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
