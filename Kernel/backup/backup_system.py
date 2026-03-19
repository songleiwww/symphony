# Xujing Adaptive Backup System
# Backup module for Symphony kernel

import os
import sqlite3
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Path configuration
SYMPHONY_ROOT = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony'
DATA_DIR = os.path.join(SYMPHONY_ROOT, 'data')
KERNEL_DIR = os.path.join(SYMPHONY_ROOT, 'Kernel')
BACKUP_DIR = os.path.join(SYMPHONY_ROOT, 'backup')
TEMP_DIR = os.path.join(SYMPHONY_ROOT, 'temp')

# P4修复: 磁盘空间配置
MIN_DISK_SPACE_GB = 1.0  # 最小保留空间
SPACE_CHECK_THRESHOLD = 0.85  # 超过85%时警告

class XujingBackup:
    """Xujing adaptive backup system"""
    
    def __init__(self):
        self.backup_dir = BACKUP_DIR
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def check_disk_space(self) -> dict:
        """
        P4修复: 检查磁盘空间
        返回: {available_gb, total_gb, used_percent, is_safe}
        """
        try:
            import shutil as sh
            stat = sh.disk_usage(self.backup_dir)
            available_gb = stat.free / (1024**3)
            total_gb = stat.total / (1024**3)
            used_percent = (stat.used / stat.total) * 100
            is_safe = available_gb >= MIN_DISK_SPACE_GB
            
            return {
                "available_gb": round(available_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_percent": round(used_percent, 1),
                "is_safe": is_safe
            }
        except Exception as e:
            return {"error": str(e), "is_safe": True}
    
    def should_backup(self) -> tuple:
        """
        P4修复: 判断是否可以进行备份
        返回: (can_backup, reason)
        """
        space = self.check_disk_space()
        
        if "error" in space:
            return True, "空间检查跳过"
        
        if not space["is_safe"]:
            return False, f"磁盘空间不足: {space['available_gb']}GB < {MIN_DISK_SPACE_GB}GB"
        
        if space["used_percent"] > SPACE_CHECK_THRESHOLD * 100:
            return False, f"磁盘空间紧张: {space['used_percent']}%已使用"
        
        return True, "空间检查通过"
        
    def get_timestamp(self):
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Database backup
    def backup_database(self, db_name='symphony.db'):
        # P4修复: 先检查磁盘空间
        can_backup, reason = self.should_backup()
        if not can_backup:
            return False, f"跳过备份: {reason}"
        
        source = os.path.join(DATA_DIR, db_name)
        if not os.path.exists(source):
            return False, f"Source not found: {source}"
        
        timestamp = self.get_timestamp()
        backup_name = f"{db_name.replace('.db', '')}_backup_{timestamp}.db"
        dest = os.path.join(self.backup_dir, backup_name)
        
        try:
            shutil.copy2(source, dest)
            if self.verify_database(dest):
                return True, backup_name
            else:
                return False, "Verification failed"
        except Exception as e:
            return False, str(e)
    
    def verify_database(self, db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()
            return result[0] == 'ok'
        except:
            return False
    
    # Kernel code backup
    def backup_kernel(self):
        timestamp = self.get_timestamp()
        backup_name = f"kernel_backup_{timestamp}"
        dest = os.path.join(self.backup_dir, backup_name)
        
        try:
            if os.path.exists(KERNEL_DIR):
                shutil.copytree(KERNEL_DIR, dest)
            return True, backup_name
        except Exception as e:
            return False, str(e)
    
    # Config backup
    def backup_config(self):
        timestamp = self.get_timestamp()
        config_files = [
            'config.yaml',
            'tools.md',
            'SKILL.md',
            'SKILL_DEPLOYMENT.md'
        ]
        
        saved = []
        for f in config_files:
            source = os.path.join(SYMPHONY_ROOT, f)
            if os.path.exists(source):
                dest = os.path.join(self.backup_dir, f"{f}_{timestamp}")
                shutil.copy2(source, dest)
                saved.append(f)
        
        return len(saved) > 0, saved
    
    # Full backup
    def full_backup(self):
        results = {
            'timestamp': self.get_timestamp(),
            'databases': [],
            'kernel': None,
            'config': None,
            'status': 'success'
        }
        
        databases = ['symphony.db', 'evolution.db', 'symphony_template.db']
        for db in databases:
            success, msg = self.backup_database(db)
            results['databases'].append({'name': db, 'success': success, 'file': msg})
        
        success, msg = self.backup_kernel()
        results['kernel'] = {'success': success, 'file': msg}
        
        success, msg = self.backup_config()
        results['config'] = {'success': success, 'files': msg}
        
        self.save_backup_record(results)
        
        return results
    
    # Backup record management
    def save_backup_record(self, results):
        record_file = os.path.join(DATA_DIR, 'backup_records.json')
        
        records = []
        if os.path.exists(record_file):
            with open(record_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
        
        records.append(results)
        records = records[-100:]
        
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    # Cleanup old backups
    def cleanup_old_backups(self, keep_days=7):
        if not os.path.exists(self.backup_dir):
            return []
        
        cutoff = datetime.now() - timedelta(days=keep_days)
        cleaned = []
        
        for item in os.listdir(self.backup_dir):
            item_path = os.path.join(self.backup_dir, item)
            if os.path.isfile(item_path):
                mtime = datetime.fromtimestamp(os.path.getmtime(item_path))
                if mtime < cutoff:
                    os.remove(item_path)
                    cleaned.append(item)
            elif os.path.isdir(item_path):
                mtime = datetime.fromtimestamp(os.path.getmtime(item_path))
                if mtime < cutoff:
                    shutil.rmtree(item_path)
                    cleaned.append(item)
        
        return cleaned


# Global instance
_backup_system = None

def get_backup_system():
    global _backup_system
    if _backup_system is None:
        _backup_system = XujingBackup()
    return _backup_system


if __name__ == '__main__':
    import sys
    
    backup = get_backup_system()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'full':
            print("Running full backup...")
            result = backup.full_backup()
            print(f"Result: {result}")
            
        elif cmd == 'db':
            print("Running database backup...")
            result = backup.backup_database('symphony.db')
            print(f"Result: {result}")
            
        elif cmd == 'cleanup':
            print("Cleaning old backups...")
            cleaned = backup.cleanup_old_backups()
            print(f"Cleaned: {cleaned}")
            
        else:
            print("Unknown command")
    else:
        print("=== Xujing Backup System ===")
        print("Usage: python backup_system.py [full|db|cleanup]")
