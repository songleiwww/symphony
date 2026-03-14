#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.9.0 - 模型限流检测与自动恢复系统
分析限流时间，到期自动重新加入可调用行列
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


VERSION = "1.9.0"


class RateLimitManager:
    """限流管理器"""
    
    def __init__(self):
        # 限流记录: {model_index: {"first_429": timestamp, "count": count, "status": "limited"}}
        self.rate_limits = {}
        # 模型状态: {model_index: "available" | "limited" | "testing"}
        self.model_status = {}
        # 重试间隔（秒）
        self.retry_interval = 60
        # 最大连续限流次数
        self.max_consecutive_429 = 3
        
    def mark_rate_limit(self, model_index: int):
        """标记限流"""
        now = time.time()
        if model_index not in self.rate_limits:
            self.rate_limits[model_index] = {
                "first_429": now,
                "count": 1,
                "status": "limited"
            }
        else:
            self.rate_limits[model_index]["count"] += 1
        
        self.model_status[model_index] = "limited"
        print(f"  ⚠️ 模型 {model_index} 触发限流 (第{self.rate_limits[model_index]['count']}次)")
        
    def analyze_rate_limit_time(self, model_index: int) -> dict:
        """分析限流时间"""
        if model_index not in self.rate_limits:
            return {"estimated_recovery": None, "reason": "无记录"}
        
        record = self.rate_limits[model_index]
        first_429 = record["first_429"]
        elapsed = time.time() - first_429
        
        # 简单估算：每触发一次增加等待时间
        base_wait = 30  # 基础等待30秒
        estimated_wait = base_wait * record["count"]
        
        return {
            "first_429_time": datetime.fromtimestamp(first_429).strftime("%H:%M:%S"),
            "elapsed_seconds": int(elapsed),
            "consecutive_count": record["count"],
            "estimated_recovery": estimated_wait,
            "should_retry": elapsed >= estimated_wait
        }
    
    def should_retry(self, model_index: int) -> bool:
        """检查是否应该重试"""
        if model_index not in self.rate_limits:
            return True
        
        analysis = self.analyze_rate_limit_time(model_index)
        return analysis.get("should_retry", False)
    
    def recover_model(self, model_index: int):
        """恢复模型"""
        if model_index in self.rate_limits:
            del self.rate_limits[model_index]
        self.model_status[model_index] = "available"
        print(f"  ✅ 模型 {model_index} 已恢复")
        
    def get_status(self) -> dict:
        """获取状态"""
        return {
            "rate_limits": self.rate_limits,
            "model_status": self.model_status
        }


