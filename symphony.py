#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎼 交响监控控制台
实时监控交响系统的工作状态
"""

import sys
import io
import os

# 简单设置编码，不要修改stdout
if sys.platform == 'win32':
    # 设置标准输出编码为UTF-8
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass

# 只在直接运行时修改stdout，import时不修改
if __name__ == "__main__" and sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

import time
import json
import requests
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import (
    CONFIG, MODEL_INFO, SYSTEM_CONFIG,
    get_provider_for_model, get_api_config_for_model, get_model_info,
    get_genesis_story, get_dream_maker, get_jiaoJiao, get_brand,
    DOUBAO_CONFIG, NVIDIA_CONFIG, ZHIPU_CONFIG,
    check_rate_limit, record_request, get_models_by_type, get_all_models,
    get_provider_name, get_models_by_provider
)


# =============================================================================
# 实时监控器
# =============================================================================

class RealtimeMonitor:
    """实时监控器"""
    
    def __init__(self):
        self.active_calls: Dict[str, Dict] = {}  # 进行中的调用
        self.call_history: List[Dict] = []  # 调用历史
        self.model_stats: Dict[str, Dict] = {}  # 模型统计
        self.start_time = datetime.now()
        self.lock = threading.Lock()
        self.callbacks: List[callable] = []
    
    def register_callback(self, callback: callable):
        """注册回调"""
        self.callbacks.append(callback)
    
    def notify(self, event: str, data: Any = None):
        """通知更新"""
        for cb in self.callbacks:
            try:
                cb(event, data)
            except:
                pass
    
    def start_call(self, call_id: str, model: str, prompt: str):
        """开始调用"""
        with self.lock:
            self.active_calls[call_id] = {
                "model": model,
                "prompt": prompt[:50],
                "start_time": time.time(),
                "status": "running"
            }
            self.notify("start", {"call_id": call_id, "model": model})
    
    def end_call(self, call_id: str, success: bool, response: str = "", error: str = "", elapsed: float = 0):
        """结束调用"""
        with self.lock:
            if call_id in self.active_calls:
                call = self.active_calls.pop(call_id)
                
                record = {
                    "call_id": call_id,
                    "model": call["model"],
                    "prompt": call["prompt"],
                    "success": success,
                    "response": response[:100] if response else "",
                    "error": error,
                    "elapsed": elapsed,
                    "timestamp": datetime.now().isoformat()
                }
                self.call_history.append(record)
                
                # 更新统计
                model = call["model"]
                if model not in self.model_stats:
                    self.model_stats[model] = {"success": 0, "fail": 0, "total_time": 0, "calls": 0}
                
                stats = self.model_stats[model]
                stats["calls"] += 1
                if success:
                    stats["success"] += 1
                    stats["total_time"] += elapsed
                else:
                    stats["fail"] += 1
                
                # 保持历史记录
                if len(self.call_history) > 1000:
                    self.call_history = self.call_history[-500:]
                
                self.notify("end", record)
                
                # 保存到文件供外部程序读取
                save_monitor_to_file()
    
    def get_active(self) -> List[Dict]:
        """获取进行中的调用"""
        with self.lock:
            return list(self.active_calls.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        with self.lock:
            uptime = (datetime.now() - self.start_time).total_seconds()
            total_calls = len(self.call_history)
            success_calls = sum(1 for c in self.call_history if c["success"])
            
            return {
                "uptime": uptime,
                "total_calls": total_calls,
                "success_rate": (success_calls / total_calls * 100) if total_calls > 0 else 0,
                "active_calls": len(self.active_calls),
                "model_stats": self.model_stats.copy()
            }
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """获取历史记录"""
        with self.lock:
            return self.call_history[-limit:]


# 全局监控器
_monitor = RealtimeMonitor()

# 监控数据文件路径
MONITOR_FILE = str(Path(__file__).parent / "monitor_data.json")


def save_monitor_to_file():
    """保存监控数据到文件（供外部程序读取）"""
    try:
        stats = _monitor.get_stats()
        history = _monitor.get_history(10)
        
        data = {
            "uptime": stats.get("uptime", 0),
            "total_calls": stats.get("total_calls", 0),
            "success_rate": stats.get("success_rate", 0),
            "active_calls": stats.get("active_calls", 0),
            "model_stats": stats.get("model_stats", {}),
            "recent_calls": [
                {
                    "model": h.get("model", ""),
                    "success": h.get("success", False),
                    "elapsed": h.get("elapsed", 0),
                    "prompt": h.get("prompt", "")[:50] + "..." if len(h.get("prompt", "")) > 50 else h.get("prompt", ""),
                    "timestamp": h.get("timestamp", "")
                }
                for h in history
            ],
            "last_update": datetime.now().isoformat()
        }
        
        with open(MONITOR_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass  # 静默失败，不影响主流程


def load_monitor_from_file() -> dict:
    """从文件加载监控数据（供外部程序读取）"""
    try:
        if Path(MONITOR_FILE).exists():
            with open(MONITOR_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}


def get_monitor() -> RealtimeMonitor:
    return _monitor


# =============================================================================
# 交响调用器（带监控）
# =============================================================================

class Symphony:
    """交响核心类"""
    
    def __init__(self):
        self.config = CONFIG
        self.monitor = _monitor
        self.call_count = 0
        
        # 品牌信息
        brand = get_brand()
        self.brand = brand
    
    def call_model(self, model_id: str, prompt: str) -> Dict[str, Any]:
        """调用模型（带监控和限流检测）"""
        self.call_count += 1
        call_id = f"call_{self.call_count}_{int(time.time())}"
        
        # 获取模型信息
        model_info = get_model_info(model_id)
        provider = model_info.get("provider", "unknown")
        
        # 检查限流
        allowed, recovery_time = check_rate_limit(provider)
        if not allowed:
            return {
                "success": False,
                "model": model_id,
                "error": f"限流中，{recovery_time:.1f}秒后恢复",
                "rate_limited": True,
                "recovery_time": recovery_time,
                "call_id": call_id
            }
        
        # 记录请求
        record_request(provider)
        
        # 开始监控
        self.monitor.start_call(call_id, model_id, prompt)
        
        # 获取API配置
        api_config = get_api_config_for_model(model_id)
        
        url = f"{api_config['base_url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        start = time.time()
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=120)
            elapsed = time.time() - start
            
            # 先检查状态码
            if resp.status_code == 429:
                # 限流错误
                try:
                    err_data = resp.json()
                    err_msg = err_data.get("error", {}).get("message", "达到调用限制")
                except:
                    err_msg = "达到调用限制，请稍后再试"
                
                # 尝试解析恢复时间
                recovery = check_rate_limit(provider)
                if recovery[1]:
                    error = f"⏳ API限流中，预计{recovery[1]:.0f}秒后恢复 | 原因: {err_msg}"
                else:
                    error = f"⏳ API限流: {err_msg}"
                content = ""
                success = False
            elif resp.status_code != 200:
                # 其他错误
                content = ""
                try:
                    err_data = resp.json()
                    error = f"Status {resp.status_code}: {err_data.get('error', {}).get('message', resp.text[:100])}"
                except:
                    error = f"Status {resp.status_code}: {resp.text[:100]}"
                success = False
            else:
                # 200 OK
                result = resp.json()
                choices = result.get("choices", [])
                if choices:
                    content = choices[0]["message"].get("content", "") or ""
                    finish_reason = choices[0].get("finish_reason", "")
                    
                    # 检查是否正常结束
                    if not content and finish_reason == "length":
                        content = "[响应被截断]"
                    
                    success = True
                    error = ""
                else:
                    content = ""
                    error = "⚠️ 无响应内容"
                    success = False
            
            # 结束监控
            self.monitor.end_call(call_id, success, content, error, elapsed)
            
            return {
                "success": success,
                "model": model_id,
                "response": content,
                "elapsed": elapsed,
                "call_id": call_id
            }
        except Exception as e:
            elapsed = time.time() - start
            self.monitor.end_call(call_id, False, "", str(e), elapsed)
            return {
                "success": False,
                "model": model_id,
                "error": str(e),
                "elapsed": elapsed,
                "call_id": call_id
            }
    
    def call_multiple(self, prompt: str, models: List[str] = None) -> List[Dict]:
        """多模型调用"""
        if models is None:
            models = self.config["models"][:3]
        
        results = []
        with ThreadPoolExecutor(max_workers=len(models)) as executor:
            futures = {executor.submit(self.call_model, m, prompt): m for m in models}
            for future in as_completed(futures):
                results.append(future.result())
        
        # 保存监控数据到文件
        save_monitor_to_file()
        
        return results


# =============================================================================
# 监控控制台
# =============================================================================

def show_dashboard():
    """显示监控仪表板"""
    # 优先从共享文件读取（可跨进程）
    file_data = load_monitor_from_file()
    
    if file_data and file_data.get("total_calls", 0) > 0:
        # 使用文件数据
        stats = {
            "uptime": file_data.get("uptime", 0),
            "total_calls": file_data.get("total_calls", 0),
            "success_rate": file_data.get("success_rate", 0),
            "active_calls": file_data.get("active_calls", 0),
            "model_stats": file_data.get("model_stats", {})
        }
        history = file_data.get("recent_calls", [])
        active = []
        source = "文件共享"
    else:
        # 降级到内存数据
        monitor = _monitor
        stats = monitor.get_stats()
        history = monitor.get_history(10)
        active = monitor.get_active()
        source = "内存"
    
    # 颜色代码
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    
    # ===== 系统状态 =====
    print(f"{BOLD}{CYAN}📊 系统状态{RESET}")
    uptime_mins = stats['uptime'] / 60
    print(f"   ⏱️  运行时间: {uptime_mins:.1f}分钟")
    print(f"   📞 总调用次数: {stats['total_calls']}")
    
    # 成功率颜色
    rate = stats['success_rate']
    rate_color = GREEN if rate >= 80 else YELLOW if rate >= 50 else RED
    print(f"   ✅ 成功率: {rate_color}{rate:.1f}%{RESET}")
    
    # 进行中
    if stats['active_calls'] > 0:
        print(f"   🔄 进行中: {YELLOW}{stats['active_calls']}个{RESET}")
    else:
        print(f"   💤 进行中: 0个")
    
    # ===== 进行中的调用 =====
    if active:
        print(f"\n{BOLD}{YELLOW}🔄 进行中的调用:{RESET}")
        for a in active:
            elapsed = time.time() - a["start_time"]
            print(f"   • {a['model']}: {a['prompt'][:20]}... ({elapsed:.1f}s)")
    
    # ===== 最近调用 =====
    if history:
        print(f"\n{BOLD}{CYAN}📜 最近调用 (最新5条):{RESET}")
        for h in reversed(history[-5:]):
            status = f"{GREEN}✅{RESET}" if h["success"] else f"{RED}❌{RESET}"
            prompt = h['prompt'][:25] + "..." if len(h['prompt']) > 25 else h['prompt']
            print(f"   {status} {h['model']} ({h['elapsed']:.2f}s) - {prompt}")
    
    # ===== 详细模型统计 =====
    if stats["model_stats"]:
        print(f"\n{BOLD}{BLUE}📈 模型统计 (所有模型):{RESET}")
        
        # 计算汇总
        total_success = sum(s['success'] for s in stats["model_stats"].values())
        total_fail = sum(s['fail'] for s in stats["model_stats"].values())
        total_time = sum(s['total_time'] for s in stats["model_stats"].values())
        total_calls_model = sum(s['calls'] for s in stats["model_stats"].values())
        
        # 汇总信息
        avg_time = total_time / total_calls_model if total_calls_model > 0 else 0
        print(f"\n   {BOLD}汇总:{RESET} 总调用{total_calls_model}次 | 成功{total_success}次 | 失败{total_fail}次 | 平均{avg_time:.2f}秒/次")
        
        # 找出最快和最慢
        if stats["model_stats"]:
            fastest = min(stats["model_stats"].items(), key=lambda x: x[1]['total_time']/x[1]['calls'] if x[1]['calls'] > 0 else 999)
            slowest = max(stats["model_stats"].items(), key=lambda x: x[1]['total_time']/x[1]['calls'] if x[1]['calls'] > 0 else 0)
            fastest_avg = fastest[1]['total_time']/fastest[1]['calls'] if fastest[1]['calls'] > 0 else 0
            slowest_avg = slowest[1]['total_time']/slowest[1]['calls'] if slowest[1]['calls'] > 0 else 0
            print(f"   🚀 最快: {fastest[0]} ({fastest_avg:.2f}s) | 🐢 最慢: {slowest[0]} ({slowest_avg:.2f}s)")
        
        # 每个模型的详细统计
        print(f"\n   {BOLD}模型详情:{RESET}")
        for model, s in sorted(stats["model_stats"].items(), key=lambda x: -x[1]['calls']):
            rate = (s["success"] / s["calls"] * 100) if s["calls"] > 0 else 0
            rate_color = GREEN if rate >= 80 else YELLOW if rate >= 50 else RED
            avg = s["total_time"] / s["success"] if s["success"] > 0 else 0
            
            # 状态图标
            if s['calls'] == s['success']:
                icon = f"{GREEN}✓{RESET}"
            elif s['success'] == 0:
                icon = f"{RED}✗{RESET}"
            else:
                icon = f"{YELLOW}~{RESET}"
            
            print(f"   {icon} {model}: {s['success']}/{s['calls']} ({rate_color}{rate:.0f}%{RESET}) 平均{avg:.2f}s | 总{s['total_time']:.1f}s")


def show_menu():
    """显示菜单"""
    brand = get_brand()
    
    print("\n" + "="*70)
    print(f"🎼 {brand['name_cn']} {brand['name_en']} 控制系统 v2.0")
    print("="*70)
    print("\n📋 可用模型:")
    
    # 按提供商分组显示
    print("\n  🔥 火山引擎 (Doubao):")
    for m in get_models_by_provider("doubao"):
        info = get_model_info(m)
        type_icon = get_type_icon(info.get("type", "general"))
        print(f"    • {m} {type_icon}")
    
    print("\n  📊 智谱 (Zhipu):")
    for m in get_models_by_provider("zhipu"):
        info = get_model_info(m)
        type_icon = get_type_icon(info.get("type", "general"))
        print(f"    • {m} {type_icon}")
    
    print("\n  🦁 魔搭 (ModelScope):")
    for m in get_models_by_provider("modelscope"):
        info = get_model_info(m)
        type_icon = get_type_icon(info.get("type", "general"))
        print(f"    • {m} {type_icon}")
    
    print("\n  ⚡ 英伟达 (NVIDIA):")
    for m in get_models_by_provider("nvidia"):
        info = get_model_info(m)
        type_icon = get_type_icon(info.get("type", "general"))
        print(f"    • {m} {type_icon}")
    
    print("\n" + "="*70)
    print("📌 模型类型说明:")
    print("  🧠 推理  💻 代码  👁️ 视觉  🖼️ 图像  🎬 视频  📝 通用")
    print("="*70)
    print("\n选择模式:")
    print("  1. 🎯 对话模式")
    print("  2. 👥 多人调度")
    print("  3. 📊 监控面板")
    print("  4. 🧪 快速测试")
    print("  5. 🔄 实时监控(自动刷新)")
    print("  0. 🚪 退出")
    print("="*70)


def get_type_icon(model_type: str) -> str:
    """获取模型类型图标"""
    icons = {
        "general": "📝",
        "reasoning": "🧠",
        "code": "💻",
        "vision": "👁️",
        "vision_reasoning": "🧠👁️",
        "image": "🖼️",
        "video": "🎬",
    }
    return icons.get(model_type, "📝")


def chat_mode():
    """对话模式"""
    symphony = Symphony()
    print("\n🎯 对话模式 (输入 'quit' 退出, 'stats' 查看统计)")
    
    while True:
        try:
            prompt = input("\n> ").strip()
            if not prompt:
                continue
            if prompt.lower() == "quit":
                break
            if prompt.lower() == "stats":
                show_dashboard()
                continue
            
            result = symphony.call_model(CONFIG["primary_model"], prompt)
            
            if result["success"]:
                print(f"\n✅ [{result['model']}] ({result['elapsed']:.2f}s)")
                print(result["response"])
            else:
                print(f"\n❌ 失败: {result.get('error')}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n错误: {e}")


def multi_mode():
    """多模型模式"""
    symphony = Symphony()
    print("\n👥 多人调度模式")
    prompt = input("请输入问题: ").strip()
    
    if not prompt:
        return
    
    print("\n🚀 开始多模型调用...")
    results = symphony.call_multiple(prompt)
    
    print("\n" + "="*70)
    print("📊 多模型协作结果")
    print("="*70)
    
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"\n{status} {r['model']} ({r.get('elapsed', 0):.2f}s)")
        if r["success"]:
            print(f"   {r['response'][:200]}...")
        else:
            print(f"   错误: {r.get('error', 'unknown')}")


def monitor_mode():
    """监控模式"""
    show_dashboard()


def realtime_monitor():
    """实时监控"""
    import os
    import shutil
    
    # 获取终端宽度
    def get_width():
        return shutil.get_terminal_size().columns or 60
    
    print("\n🔄 实时监控模式已启动")
    print("按 Enter 退出\n")
    
    try:
        count = 0
        while True:
            count += 1
            
            # 清除屏幕
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # 显示刷新标识
            width = get_width()
            print("🎼 交响 Symphony 实时监控".center(width))
            print(f"🔄 刷新 #{count} | {time.strftime('%Y-%m-%d %H:%M:%S')}".center(width))
            print("─"*width)
            
            try:
                show_dashboard()
            except Exception as e:
                print(f"显示错误: {e}")
            
            print("─"*width)
            print(f"💡 1秒后刷新 | 按 Enter 退出")
            
            # 使用线程来监听输入
            import threading
            import sys
            def check_input():
                try:
                    input()
                except:
                    pass
            
            t = threading.Thread(target=check_input, daemon=True)
            t.start()
            t.join(timeout=1)
            
            if not t.is_alive():
                break
                
    except KeyboardInterrupt:
        print("\n\n👋 退出监控")
    except Exception as e:
        print(f"\n\n退出监控: {e}")


def quick_test():
    """快速测试"""
    symphony = Symphony()
    print("\n🧪 快速测试...")
    
    test_models = ["ark-code-latest", "Doubao-Seed-2.0-pro"]
    prompt = "用一句话介绍你自己"
    
    results = symphony.call_multiple(prompt, test_models)
    
    success = sum(1 for r in results if r["success"])
    print(f"\n✅ 测试完成: {success}/{len(results)} 成功")
    
    show_dashboard()


# =============================================================================
# 主程序
# =============================================================================

def main():
    """主程序"""
    # 修复可能的stdout关闭问题
    try:
        if sys.stdout.closed:
            sys.stdout = io.StringIO()
    except:
        pass
    
    # 显示品牌
    brand = get_brand()
    print(f"\n{brand['color']} {brand['name_cn']} ({brand['name_en']}) - {brand['tagline']}")
    
    while True:
        show_menu()
        
        choice = input("\n请选择 (0-5): ").strip()
        
        if choice == "0":
            print("\n👋 再见!")
            break
        elif choice == "1":
            chat_mode()
        elif choice == "2":
            multi_mode()
        elif choice == "3":
            monitor_mode()
        elif choice == "4":
            quick_test()
        elif choice == "5":
            realtime_monitor()
        else:
            print("\n❌ 无效选择")


if __name__ == "__main__":
    main()
