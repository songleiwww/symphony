#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本更新管理器 - 系统版本管理与自动更新
"""
import os
import shutil
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from permission_manager import get_permission_manager

class UpdateManager:
    def __init__(self, project_dir: str = None):
        if project_dir is None:
            self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.project_dir = project_dir
            
        self.version_file = os.path.join(self.project_dir, "VERSION")
        self.backup_dir = os.path.join(self.project_dir, "backups", "versions")
        self.perm_manager = get_permission_manager()
        
        # 确保目录存在
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def get_current_version(self) -> str:
        """获取当前版本号"""
        if not os.path.exists(self.version_file):
            return "0.0.1"
            
        with open(self.version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def set_current_version(self, version: str, release_notes: str = "") -> bool:
        """设置当前版本号"""
        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                f.write(version)
            
            # 写入版本历史
            history_file = os.path.join(self.project_dir, "CHANGELOG.md")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(history_file, 'a', encoding='utf-8') as f:
                f.write(f"\n## v{version} ({timestamp})\n")
                if release_notes:
                    f.write(f"\n{release_notes}\n")
            
            return True
        except Exception as e:
            print(f"设置版本号失败: {e}")
            return False
    
    def create_backup(self, version: str = None) -> str:
        """创建当前版本完整备份"""
        if version is None:
            version = self.get_current_version()
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"v{version}_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # 排除备份目录、日志、临时文件
        exclude_dirs = ["backups", "logs", "tmp", "__pycache__", ".git"]
        exclude_files = [".env", "*.db", "*.pyc"]
        
        def ignore_func(path, names):
            ignored = []
            for name in names:
                full_path = os.path.join(path, name)
                if os.path.isdir(full_path) and name in exclude_dirs:
                    ignored.append(name)
                elif os.path.isfile(full_path):
                    for pattern in exclude_files:
                        if name.endswith(pattern[1:]) if pattern.startswith("*") else name == pattern:
                            ignored.append(name)
                            break
            return ignored
        
        shutil.copytree(self.project_dir, backup_path, ignore=ignore_func)
        
        # 保存备份元数据
        meta = {
            "version": version,
            "timestamp": timestamp,
            "backup_path": backup_path,
            "project_dir": self.project_dir
        }
        
        with open(os.path.join(backup_path, "backup_meta.json"), 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        
        return backup_path
    
    def list_backups(self) -> List[Dict]:
        """列出所有备份"""
        backups = []
        if not os.path.exists(self.backup_dir):
            return backups
            
        for backup_name in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, backup_name)
            meta_path = os.path.join(backup_path, "backup_meta.json")
            
            if os.path.isdir(backup_path) and os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    backups.append(meta)
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def restore_backup(self, backup_path: str) -> Tuple[bool, str]:
        """从备份恢复"""
        if not os.path.exists(backup_path):
            return False, "备份不存在"
            
        meta_path = os.path.join(backup_path, "backup_meta.json")
        if not os.path.exists(meta_path):
            return False, "无效的备份文件"
            
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        # 先备份当前版本
        current_version = self.get_current_version()
        current_backup = self.create_backup(f"{current_version}_pre_restore")
        
        try:
            # 恢复文件
            for root, dirs, files in os.walk(backup_path):
                # 跳过元数据文件
                if "backup_meta.json" in files:
                    files.remove("backup_meta.json")
                
                rel_path = os.path.relpath(root, backup_path)
                target_root = os.path.join(self.project_dir, rel_path)
                
                # 创建目标目录
                if not os.path.exists(target_root):
                    os.makedirs(target_root)
                
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_root, file)
                    shutil.copy2(src_file, dst_file)
            
            # 记录日志
            self.perm_manager.log_operation(
                "system", "版本恢复", 
                f"从备份恢复版本: {meta['version']}, 备份路径: {backup_path}"
            )
            
            return True, f"恢复成功，当前版本已恢复到 v{meta['version']}"
        except Exception as e:
            # 恢复失败，回滚到之前的备份
            self.restore_backup(current_backup)
            return False, f"恢复失败: {str(e)}"
    
    def check_for_updates(self, update_url: str = None) -> Optional[Dict]:
        """检查是否有新版本"""
        if update_url is None:
            # 默认从GitHub检查更新
            update_url = "https://api.github.com/repos/songleiwww/symphony/releases/latest"
            
        try:
            resp = requests.get(update_url, timeout=10)
            resp.raise_for_status()
            release_info = resp.json()
            
            latest_version = release_info["tag_name"].lstrip("v")
            current_version = self.get_current_version()
            
            # 版本比较
            from packaging import version
            has_update = version.parse(latest_version) > version.parse(current_version)
            
            return {
                "has_update": has_update,
                "current_version": current_version,
                "latest_version": latest_version,
                "release_notes": release_info.get("body", ""),
                "download_url": release_info.get("zipball_url", "")
            }
        except Exception as e:
            print(f"检查更新失败: {e}")
            return None
    
    def apply_update(self, update_package: str, version: str, release_notes: str = "") -> Tuple[bool, str]:
        """应用更新包"""
        try:
            # 1. 备份当前版本
            backup_path = self.create_backup()
            print(f"已备份当前版本到: {backup_path}")
            
            # 2. 解压更新包（假设是zip文件）
            import tempfile
            import zipfile
            
            temp_dir = tempfile.mkdtemp()
            
            with zipfile.ZipFile(update_package, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 3. 覆盖更新文件
            update_root = os.path.join(temp_dir, os.listdir(temp_dir)[0]) if len(os.listdir(temp_dir)) == 1 else temp_dir
            
            for root, dirs, files in os.walk(update_root):
                rel_path = os.path.relpath(root, update_root)
                target_root = os.path.join(self.project_dir, rel_path)
                
                if not os.path.exists(target_root):
                    os.makedirs(target_root)
                
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_root, file)
                    shutil.copy2(src_file, dst_file)
            
            # 4. 更新版本号
            self.set_current_version(version, release_notes)
            
            # 5. 清理临时文件
            shutil.rmtree(temp_dir)
            
            # 6. 记录日志
            self.perm_manager.log_operation(
                "system", "系统更新", 
                f"更新到版本 v{version}, 备份路径: {backup_path}"
            )
            
            return True, f"更新成功，当前版本: v{version}"
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def get_version_history(self) -> List[Dict]:
        """获取版本历史"""
        changelog_file = os.path.join(self.project_dir, "CHANGELOG.md")
        if not os.path.exists(changelog_file):
            return []
            
        history = []
        current_version = None
        current_content = []
        
        with open(changelog_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("## v"):
                    if current_version:
                        history.append({
                            "version": current_version,
                            "content": "\n".join(current_content).strip()
                        })
                    # 解析版本号和日期
                    parts = line.split("(", 1)
                    current_version = parts[0].strip()[3:]
                    current_content = []
                elif current_version and line:
                    current_content.append(line)
        
        if current_version:
            history.append({
                "version": current_version,
                "content": "\n".join(current_content).strip()
            })
        
        return sorted(history, key=lambda x: x["version"], reverse=True)

# 单例实例
_update_manager_instance: Optional[UpdateManager] = None

def get_update_manager() -> UpdateManager:
    """获取更新管理器单例"""
    global _update_manager_instance
    if _update_manager_instance is None:
        _update_manager_instance = UpdateManager()
    return _update_manager_instance

if __name__ == "__main__":
    # 测试更新管理器
    update_manager = get_update_manager()
    
    current_version = update_manager.get_current_version()
    print(f"当前版本: v{current_version}")
    
    # 创建测试备份
    backup_path = update_manager.create_backup()
    print(f"创建备份: {backup_path}")
    
    # 列出备份
    backups = update_manager.list_backups()
    print(f"备份数量: {len(backups)}")
    
    print("\n✅ 更新管理器初始化完成")
