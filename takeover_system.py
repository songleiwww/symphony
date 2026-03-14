#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v3.6.0 - 任务接管与备份系统
当被调度的模型未完成工作时，备份模型自动接管并完成
"""
import sys
import json
import time
import requests
import threading
import os
from datetime import datetime
from typing import Dict, List, Optional, Callable
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


VERSION = "3.6.0"
WORKSPACE = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_index: int, prompt: str, max_tokens=150, caller_id="system"):
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
    except:
        pass
    return None


class TaskTakeoverSystem:
    """任务接管与备份系统"""
    
    def __init__(self):
        self.tasks = {}                    # task_id -> task_info
        self.backup_models = {}            # model_index -> backup_info
        self.takeover_history = []          # 接管历史
        self.failure_threshold = 3          # 失败次数阈值
        self.timeout_seconds = 30          # 超时时间
        self.monitoring = False
        self.total_tokens = 0
    
    def register_backup_model(self, model_index: int, priority: int = 1):
        """注册备份模型"""
        enabled = get_enabled_models()
        if model_index < len(enabled):
            model = enabled[model_index]
            self.backup_models[model_index] = {
                "name": model["name"],
                "model_id": model["model_id"],
                "priority": priority,
                "takeover_count": 0,
                "status": "ready"
            }
            print(f"  ✅ 注册备份模型: {model['name']} (优先级: {priority})")
    
    def assign_task(self, task_id: str, task: dict, primary_model_index: int, backup_model_indices: List[int]):
        """分配任务（主模型+备份模型）"""
        self.tasks[task_id] = {
            "task_id": task_id,
            "task": task,
            "primary_model": primary_model_index,
            "backup_models": backup_model_indices,
            "status": "pending",
            "assigned_at": datetime.now().isoformat(),
            "attempts": 0,
            "result": None
        }
        
        print(f"\n📋 任务分配: {task_id}")
        print(f"   主模型: {primary_model_index}")
        print(f"   备份模型: {backup_model_indices}")
        
        return task_id
    
    def execute_with_takeover(self, task_id: str, executor: Callable) -> dict:
        """执行任务，支持自动接管"""
        task_info = self.tasks.get(task_id)
        if not task_info:
            return {"status": "error", "message": "任务不存在"}
        
        task = task_info["task"]
        primary = task_info["primary_model"]
        backups = task_info["backup_models"]
        
        # 尝试主模型
        print(f"\n🔄 尝试执行任务 {task_id}...")
        print(f"   [主模型 #{primary}] 执行中...")
        
        result = executor(primary, task)
        
        if result and result.get("success"):
            task_info["status"] = "completed"
            task_info["result"] = result
            print(f"   ✅ 主模型成功完成任务")
            return result
        
        # 主模型失败，记录尝试
        task_info["attempts"] += 1
        print(f"   ❌ 主模型失败 (尝试 {task_info['attempts']}/{self.failure_threshold})")
        
        # 自动启用备份模型接管
        print(f"\n🔄 启动自动接管机制...")
        
        for i, backup_idx in enumerate(backups):
            print(f"   [备份模型 #{backup_idx}] 尝试接管...")
            
            backup_result = executor(backup_idx, task)
            
            if backup_result and backup_result.get("success"):
                # 接管成功
                task_info["status"] = "completed_by_backup"
                task_info["result"] = backup_result
                task_info["takeover_by"] = backup_idx
                
                # 记录接管历史
                self.takeover_history.append({
                    "task_id": task_id,
                    "original_model": primary,
                    "takeover_model": backup_idx,
                    "takeover_at": datetime.now().isoformat(),
                    "success": True
                })
                
                # 更新备份模型统计
                if backup_idx in self.backup_models:
                    self.backup_models[backup_idx]["takeover_count"] += 1
                
                print(f"   ✅ 备份模型 #{backup_idx} 成功接管并完成任务!")
                return backup_result
            
            print(f"   ❌ 备份模型 #{backup_idx} 也失败")
        
        # 所有模型都失败
        task_info["status"] = "failed"
        task_info["result"] = {"status": "error", "message": "所有模型均失败"}
        
        self.takeover_history.append({
            "task_id": task_id,
            "original_model": primary,
            "takeover_model": None,
            "takeover_at": datetime.now().isoformat(),
            "success": False
        })
        
        return {"status": "error", "message": "任务失败，所有模型均无法完成"}
    
    def get_status(self) -> dict:
        """获取系统状态"""
        return {
            "total_tasks": len(self.tasks),
            "completed": len([t for t in self.tasks.values() if t["status"] == "completed"]),
            "completed_by_backup": len([t for t in self.tasks.values() if t["status"] == "completed_by_backup"]),
            "failed": len([t for t in self.tasks.values() if t["status"] == "failed"]),
            "pending": len([t for t in self.tasks.values() if t["status"] == "pending"]),
            "backup_models": {str(k): v for k, v in self.backup_models.items()},
            "takeover_history": self.takeover_history
        }


def test_takeover_system():
    """测试任务接管系统"""
    
    print("=" * 80)
    print(f"🎼 Symphony v{VERSION} - 任务接管与备份系统测试")
    print("=" * 80)
    
    system = TaskTakeoverSystem()
    
    # 注册备份模型
    print("\n[1] 注册备份模型")
    system.register_backup_model(0, priority=1)   # 智谱GLM-4-Flash
    system.register_backup_model(12, priority=2)  # MiniMax-M2.5
    system.register_backup_model(14, priority=3)  # GLM-5
    
    # 创建测试任务
    print("\n[2] 创建测试任务")
    task_id = system.assign_task(
        task_id="test_task_001",
        task={"prompt": "请用50字解释什么是机器学习"},
        primary_model_index=0,  # 主模型
        backup_model_indices=[12, 14]  # 备份模型
    )
    
    # 模拟执行器（真实API调用）
    def mock_executor(model_idx: int, task: dict) -> dict:
        print(f"      调用模型 #{model_idx}: {task['prompt'][:30]}...")
        result = call_api(model_idx, task["prompt"], 80)
        if result:
            return {"success": True, "content": result["content"], "model": model_idx}
        return {"success": False}
    
    # 执行任务
    print("\n[3] 执行任务（测试接管机制）")
    result = system.execute_with_takeover(task_id, mock_executor)
    
    # 状态报告
    print("\n" + "=" * 80)
    print("📊 任务接管系统状态报告")
    print("=" * 80)
    
    status = system.get_status()
    
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎵 Symphony v{VERSION} 任务接管系统
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 任务统计:
  • 总任务数: {status['total_tasks']}
  • 主模型完成: {status['completed']}
  • 备份接管完成: {status['completed_by_backup']}
  • 失败: {status['failed']}
  • 待处理: {status['pending']}

🔄 接管历史:
  • 接管次数: {len(status['takeover_history'])}
""")
    
    if status['takeover_history']:
        for h in status['takeover_history']:
            print(f"    - 任务 {h['task_id']}: {h['original_model']} → {h['takeover_model']} ({'成功' if h['success'] else '失败'})")
    
    print(f"""
📊 备份模型统计:
""")
    
    for idx, info in status['backup_models'].items():
        print(f"    • 模型 #{idx} ({info['name']}): 接管次数 {info['takeover_count']}")
    
    print(f"""
🔥 核心功能:
  ✅ 主模型失败自动检测
  ✅ 备份模型自动接管
  ✅ 接管历史完整记录
  ✅ 统计报告自动生成

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    return {
        "version": VERSION,
        "datetime": datetime.now().isoformat(),
        "status": status
    }


if __name__ == "__main__":
    report = test_takeover_system()
    
    with open("takeover_system_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 报告已保存: takeover_system_report.json")
    print("\nSymphony - 智韵交响，共创华章！")