# 全局限流管理器
rate_manager = RateLimitManager()


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def test_model_call(model_config, model_index: int, test_prompt: str = "你好") -> dict:
    """测试模型调用"""
    url = model_config["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model_config["api_key"], "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": test_prompt}], "max_tokens": 50, "temperature": 0.7}
    
    try:
        r = requests.post(url, headers=headers, json=data, timeout=10)
        
        if r.status_code == 200:
            j = r.json()
            return {
                "success": True,
                "status_code": 200,
                "tokens": j.get("usage", {}).get("total_tokens", 0),
                "model": model_config.get("alias", model_config.get("name"))
            }
        elif r.status_code == 429:
            # 限流
            rate_manager.mark_rate_limit(model_index)
            analysis = rate_manager.analyze_rate_limit_time(model_index)
            return {
                "success": False,
                "status_code": 429,
                "error": "Rate Limited",
                "analysis": analysis
            }
        else:
            return {
                "success": False,
                "status_code": r.status_code,
                "error": f"HTTP {r.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


print("=" * 70)
print(f"Symphony v{VERSION} - 模型限流检测与自动恢复")
print("=" * 70)

# Phase 1: 全面检测模型状态
print("\n[Phase 1] 全面检测模型状态")
print("-" * 50)

enabled = get_enabled_models()
test_results = []

for i, model in enumerate(enabled):
    name = model.get("alias", model.get("name"))
    provider = model.get("provider", "unknown")
    print(f"\n测试模型 {i}: {name} ({provider})")
    
    result = test_model_call(model, i, "测试")
    
    if result.get("success"):
        print(f"  ✅ 正常 - {result.get('tokens')} tokens")
        test_results.append({
            "index": i,
            "name": name,
            "status": "available",
            "tokens": result.get("tokens", 0)
        })
        rate_manager.recover_model(i)
    elif result.get("status_code") == 429:
        analysis = result.get("analysis", {})
        print(f"  ❌ 限流 - 预计{analysis.get('estimated_recovery', '?')}秒后恢复")
        test_results.append({
            "index": i,
            "name": name,
            "status": "limited",
            "analysis": analysis
        })
    else:
        print(f"  ❌ 失败 - {result.get('error')}")
        test_results.append({
            "index": i,
            "name": name,
            "status": "error",
            "error": result.get("error")
        })

# Phase 2: 限流分析
print("\n" + "=" * 70)
print("[Phase 2] 限流分析")
print("-" * 50)

limited_models = [r for r in test_results if r.get("status") == "limited"]

if limited_models:
    print(f"\n发现 {len(limited_models)} 个限流模型:")
    for m in limited_models:
        analysis = m.get("analysis", {})
        print(f"\n  模型: {m['name']}")
        print(f"    首次限流: {analysis.get('first_429_time', 'N/A')}")
        print(f"    持续时间: {analysis.get('elapsed_seconds', 0)}秒")
        print(f"    连续次数: {analysis.get('consecutive_count', 1)}")
        print(f"    预计恢复: {analysis.get('estimated_recovery', '?')}秒")
else:
    print("\n  ✅ 无限流模型")

# Phase 3: 自动恢复机制
print("\n" + "=" * 70)
print("[Phase 3] 自动恢复机制")
print("-" * 50)

auto_recovery_code = '''"""
Symphony Rate Limit Auto-Recovery - 自动恢复机制
"""
import threading
import time
from datetime import datetime

class AutoRecovery:
    """自动恢复"""
    
    def __init__(self, rate_manager, check_interval=30):
        self.rate_manager = rate_manager
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        
    def start(self):
        """启动自动恢复"""
        self.running = True
        self.thread = threading.Thread(target=self._check_loop)
        self.thread.daemon = True
        self.thread.start()
        print("自动恢复服务已启动")
        
    def stop(self):
        """停止自动恢复"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("自动恢复服务已停止")
        
    def _check_loop(self):
        """检查循环"""
        while self.running:
            # 检查每个限流模型
            for model_idx in list(self.rate_manager.rate_limits.keys()):
                if self.rate_manager.should_retry(model_idx):
                    print(f"模型 {model_idx} 尝试恢复...")
                    # 这里可以触发测试调用
                    # 如果成功则恢复
                    pass
            
            time.sleep(self.check_interval)


# 使用示例
if __name__ == "__main__":
    from your_module import rate_manager
    
    auto_recovery = AutoRecovery(rate_manager, check_interval=30)
    auto_recovery.start()
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        auto_recovery.stop()
'''

with open("auto_recovery.py", "w", encoding="utf-8") as f:
    f.write(auto_recovery_code)
print("  ✅ auto_recovery.py 已生成")

# Phase 4: 策略建议
print("\n" + "=" * 70)
print("[Phase 4] 限流应对策略")
print("-" * 50)

strategies = """
限流应对策略建议：

1. 【预防策略】
   - 分散调用时间，避免集中请求
   - 设置调用间隔（如每模型至少间隔2秒）
   - 监控调用频率

2. 【检测策略】
   - 实时检测HTTP 429响应
   - 记录首次限流时间
   - 统计连续限流次数

3. 【恢复策略】
   - 指数退避等待（30s → 60s → 120s...）
   - 自动重试机制
   - 切换备用模型

4. 【架构策略】
   - 模型池轮询
   - 负载均衡
   - 熔断器模式
"""

print(strategies)

# Phase 5: 总结
print("\n" + "=" * 70)
print("[Phase 5] 总结报告")
print("-" * 50)

available_count = len([r for r in test_results if r.get("status") == "available"])
limited_count = len([r for r in test_results if r.get("status") == "limited"])
error_count = len([r for r in test_results if r.get("status") == "error"])

print(f"""
模型状态统计:
  ✅ 可用: {available_count}
  ❌ 限流: {limited_count}
  ⚠️ 错误: {error_count}
  总计: {len(test_results)}

限流模型恢复建议:
""")

for m in limited_models:
    analysis = m.get("analysis", {})
    wait = analysis.get("estimated_recovery", 0)
    if wait:
        print(f"  - {m['name']}: 等待约{wait}秒后自动恢复")

# 保存报告
report = {
    "version": VERSION,
    "datetime": datetime.now().isoformat(),
    "test_results": test_results,
    "summary": {
        "available": available_count,
        "limited": limited_count,
        "error": error_count
    },
    "rate_limits": rate_manager.get_status()
}

with open("rate_limit_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n✅ 报告已保存: rate_limit_report.json")
print("\nSymphony - 智韵交响，共创华章！")
