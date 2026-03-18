#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境迁移管理器
支持无伤迁移和程序迁移
"""
import os
import json
import shutil
import sqlite3
from datetime import datetime

class MigrationManager:
    """序境迁移管理器"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            self.base_path = os.path.dirname(os.path.dirname(__file__))
        else:
            self.base_path = base_path
        
        self.data_path = os.path.join(self.base_path, "data")
        self.kernel_path = os.path.join(self.base_path, "Kernel")
    
    def get_status(self) -> dict:
        """获取系统状态"""
        status = {
            "database": False,
            "memory": False,
            "modules": []
        }
        
        # 检查数据库
        db_path = os.path.join(self.data_path, "symphony.db")
        if os.path.exists(db_path):
            status["database"] = {
                "exists": True,
                "size": os.path.getsize(db_path),
                "path": db_path
            }
        
        # 检查记忆存储
        mem_dir = os.path.join(self.kernel_path, "evolution", "memory_storage")
        if os.path.exists(mem_dir):
            files = os.listdir(mem_dir)
            status["memory"] = {
                "exists": True,
                "count": len(files),
                "path": mem_dir
            }
        
        # 检查核心模块
        core_files = ["workflow.py", "dispatcher.py", "roundtable_stream.py", "kernel_loader.py"]
        for f in core_files:
            fpath = os.path.join(self.kernel_path, f)
            if os.path.exists(fpath):
                status["modules"].append(f)
        
        return status
    
    def backup(self, target_path: str = None) -> dict:
        """创建完整备份"""
        if target_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_path = os.path.join(self.base_path, "backups", f"xujing_backup_{timestamp}")
        
        os.makedirs(target_path, exist_ok=True)
        
        result = {
            "target": target_path,
            "items": []
        }
        
        # 备份数据库
        db_path = os.path.join(self.data_path, "symphony.db")
        if os.path.exists(db_path):
            dest = os.path.join(target_path, "symphony.db")
            shutil.copy2(db_path, dest)
            result["items"].append({"type": "database", "file": "symphony.db"})
        
        # 备份用户记忆 (重要！不可丢失)
        mem_dir = os.path.join(self.kernel_path, "evolution", "memory_storage")
        if os.path.exists(mem_dir):
            mem_dest = os.path.join(target_path, "memory_storage")
            shutil.copytree(mem_dir, mem_dest)
            file_count = len(os.listdir(mem_dir))
            result["items"].append({"type": "user_memory", "file": "memory_storage", "count": file_count})
        
        # 备份工作记忆
        wm_path = os.path.join(self.kernel_path, "evolution", "working_memory.json")
        if os.path.exists(wm_path):
            dest = os.path.join(target_path, "working_memory.json")
            shutil.copy2(wm_path, dest)
            result["items"].append({"type": "working_memory", "file": "working_memory.json"})
        
        # 备份核心文件
        core_files = ["workflow.py", "dispatcher.py", "roundtable_stream.py", "roundtable.py"]
        for f in core_files:
            src = os.path.join(self.kernel_path, f)
            if os.path.exists(src):
                dest = os.path.join(target_path, f)
                shutil.copy2(src, dest)
                result["items"].append({"type": "module", "file": f})
        
        # 备份配置
        config_files = ["DISPATCH_RULES.md", "KERNEL_ORDER.md", "DEVELOPMENT.md"]
        for f in config_files:
            src = os.path.join(self.kernel_path, f)
            if os.path.exists(src):
                dest = os.path.join(target_path, f)
                shutil.copy2(src, dest)
                result["items"].append({"type": "config", "file": f})
        
        result["status"] = "success"
        return result
    
    def restore(self, backup_path: str) -> dict:
        """从备份恢复"""
        result = {"status": "pending"}
        
        # 恢复数据库
        db_backup = os.path.join(backup_path, "symphony.db")
        if os.path.exists(db_backup):
            db_dest = os.path.join(self.data_path, "symphony.db")
            shutil.copy2(db_backup, db_dest)
            result["database"] = "restored"
        
        # 恢复用户记忆 (重要！)
        mem_backup = os.path.join(backup_path, "memory_storage")
        if os.path.exists(mem_backup):
            mem_dest = os.path.join(self.kernel_path, "evolution", "memory_storage")
            if os.path.exists(mem_dest):
                shutil.rmtree(mem_dest)
            shutil.copytree(mem_backup, mem_dest)
            result["memory"] = "restored"
        
        # 恢复工作记忆
        wm_backup = os.path.join(backup_path, "working_memory.json")
        if os.path.exists(wm_backup):
            wm_dest = os.path.join(self.kernel_path, "evolution", "working_memory.json")
            shutil.copy2(wm_backup, wm_dest)
        
        # 恢复核心文件
        core_files = ["workflow.py", "dispatcher.py", "roundtable_stream.py"]
        for f in core_files:
            src = os.path.join(backup_path, f)
            if os.path.exists(src):
                dest = os.path.join(self.kernel_path, f)
                shutil.copy2(src, dest)
        
        result["status"] = "success"
        return result
    
    def export_config(self, include_memory: bool = False) -> dict:
        """
        导出配置
        include_memory: 是否包含记忆（程序迁移时设为False）
        """
        mem_dir = os.path.join(self.kernel_path, "evolution", "memory_storage")
        memory_count = 0
        if os.path.exists(mem_dir):
            memory_count = len(os.listdir(mem_dir))
        
        return {
            "version": "9.0",
            "exported_at": datetime.now().isoformat(),
            "streaming_enabled": True,
            "database_path": self.data_path,
            "modules": self.get_status()["modules"],
            "user_memory": {
                "count": memory_count,
                "included": include_memory,
                "critical": True,
                "note": "程序迁移不带记忆" if not include_memory else "完整迁移含记忆"
            }
        }
    
    def migrate_program(self, target_path: str) -> dict:
        """
        程序迁移（不带记忆）
        仅迁移核心程序文件
        """
        os.makedirs(target_path, exist_ok=True)
        
        result = {
            "type": "program_only",
            "target": target_path,
            "items": []
        }
        
        # 仅迁移核心模块
        core_files = ["workflow.py", "dispatcher.py", "roundtable_stream.py", "roundtable.py"]
        for f in core_files:
            src = os.path.join(self.kernel_path, f)
            if os.path.exists(src):
                dest = os.path.join(target_path, f)
                shutil.copy2(src, dest)
                result["items"].append({"type": "module", "file": f})
        
        # 迁移配置文件
        config_files = ["DISPATCH_RULES.md", "KERNEL_ORDER.md"]
        for f in config_files:
            src = os.path.join(self.kernel_path, f)
            if os.path.exists(src):
                dest = os.path.join(target_path, f)
                shutil.copy2(src, dest)
                result["items"].append({"type": "config", "file": f})
        
        result["status"] = "success"
        result["note"] = "程序迁移完成（不含用户记忆）"
        return result


if __name__ == "__main__":
    mg = MigrationManager()
    print("=== 序境迁移管理器 ===")
    status = mg.get_status()
    print(f"数据库: {'✓' if status['database'] else '✗'}")
    print(f"记忆存储: {'✓' if status['memory'] else '✗'}")
    print(f"核心模块: {len(status['modules'])} 个")
