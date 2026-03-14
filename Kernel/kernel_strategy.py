# -*- coding: utf-8 -*-
"""
序境内核策略 - 自动初始化与迭代
===================================
策略:
1. 如果 skills/symphony/kernel 不存在则创建
2. 参考旧内核文件但必须迭代
3. 迭代策略: 使用 symphony.db 数据, 组织多模态协作
"""
import sqlite3
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional

# 路径配置
SKILL_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony'
KERNEL_DIR = os.path.join(SKILL_DIR, 'Kernel')
DATA_DIR = os.path.join(SKILL_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'symphony.db')
OLD_DIR = os.path.join(SKILL_DIR, 'old')


class KernelStrategy:
    """内核策略引擎"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.kernel_dir = KERNEL_DIR
        self.data = {}
        
    def initialize(self) -> bool:
        """初始化内核"""
        print("="*60)
        print("序境内核策略 - 自动初始化")
        print("="*60)
        
        # 1. 检查并创建目录结构
        self._ensure_directories()
        
        # 2. 验证数据库
        if not self._verify_database():
            print("❌ 数据库验证失败")
            return False
        
        # 3. 加载数据
        self._load_data()
        
        # 4. 生成内核文件
        self._generate_kernel_files()
        
        print("\n✅ 内核初始化完成")
        return True
    
    def _ensure_directories(self):
        """确保目录结构存在"""
        dirs = [
            (KERNEL_DIR, 'Kernel内核目录'),
            (DATA_DIR, 'data数据目录'),
        ]
        
        for dir_path, desc in dirs:
            if os.path.exists(dir_path):
                print(f"✅ {desc}已存在")
            else:
                print(f"📁 正在创建{desc}...")
                os.makedirs(dir_path, exist_ok=True)
                print(f"✅ {desc}创建完成")
    
    def _verify_database(self) -> bool:
        """验证数据库"""
        if not os.path.exists(self.db_path):
            print(f"❌ 数据库不存在: {self.db_path}")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查核心表
        required_tables = ['官署表', '官属角色表', '模型配置表', '内核规则表']
        all_exist = True
        
        for table in required_tables:
            cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone()[0] > 0
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count}条")
            else:
                print(f"❌ {table}: 不存在")
                all_exist = False
        
        conn.close()
        return all_exist
    
    def _load_data(self):
        """从数据库加载数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 加载规则
        cursor.execute("SELECT id, 规则名称, 规则内容, 优先级 FROM 内核规则表 WHERE 状态='启用' ORDER BY 优先级")
        self.data['rules'] = [{'id': r[0], 'name': r[1], 'content': r[2], 'priority': r[3]} for r in cursor.fetchall()]
        
        # 加载官署
        cursor.execute("SELECT id, 名称, 级别, 职责, 编制 FROM 官署表 ORDER BY 级别, 名称")
        self.data['offices'] = [{'id': r[0], 'name': r[1], 'level': r[2], 'duty': r[3], 'quota': r[4]} for r in cursor.fetchall()]
        
        # 加载官属
        cursor.execute("SELECT id, 姓名, 官职, 官署ID, 模型名称, 模型服务商 FROM 官属角色表")
        self.data['roles'] = [{'id': r[0], 'name': r[1], 'title': r[2], 'office_id': r[3], 'model': r[4], 'provider': r[5]} for r in cursor.fetchall()]
        
        # 加载模型
        cursor.execute("SELECT 模型名称, 服务商, url, 模型类型 FROM 模型配置表 WHERE 状态='正常'")
        self.data['models'] = [{'name': r[0], 'provider': r[1], 'url': r[2], 'type': r[3]} for r in cursor.fetchall()]
        
        conn.close()
        
        print(f"\n📊 数据加载完成:")
        print(f"   规则: {len(self.data['rules'])}条")
        print(f"   官署: {len(self.data['offices'])}个")
        print(f"   官属: {len(self.data['roles'])}人")
        print(f"   模型: {len(self.data['models'])}个")
    
    def _generate_kernel_files(self):
        """生成内核文件"""
        print("\n📝 生成内核文件...")
        
        # 1. __init__.py
        self._generate_init()
        
        # 2. kernel_loader.py (已存在则迭代)
        self._generate_loader()
        
        # 3. config_manager.py
        self._generate_config_manager()
        
        # 4. dispatch_manager.py (多模调度)
        self._generate_dispatch_manager()
        
        print("✅ 内核文件生成完成")
    
    def _generate_init(self):
        """生成 __init__.py"""
        content = '''# -*- coding: utf-8 -*-
"""
序境交响内核
策略: 现在进行时永远优先过去进行时
数据源: symphony.db (唯一数据源)
"""
__version__ = "2.0.0"
__author__ = "序境系统"

from .kernel_loader import KernelLoader
from .config_manager import ConfigManager
from .dispatch_manager import DispatchManager

__all__ = ['KernelLoader', 'ConfigManager', 'DispatchManager']
'''
        self._write_file('__init__.py', content)
    
    def _generate_loader(self):
        """生成 kernel_loader.py (迭代版本)"""
        content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内核加载器 - 从 symphony.db 加载配置
