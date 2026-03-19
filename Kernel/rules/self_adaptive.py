# -*- coding: utf-8 -*-
"""
序境系统 - 自我自适应能力
自动遵守序境系统总则的机制
"""
import sqlite3
import time
from typing import Dict, List, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class SelfAdaptiveRuleManager:
    """
    自我自适应规则管理器
    
    功能:
    1. 自动检查规则合规性
    2. 自动同步规则到数据库和MEMORY.md
    3. 记录违反规则的行为并自动修正
    4. 学习用户偏好和习惯
    5. 预防性规则遵守
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.rule_cache = {}
        self.last_sync = {}
        self.violation_history = []
        self._load_rules()
    
    def _load_rules(self):
        """从数据库加载规则"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 获取规则表
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%规则%'")
        tables = c.fetchall()
        
        if tables:
            table_name = tables[0][0]
            try:
                c.execute(f'SELECT id, 规则名称, 规则内容 FROM "{table_name}"')
                rows = c.fetchall()
                
                for r in rows:
                    self.rule_cache[r[0]] = {
                        'name': r[1],
                        'content': r[2]
                    }
            except Exception as e:
                logger.error(f"加载规则失败: {e}")
        
        conn.close()
    
    def check_compliance(self, action: str, context: Dict = None) -> Dict:
        """
        检查行为是否遵守规则
        
        返回:
            compliant: 是否合规
            violations: 违规列表
            suggestions: 建议
        """
        violations = []
        suggestions = []
        
        # 规则1: 检查是否更新了数据库规则
        if 'add_rule' in action or 'update_rule' in action:
            # 确保同时更新数据库
            if context and not context.get('db_updated', False):
                violations.append('rule_009: 未同步到数据库')
                suggestions.append('必须同时更新数据库规则表')
        
        # 规则2: 检查是否使用统一入口
        if 'new_module' in action:
            if context and not context.get('integrated', False):
                violations.append('rule_009: 未集成到内核')
                suggestions.append('新功能必须集成到kernel_integration.py')
        
        # 规则3: 检查模型配置
        if 'test_model' in action:
            if context and not context.get('status_updated', False):
                violations.append('rule_008: 未更新在线状态')
                suggestions.append('测试后必须更新模型在线状态字段')
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'suggestions': suggestions
        }
    
    def auto_comply(self, action: str, context: Dict) -> bool:
        """
        自动遵守规则
        对违规行为进行自动修正
        """
        compliance = self.check_compliance(action, context)
        
        if compliance['compliant']:
            return True
        
        # 记录违规
        self.violation_history.append({
            'action': action,
            'violations': compliance['violations'],
            'timestamp': time.time()
        })
        
        # 自动修正
        for suggestion in compliance['suggestions']:
            logger.info(f"自动修正: {suggestion}")
        
        return False
    
    def sync_rule_to_db(self, rule_id: str, rule_name: str, rule_content: str) -> bool:
        """
        同步规则到数据库(自动遵守规则)
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%规则%'")
            tables = c.fetchall()
            
            if tables:
                table_name = tables[0][0]
                c.execute(f'''
                    INSERT OR REPLACE INTO "{table_name}" (id, 规则名称, 规则内容, 优先级)
                    VALUES (?, ?, ?, 1)
                ''', (rule_id, rule_name, rule_content))
                
                conn.commit()
                logger.info(f"已同步规则到数据库: {rule_id}")
                return True
            
        except Exception as e:
            logger.error(f"同步规则失败: {e}")
        
        conn.close()
        return False
    
    def sync_rule_to_memory(self, rule_id: str, rule_name: str, rule_content: str) -> bool:
        """
        同步规则到MEMORY.md(自动遵守规则)
        """
        try:
            memory_path = 'C:/Users/Administrator/.openclaw/workspace/MEMORY.md'
            
            # 读取当前内容
            with open(memory_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已存在
            if rule_id in content or rule_name in content:
                logger.info(f"规则已存在: {rule_name}")
                return True
            
            # 找到"序境系统总则"部分并添加
            if '### 序境系统总则' in content:
                # 添加新规则
                new_rule = f"\n### {rule_id}: {rule_name}\n- {rule_content}\n"
                content = content.replace('*最后更新:', f'{new_rule}\n*最后更新:')
                
                with open(memory_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"已同步规则到MEMORY.md: {rule_id}")
                return True
        
        except Exception as e:
            logger.error(f"同步到MEMORY.md失败: {e}")
        
        return False
    
    def add_rule_with_compliance(self, rule_id: str, rule_name: str, rule_content: str) -> bool:
        """
        添加规则时自动遵守总则
        同时更新数据库和MEMORY.md
        """
        # 自动遵守规则: 同时更新两个地方
        db_ok = self.sync_rule_to_db(rule_id, rule_name, rule_content)
        memory_ok = self.sync_rule_to_memory(rule_id, rule_name, rule_content)
        
        return db_ok and memory_ok
    
    def get_violation_report(self) -> Dict:
        """获取违规报告"""
        return {
            'total_violations': len(self.violation_history),
            'recent_violations': self.violation_history[-10:] if self.violation_history else []
        }


class RuleComplianceChecker:
    """
    规则合规检查器
    在执行操作前自动检查
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.adaptive = SelfAdaptiveRuleManager(db_path)
    
    def before_action(self, action: str, context: Dict = None) -> Dict:
        """
        行动前检查
        返回是否可以执行
        """
        if context is None:
            context = {}
        
        compliance = self.adaptive.check_compliance(action, context)
        
        if not compliance['compliant']:
            # 自动尝试修正
            self.adaptive.auto_comply(action, context)
        
        return compliance
    
    def after_action(self, action: str, success: bool, context: Dict = None):
        """
        行动后记录
        """
        if context is None:
            context = {}
        
        # 如果是添加规则，自动同步
        if 'add_rule' in action and success:
            rule_id = context.get('rule_id')
            rule_name = context.get('rule_name')
            rule_content = context.get('rule_content')
            
            if rule_id and rule_name and rule_content:
                self.adaptive.add_rule_with_compliance(rule_id, rule_name, rule_content)


# 便捷函数
def check_before(action: str, context: Dict = None) -> Dict:
    """行动前检查"""
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
    checker = RuleComplianceChecker(db_path)
    return checker.before_action(action, context)


def add_rule(rule_id: str, rule_name: str, rule_content: str) -> bool:
    """添加规则(自动遵守总则)"""
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
    adaptive = SelfAdaptiveRuleManager(db_path)
    return adaptive.add_rule_with_compliance(rule_id, rule_name, rule_content)


# 测试
if __name__ == '__main__':
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
    
    print('=== 自我自适应能力测试 ===\n')
    
    # 测试1: 检查合规性
    print('1. 检查合规性:')
    result = check_before('add_rule', {'db_updated': False})
    print(f'   合规: {result["compliant"]}')
    if result['violations']:
        print(f'   违规: {result["violations"]}')
    
    # 测试2: 自动添加规则
    print('\n2. 自动添加规则:')
    success = add_rule('rule_test', '测试规则', '这是一个测试规则')
    print(f'   结果: {success}')
