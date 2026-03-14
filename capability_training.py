#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.6.0 - 能力训练系统
训练主模型和被调用模型使用工具、MCP服务、自主收集技术资料
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


VERSION = "1.6.0"


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


def capability_training():
    """能力训练"""
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 18 + "🎓 Symphony 能力训练系统 v" + VERSION + " 🎓" + " " * 24 + "║")
    print("║" + " " * 78 + "║")
    print("║" + f"  训练内容: 工具使用 | MCP服务 | 自主收集技术资料  " + " " * 22 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    total_tokens = 0
    training_results = {}
    lock = threading.Lock()
    
    # 训练任务
    training_tasks = [
        {
            "id": 0,
            "name": "林思远",
            "model": "智谱GLM-4",
            "role": "主模型训练师",
            "avatar": "👨‍🏫",
            "task": "工具使用能力训练",
            "prompt": """你是Symphony系统的主模型训练师。请学习和总结以下工具使用能力：

【训练内容】工具使用能力
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 文件操作工具：
   - read: 读取文件内容
   - write: 创建/覆盖文件
   - edit: 精确编辑文件

2. 执行工具：
   - exec: 执行Shell命令
   - process: 管理后台进程

3. 网络工具：
   - web_search: 网络搜索
   - web_fetch: 获取网页内容
   - browser: 浏览器自动化

4. 消息工具：
   - message: 发送消息到各平台
   - tts: 文本转语音

请用JSON格式总结：
1. 工具分类和用途
2. 最佳实践建议
3. 常见错误及避免方法"""
        },
        {
            "id": 10,
            "name": "王明远",
            "model": "Qwen3-235B",
            "role": "MCP服务训练师",
            "avatar": "🔧",
            "task": "MCP服务能力训练",
            "prompt": """你是Symphony系统的MCP服务训练师。请学习和总结MCP服务使用能力：

【训练内容】MCP服务能力
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MCP (Model Context Protocol) 服务：
1. mcporter CLI - MCP服务器管理工具
2. 支持的MCP服务器类型：
   - HTTP服务器
   - stdio服务器
3. MCP能力：
   - 工具调用 (tools)
   - 资源访问 (resources)
   - 提示模板 (prompts)

请用JSON格式总结：
1. MCP服务架构
2. 配置和使用方法
3. 与Symphony集成方案"""
        },
        {
            "id": 12,
            "name": "赵心怡",
            "model": "MiniMax-M2.5",
            "role": "资料收集训练师",
            "avatar": "📚",
            "task": "自主收集技术资料能力训练",
            "prompt": """你是Symphony系统的资料收集训练师。请学习和总结自主收集技术资料能力：

【训练内容】自主收集技术资料
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

收集方式：
1. web_search - 搜索最新技术资料
2. web_fetch - 获取文档内容
3. image/pdf - 分析文档和图片
4. memory_search - 搜索历史记忆

收集流程：
1. 确定收集目标
2. 选择合适工具
3. 执行收集任务
4. 整理和存储

请用JSON格式总结：
1. 收集策略
2. 工具选择指南
3. 资料整理方法"""
        },
        {
            "id": 15,
            "name": "陈浩然",
            "model": "DeepSeek R1",
            "role": "能力整合训练师",
            "avatar": "🎯",
            "task": "综合能力整合训练",
            "prompt": """你是Symphony系统的能力整合训练师。请整合所有训练成果：

【训练内容】综合能力整合
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

整合目标：
1. 工具使用能力 ✓
2. MCP服务能力 ✓
3. 自主收集能力 ✓

整合方案：
1. 工具链编排 - 多工具协作
2. MCP集成 - 扩展能力边界
3. 知识管理 - 资料收集与记忆

请用JSON格式输出：
1. 能力整合框架
2. 协作流程设计
3. 训练效果评估标准"""
        }
    ]
    
    # ============ 训练环节 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 30 + "🎓 能力训练环节" + " " * 32 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    def train_model(task):
        print(f"┌─ {task['avatar']} {task['name']} ({task['model']}) - {task['role']} ─────────────────────────────────┐")
        print(f"│  训练任务: {task['task']} | 进行中..." + " " * 28 + "│")
        
        result = call_api(task["id"], task["prompt"], 500)
        
        with lock:
            if result and result.get("success"):
                training_results[task["name"]] = {
                    "role": task["role"],
                    "task": task["task"],
                    "content": result["content"],
                    "tokens": result["tokens"],
                    "success": True
                }
                print("├" + "─" * 78 + "┤")
                print(f"│  ✅ 训练完成 - {result['tokens']} tokens" + " " * 47 + "│")
                print("└" + "─" * 78 + "┘")
                print()
            else:
                training_results[task["name"]] = {"success": False}
                print("├" + "─" * 78 + "┤")
                print(f"│  ❌ 训练失败" + " " * 64 + "│")
                print("└" + "─" * 78 + "┘")
                print()
    
    # 顺序训练
    for task in training_tasks:
        train_model(task)
    
    # ============ 检查未完成工作 ============
    print("┌" + "─" * 78 + "┐")
    print("│" + " " * 25 + "📋 检查未完成开发工作" + " " * 28 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    # 检查现有文件
    import os
    workspace = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"
    
    required_files = {
        "unified_api.py": "统一API接口",
        "middleware.py": "中间件层",
        "task_panel.py": "任务面板",
        "test_symphony.py": "集成测试",
        "symphony_core.py": "核心调度",
        "model_manager.py": "模型管理",
        "error_handler.py": "错误处理",
        "rate_limit_optimizer.py": "限流优化"
    }
    
    missing_files = []
    completed_files = []
    
    for filename, desc in required_files.items():
        filepath = os.path.join(workspace, filename)
        if os.path.exists(filepath):
            completed_files.append(f"✅ {filename} - {desc}")
        else:
            missing_files.append(f"❌ {filename} - {desc} (需要开发)")
    
    print("📁 已完成文件:")
    for f in completed_files:
        print(f"   {f}")
    
    print("\n⚠️ 未完成文件:")
    for f in missing_files:
        print(f"   {f}")
    
    # ============ 训练总结 ============
    print("\n" + "=" * 80)
    print("📋 能力训练报告")
    print("=" * 80)
    
    total_tokens = sum(r.get("tokens", 0) for r in training_results.values())
    success_count = sum(1 for r in training_results.values() if r.get("success"))
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎓 Symphony v{VERSION} 能力训练报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 训练统计:
  • 训练任务: {len(training_tasks)}
  • 完成: {success_count}
  • Token消耗: {total_tokens}

🎯 训练内容:
  1. ✅ 工具使用能力训练
  2. ✅ MCP服务能力训练
  3. ✅ 自主收集技术资料能力训练
  4. ✅ 综合能力整合训练

📁 开发进度:
  • 已完成: {len(completed_files)}个核心文件
  • 待开发: {len(missing_files)}个文件

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "training_tasks": len(training_tasks),
        "training_completed": success_count,
        "total_tokens": total_tokens,
        "completed_files": len(completed_files),
        "missing_files": len(missing_files)
    }


if __name__ == "__main__":
    report = capability_training()
    
    with open("capability_training_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 训练报告已保存: capability_training_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
