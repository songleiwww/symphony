#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境系统 - OpenClaw Skills 接口
符合 OpenClaw Skills 规范，提供自动化多智能体调度服务
"""
import os
import sys
import json
import time
from typing import Dict, List, Optional, Any

# 添加项目路径 - 支持从不同目录导入
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(PROJECT_DIR, "core")
KERNEL_DIR = os.path.join(PROJECT_DIR, "Kernel")

# 添加路径（去重）
for path in [PROJECT_DIR, CORE_DIR, KERNEL_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# 导入核心模块
try:
    from Kernel.kernel_loader import get_kernel
except ModuleNotFoundError:
    # 尝试相对导入
    import importlib.util
    spec = importlib.util.spec_from_file_location("kernel_loader", os.path.join(KERNEL_DIR, "kernel_loader.py"))
    kernel_loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kernel_loader)
    get_kernel = kernel_loader.get_kernel

try:
    from core.scheduler import get_scheduler
    from core.task_manager import get_task_manager, Task, TaskStatus
    from core.model_call_manager import get_model_manager
    from core.collaboration_engine import get_collaboration_engine, CollaborationMode
    from core.memory_system import get_memory_system
    from core.fault_tolerance import get_fault_tolerance
except ModuleNotFoundError:
    # 尝试其他导入方式
    pass

class SymphonySystem:
    """序境系统主类"""
    
    def __init__(self):
        self.kernel = get_kernel()
        self.scheduler = get_scheduler()
        self.task_manager = get_task_manager()
        self.model_manager = get_model_manager()
        self.collab_engine = get_collaboration_engine()
        self.memory = get_memory_system()
        self.fault_tolerance = get_fault_tolerance()
        
        self.version = "1.0.0"
        self.name = "序境系统"
        self.description = "全自动自适应多引擎调度与协作系统"
    
    def process_task(self, content: str, mode: str = "auto", 
                   role_ids: List[str] = None, **kwargs) -> Dict:
        """处理任务（主入口）"""
        try:
            # 1. 创建任务
            task = self.task_manager.create_task(
                content=content,
                task_type=kwargs.get("task_type", "通用任务"),
                priority=kwargs.get("priority", 3),
                created_by=kwargs.get("created_by", "user")
            )
            
            # 2. 调度任务
            success, matched_roles, msg = self.scheduler.schedule_task(task)
            
            if not success:
                return {
                    "success": False,
                    "task_id": task.task_id,
                    "error": msg
                }
            
            # 3. 执行任务
            if mode == "parallel":
                collab = self.collab_engine.create_collaboration(
                    task, CollaborationMode.PARALLEL, 
                    role_ids=[r["role_id"] for r in matched_roles]
                )
                result = self.collab_engine.run_collaboration(collab["collab_id"])
            elif mode == "pipeline":
                collab = self.collab_engine.create_collaboration(
                    task, CollaborationMode.PIPELINE,
                    role_ids=[r["role_id"] for r in matched_roles]
                )
                result = self.collab_engine.run_collaboration(collab["collab_id"])
            elif mode == "master_slave":
                collab = self.collab_engine.create_collaboration(
                    task, CollaborationMode.MASTER_SLAVE,
                    role_ids=[r["role_id"] for r in matched_roles]
                )
                result = self.collab_engine.run_collaboration(collab["collab_id"])
            elif mode == "review":
                collab = self.collab_engine.create_collaboration(
                    task, CollaborationMode.REVIEW,
                    role_ids=[r["role_id"] for r in matched_roles[:2]]
                )
                result = self.collab_engine.run_collaboration(collab["collab_id"])
            else:
                # 自动模式
                best_role = matched_roles[0]
                model_name = best_role["model_name"]
                
                success, result_content, meta = self.model_manager.call_model(
                    model_name, 
                    f"作为{best_role['role_name']}，请完成：{content}"
                )
                
                result = {
                    "success": success,
                    "results": [{
                        "role_id": best_role["role_id"],
                        "role_name": best_role["role_name"],
                        "content": result_content,
                        "meta": meta
                    }] if success else [],
                    "errors": [result_content] if not success else []
                }
            
            # 4. 更新任务状态
            if result.get("results"):
                self.task_manager.update_task_status(task.task_id, TaskStatus.COMPLETED)
            else:
                self.task_manager.update_task_status(task.task_id, TaskStatus.FAILED)
            
            # 5. 保存到记忆
            self.memory.add_memory(
                content=f"任务完成：{content[:50]}... 结果：{len(result.get('results', []))}个角色",
                memory_type="short_term",
                importance=0.6,
                source="system",
                tags=["任务", "完成"]
            )
            
            return {
                "success": True,
                "task_id": task.task_id,
                "mode": mode,
                "matched_roles": matched_roles,
                "result": result,
                "duration": time.time() - task.created_at
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "roles_count": len(self.kernel.roles),
            "models_count": len(self.kernel.models),
            "task_stats": self.task_manager.get_task_statistics(),
            "memory_stats": self.memory.get_statistics()
        }
    
    def search_knowledge(self, query: str) -> List[Dict]:
        """搜索知识记忆"""
        return self.memory.search_memory(query)
    
    def add_knowledge(self, content: str, importance: float = 0.7, **kwargs) -> str:
        """添加知识到长期记忆"""
        return self.memory.add_memory(
            content=content,
            memory_type="long_term",
            importance=importance,
            **kwargs
        )

# 全局单例
_symphony_instance: Optional['SymphonySystem'] = None

def get_symphony() -> 'SymphonySystem':
    """获取序境系统单例"""
    global _symphony_instance
    if _symphony_instance is None:
        _symphony_instance = SymphonySystem()
    return _symphony_instance

# ========== 命令行接口 ==========

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="序境系统")
    parser.add_argument("command", choices=["task", "status", "roles", "models", "memory", "add-memory"],
                       help="命令")
    parser.add_argument("--content", "-c", help="任务内容")
    parser.add_argument("--mode", "-m", default="auto", help="处理模式")
    parser.add_argument("--query", "-q", help="搜索查询")
    parser.add_argument("--importance", "-i", type=float, default=0.7, help="知识重要性")
    
    args = parser.parse_args()
    
    symphony = get_symphony()
    
    if args.command == "task":
        if not args.content:
            print("错误：任务内容不能为空")
            sys.exit(1)
        result = symphony.process_task(args.content, args.mode)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "status":
        status = symphony.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    elif args.command == "roles":
        roles = symphony.kernel.roles
        print(json.dumps(roles, ensure_ascii=False, indent=2))
    elif args.command == "models":
        models = symphony.kernel.models
        print(json.dumps(models, ensure_ascii=False, indent=2))
    elif args.command == "memory":
        if not args.query:
            print("错误：搜索查询不能为空")
            sys.exit(1)
        results = symphony.search_knowledge(args.query)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.command == "add-memory":
        if not args.content:
            print("错误：知识内容不能为空")
            sys.exit(1)
        mem_id = symphony.add_knowledge(args.content, args.importance)
        print(f"知识已添加: {mem_id}")
