# -*- coding: utf-8 -*-
"""
模块化系统 - 迭代策略
==================
原理: 从现在进行时到过去进行时
- 用户/开发者可删除所有文件进行迭代
- 根据 memory 记忆和现有文件重构功能
- 模块化设计，用户可选择保留/删除

核心模块:
1. kernel - 内核核心 (必需)
2. data - 数据存储 (必需)
3. core - 核心引擎 (可选)
4. skills - 技能扩展 (可选)
"""
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

# 路径配置
SKILL_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony'

# 模块定义
MODULES = {
    'kernel': {
        'name': '内核核心',
        'required': True,
        'files': ['kernel_loader.py', 'config_manager.py', 'dispatch_manager.py', 'kernel_strategy.py'],
        'desc': '加载配置、管理官署官属、多模调度'
    },
    'data': {
        'name': '数据存储',
        'required': True,
        'files': ['symphony.db'],
        'desc': '官署、官属、模型、规则数据'
    },
    'core': {
        'name': '核心引擎',
        'required': False,
        'files': ['symphony_api.py', 'model_call_manager.py', 'scheduler.py', 'task_manager.py'],
        'desc': 'API调用、任务调度、协作引擎'
    },
    'old': {
        'name': '历史文件',
        'required': False,
        'files': ['*.json', '*.py'],
        'desc': '历史版本，禁用'
    }
}

class ModularSystem:
    """模块化系统 - 支持迭代"""
    
    def __init__(self):
        self.base_dir = SKILL_DIR
        self.modules = MODULES
        self.active_modules = []
        
    def scan_modules(self) -> Dict:
        """扫描可用模块"""
        print("="*60)
        print("模块扫描")
        print("="*60)
        
        for module_id, info in self.modules.items():
            module_path = os.path.join(self.base_dir, module_id)
            
            if os.path.exists(module_path):
                print(f"✅ {info['name']}: 存在")
                self.active_modules.append(module_id)
            else:
                print(f"❌ {info['name']}: 不存在")
        
        return {
            'active': self.active_modules,
            'total': len(self.modules)
        }
    
    def rebuild_from_db(self) -> bool:
        """从数据库重构内核"""
        db_path = os.path.join(self.base_dir, 'data', 'symphony.db')
        
        if not os.path.exists(db_path):
            print("❌ 数据库不存在，需要初始化")
            return False
        
        print("\n=== 从数据库重构 ===")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查核心表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        print(f"数据库表: {tables}")
        
        # 检查内核规则
        if '内核规则表' in tables:
            cursor.execute("SELECT 规则名称, 规则内容 FROM 内核规则表")
            rules = cursor.fetchall()
            print(f"\n内核规则 ({len(rules)}):")
            for name, content in rules:
                print(f"  • {name}")
        
        conn.close()
        return True
    
    def get_module_status(self) -> Dict:
        """获取模块状态"""
        status = {}
        for module_id, info in self.modules.items():
            module_path = os.path.join(self.base_dir, module_id)
            status[module_id] = {
                'name': info['name'],
                'exists': os.path.exists(module_path),
                'required': info['required'],
                'desc': info['desc']
            }
        return status
    
    def list_keepable_modules(self) -> List[Dict]:
        """列出可保留的模块"""
        keepable = []
        for module_id, info in self.modules.items():
            if not info['required']:
                keepable.append({
                    'id': module_id,
                    'name': info['name'],
                    'desc': info['desc']
                })
        return keepable


def main():
    system = ModularSystem()
    
    # 1. 扫描模块
    scan_result = system.scan_modules()
    
    # 2. 获取状态
    status = system.get_module_status()
    
    print("\n=== 模块状态 ===")
    for module_id, info in status.items():
        mark = "⭐" if info['required'] else "○"
        state = "✅" if info['exists'] else "❌"
        print(f"{mark} {info['name']} {state}")
    
    # 3. 可保留模块
    keepable = system.list_keepable_modules()
    print("\n=== 可选模块 (用户可选择保留) ===")
    for m in keepable:
        print(f"  • {m['name']}: {m['desc']}")
    
    # 4. 从数据库重构
    system.rebuild_from_db()


if __name__ == "__main__":
    main()