迭代版本: 支持规则/官署/官属/模型
"""
import sqlite3
import os
from typing import Dict, List, Optional

class KernelLoader:
    """内核加载器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            current_file = os.path.abspath(__file__)
            project_dir = os.path.dirname(os.path.dirname(current_file))
            self.db_path = os.path.join(project_dir, "data", "symphony.db")
        else:
            self.db_path = db_path
        
        self.rules: List[Dict] = []
        self.offices: List[Dict] = []
        self.roles: List[Dict] = []
        self.models: Dict[str, Dict] = []
        
    def load_all(self) -> bool:
        """加载所有配置"""
        try:
            self.load_rules()
            self.load_offices()
            self.load_roles()
            self.load_models()
            return True
        except Exception as e:
            print(f"加载失败: {{e}}")
            return False
    
    def load_rules(self) -> bool:
        """加载内核规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(内核规则表)")
        columns = [col[1] for col in cursor.fetchall()]
        cursor.execute("SELECT * FROM 内核规则表 WHERE 状态='启用' ORDER BY 优先级")
        self.rules = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        print(f"加载规则: {{len(self.rules)}}条")
        return True
    
    def load_offices(self) -> bool:
        """加载官署配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(官署表)")
        columns = [col[1] for col in cursor.fetchall()]
        cursor.execute("SELECT * FROM 官署表 WHERE 状态='正常' ORDER BY 级别, 名称")
        self.offices = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        print(f"加载官署: {{len(self.offices)}}个")
        return True
    
    def load_roles(self) -> bool:
        """加载官属角色"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(官属角色表)")
        columns = [col[1] for col in cursor.fetchall()]
        cursor.execute("SELECT * FROM 官属角色表 WHERE 状态='正常'")
        self.roles = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        print(f"加载官属: {{len(self.roles)}}人")
        return True
    
    def load_models(self) -> bool:
        """加载模型配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM 模型配置表 WHERE 状态='正常'")
        rows = cursor.fetchall()
        cursor.execute("PRAGMA table_info(模型配置表)")
        columns = [col[1] for col in cursor.fetchall()]
        self.models = [dict(zip(columns, row)) for row in rows]
        conn.close()
        print(f"加载模型: {{len(self.models)}}个")
        return True
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {{
            "rules": len(self.rules),
            "offices": len(self.offices),
            "roles": len(self.roles),
            "models": len(self.models)
        }}
'''
        self._write_file('kernel_loader.py', content)
    
    def _generate_config_manager(self):
        """生成配置管理器"""
        content = '''# -*- coding: utf-8 -*-
"""
配置管理器 - 管理内核配置
"""
import sqlite3
from typing import Dict, List, Optional

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_rules(self) -> List[Dict]:
        """获取所有规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM 内核规则表 WHERE 状态='启用'")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def update_rule(self, rule_id: str, content: str) -> bool:
        """更新规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE 内核规则表 SET 规则内容=? WHERE id=?", (content, rule_id))
        conn.commit()
        conn.close()
        return True
'''
        self._write_file('config_manager.py', content)
    
    def _generate_dispatch_manager(self):
        """生成调度管理器 - 多模态协作"""
        content = '''# -*- coding: utf-8 -*-
"""
调度管理器 - 多模态协作调度
基于官署/官属/模型进行智能调度
"""
import sqlite3
from typing import Dict, List, Optional

class DispatchManager:
    """调度管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_providers()
    
    def _init_providers(self):
        """初始化可用服务商"""
        self.providers = {
            '火山引擎': {'status': 'available', 'models': 9},
            '硅基流动': {'status': 'available', 'models': 9},
            '英伟达': {'status': 'available', 'models': 22},
            '魔搭': {'status': 'available', 'models': 10},
            '智谱': {'status': 'limited', 'models': 6},
            'OpenRouter': {'status': 'limited', 'models': 1},
            '魔力方舟': {'status': 'offline', 'models': 8},
        }
    
    def get_available_providers(self) -> List[str]:
        """获取可用服务商"""
        return [p for p, v in self.providers.items() if v['status'] == 'available']
    
    def dispatch(self, office_id: str, task_type: str = 'general') -> Optional[Dict]:
        """调度官属执行任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查找可用官属
        cursor.execute("""
            SELECT r.id, r.姓名, r.官职, r.模型名称, r.模型服务商
            FROM 官属角色表 r
            WHERE r.官署ID = ? AND r.状态 = '正常'
        """, (office_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'title': row[2],
                'model': row[3],
                'provider': row[4]
            }
        return None
    
    def get_stats(self) -> Dict:
        """获取调度统计"""
        return self.providers.copy()
'''
        self._write_file('dispatch_manager.py', content)
    
    def _write_file(self, filename: str, content: str):
        """写入文件"""
        filepath = os.path.join(self.kernel_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ {filename}")


def main():
    """主函数"""
    strategy = KernelStrategy()
    strategy.initialize()
    
    print("\n=== 内核统计 ===")
    print(f"规则: {len(strategy.data.get('rules', []))}条")
    print(f"官署: {len(strategy.data.get('offices', []))}个")
    print(f"官属: {len(strategy.data.get('roles', []))}人")
    print(f"模型: {len(strategy.data.get('models', []))}个")


if __name__ == "__main__":
    main()
