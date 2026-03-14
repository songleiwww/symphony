# -*- coding: utf-8 -*-
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
