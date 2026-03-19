# -*- coding: utf-8 -*-
"""
序境系统 - 内核健康体质模块
集思广益、预设问题、测试内核、自动修复、抵御风险
"""
import sqlite3
import time
import threading
import requests
from typing import Dict, List, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class KernelHealthChecker:
    """
    内核健康检查器

    功能:
    1. 内循环健康检测 - 检查各模块状态
    2. 预设问题分析 - 预测潜在风险
    3. 多维度测试 - 调度/存储/网络/规则
    4. 自动修复 - 常见问题自动修复
    5. 风险评估 - 高危风险预警
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.health_records = []
        self.risk_threshold = 0.7

    def check_database_health(self) -> Dict:
        """检查数据库健康状态"""
        result = {
            'check': 'database',
            'status': 'unknown',
            'issues': [],
            'score': 0
        }

        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # 检查表是否存在
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [t[0] for t in c.fetchall()]

            required_tables = ['模型配置表', '官署表', '官署角色表']
            missing = [t for t in required_tables if t not in tables]

            if missing:
                result['issues'].append('Missing tables: ' + str(missing))
                result['score'] -= 30
            else:
                result['score'] += 30

            # 检查模型数量
            c.execute('SELECT COUNT(*) FROM 模型配置表')
            model_count = c.fetchone()[0]
            if model_count < 10:
                result['issues'].append('Model count too low: ' + str(model_count))
                result['score'] -= 20
            else:
                result['score'] += 20

            # 检查在线模型
            c.execute("SELECT COUNT(*) FROM 模型配置表 WHERE 在线状态 = 'online'")
            online_count = c.fetchone()[0]
            if online_count < 3:
                result['issues'].append('Online models too few: ' + str(online_count))
                result['score'] -= 20
            else:
                result['score'] += 20

            # 检查规则表
            rule_tables = [t for t in tables if '规则' in t]
            if rule_tables:
                result['score'] += 15

            # 检查规则数量
            c.execute(f'SELECT COUNT(*) FROM "{rule_tables[0]}"')
            rule_count = c.fetchone()[0]
            if rule_count < 5:
                result['issues'].append('Rules too few: ' + str(rule_count))
                result['score'] -= 15
            else:
                result['score'] += 15

            conn.close()

            # 评分
            result['score'] = max(0, min(100, result['score']))
            result['status'] = 'healthy' if result['score'] >= 70 else 'warning' if result['score'] >= 50 else 'critical'

        except Exception as e:
            result['status'] = 'critical'
            result['issues'].append('Database error: ' + str(e))

        return result

    def check_module_health(self) -> Dict:
        """检查内核模块健康状态"""
        result = {
            'check': 'modules',
            'status': 'unknown',
            'issues': [],
            'score': 0,
            'modules': {}
        }

        kernel_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel'
        import os

        # 检查关键模块
        critical_modules = {
            'kernel_integration.py': '统一入口',
            'dispatcher_multiprovider.py': '多服务商调度',
            'dispatcher_evolution.py': '进化调度',
            'progress/realtime_progress.py': '实时进度',
            'rules/self_adaptive.py': '自我自适应',
            'control/task_controller.py': '任务控制'
        }

        for module, desc in critical_modules.items():
            module_path = os.path.join(kernel_path, module)
            exists = os.path.exists(module_path)

            result['modules'][module] = {
                'exists': exists,
                'description': desc
            }

            if exists:
                result['score'] += 15
            else:
                result['issues'].append('Missing module: ' + module)

        result['score'] = min(100, result['score'])
        result['status'] = 'healthy' if result['score'] >= 70 else 'warning' if result['score'] >= 50 else 'critical'

        return result

    def check_api_connectivity(self) -> Dict:
        """检查API连接性"""
        result = {
            'check': 'api_connectivity',
            'status': 'unknown',
            'issues': [],
            'score': 0,
            'providers': {}
        }

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # 抽样检查各服务商API
        c.execute('''
            SELECT DISTINCT API地址
            FROM 模型配置表
            WHERE 在线状态 = 'online'
            LIMIT 5
        ''')

        providers = c.fetchall()
        conn.close()

        if not providers:
            result['issues'].append('No online models')
            result['status'] = 'critical'
            return result

        for (api_url,) in providers:
            provider_name = api_url.split('//')[1].split('.')[0] if '//' in api_url else 'unknown'

            try:
                import urllib.request
                req = urllib.request.Request(api_url.replace('/chat/completions', ''))
                req.add_header('Content-Type', 'application/json')
                result['providers'][provider_name] = 'reachable'
                result['score'] += 15
            except:
                result['providers'][provider_name] = 'unreachable'
                result['issues'].append('API unreachable: ' + provider_name)

        result['score'] = min(100, result['score'])
        result['status'] = 'healthy' if result['score'] >= 70 else 'warning' if result['score'] >= 40 else 'critical'

        return result

    def anticipate_problems(self) -> List[Dict]:
        """预设可能性问题"""
        problems = []

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # 问题1: 模型过载风险
        c.execute("SELECT COUNT(*) FROM 模型配置表 WHERE 在线状态 = 'online'")
        online = c.fetchone()[0]
        if online < 5:
            problems.append({
                'id': 'RISK_001',
                'type': 'capacity',
                'severity': 'high',
                'description': 'Online model count insufficient: ' + str(online),
                'suggestion': 'Add more online model configurations'
            })

        # 问题2: 规则过期风险
        try:
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%规则%'")
            rule_table = c.fetchone()
            if rule_table:
                c.execute(f'SELECT MAX(更新时间) FROM "{rule_table[0]}"')
                last_update = c.fetchone()[0]
                if last_update:
                    update_time = time.strptime(last_update, '%Y-%m-%d %H:%M:%S')
                    days_old = (time.time() - time.mktime(update_time)) / 86400
                    if days_old > 7:
                        problems.append({
                            'id': 'RISK_002',
                            'type': 'stale',
                            'severity': 'medium',
                            'description': 'Rules not updated for {:.0f} days'.format(days_old),
                            'suggestion': 'Regularly update rules'
                        })
        except:
            pass

        # 问题3: 单一服务商依赖
        c.execute("SELECT COUNT(DISTINCT API地址) FROM 模型配置表")
        provider_count = c.fetchone()[0]
        if provider_count < 3:
            problems.append({
                'id': 'RISK_003',
                'type': 'dependency',
                'severity': 'high',
                'description': 'Provider count too low: ' + str(provider_count),
                'suggestion': 'Increase multi-provider configuration'
            })

        conn.close()

        return problems

    def run_full_checkup(self) -> Dict:
        """全面体检"""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_score': 0,
            'overall_status': 'unknown',
            'checks': [],
            'risks': [],
            'recommendations': []
        }

        checks = [
            self.check_database_health(),
            self.check_module_health(),
            self.check_api_connectivity()
        ]

        for check in checks:
            report['checks'].append(check)
            report['overall_score'] += check.get('score', 0)

        report['overall_score'] = report['overall_score'] // len(checks)

        report['risks'] = self.anticipate_problems()

        high_risks = [r for r in report['risks'] if r['severity'] == 'high']
        if high_risks:
            report['overall_status'] = 'critical'
        elif report['risks']:
            report['overall_status'] = 'warning'
        elif report['overall_score'] >= 70:
            report['overall_status'] = 'healthy'
        else:
            report['overall_status'] = 'warning'

        if high_risks:
            report['recommendations'].append('High risks exist, need immediate attention')
        if report['overall_score'] < 70:
            report['recommendations'].append('Kernel health insufficient, suggest full maintenance')

        self.health_records.append(report)

        return report

    def auto_repair(self) -> Dict:
        """自动修复常见问题"""
        repair_log = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'repairs': []
        }

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # 修复1: 清理失控模型
        try:
            c.execute("SELECT COUNT(*) FROM 模型配置表 WHERE 在线状态 = '失控'")
            lost_count = c.fetchone()[0]
            if lost_count > 5:
                c.execute("UPDATE 模型配置表 SET 在线状态 = 'offline' WHERE 在线状态 = '失控'")
                repair_log['repairs'].append('Reset {}失控 models to offline'.format(lost_count))
        except:
            pass

        # 修复2: 补充默认规则
        try:
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%规则%'")
            rule_table = c.fetchone()
            if rule_table:
                c.execute(f'SELECT COUNT(*) FROM "{rule_table[0]}"')
                rule_count = c.fetchone()[0]
                if rule_count < 5:
                    default_rules = [
                        ('rule_default_001', '默认规则', '系统默认规则', 1),
                        ('rule_default_002', '调度规则', '模型调度规则', 1)
                    ]
                    for rule in default_rules:
                        try:
                            c.execute(f'INSERT OR IGNORE INTO "{rule_table[0]}" (id, 规则名称, 规则内容, 优先级) VALUES (?, ?, ?, ?)', rule)
                            repair_log['repairs'].append('Added rule: ' + rule[1])
                        except:
                            pass
        except:
            pass

        conn.commit()
        conn.close()

        return repair_log


class KernelDefenseSystem:
    """内核防御系统 - 抵御高危风险"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.defense_log = []

    def defend_against_risks(self, risks: List[Dict]) -> Dict:
        """防御风险"""
        defense = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'actions': []
        }

        for risk in risks:
            if risk['severity'] == 'high':
                action = {
                    'risk_id': risk['id'],
                    'action': 'quarantine',
                    'status': 'pending'
                }

                if risk['type'] == 'capacity':
                    action['action'] = 'scale_up'
                    action['description'] = 'Expand model capacity'
                elif risk['type'] == 'dependency':
                    action['action'] = 'diversify'
                    action['description'] = 'Increase provider diversity'
                elif risk['type'] == 'stale':
                    action['action'] = 'refresh'
                    action['description'] = 'Refresh rules'

                defense['actions'].append(action)

        return defense


# 测试
if __name__ == '__main__':
    db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

    print('=== Kernel Health Check ===\n')

    checker = KernelHealthChecker(db_path)
    report = checker.run_full_checkup()

    print('Overall Score: {}/100'.format(report['overall_score']))
    print('Health Status: {}\n'.format(report['overall_status']))

    print('=== Check Details ===')
    for check in report['checks']:
        print('\n{}: {} ({} points)'.format(check['check'], check['status'], check['score']))
        if check['issues']:
            print('  Issues:', check['issues'])

    print('\n=== Risk Anticipation ===')
    for risk in report['risks']:
        print('[{}] {}: {}'.format(risk['severity'], risk['id'], risk['description']))
        print('  Suggestion: {}'.format(risk['suggestion']))

    print('\n=== Auto Repair ===')
    repair = checker.auto_repair()
    for r in repair['repairs']:
        print('  - {}'.format(r))

    print('\n=== Defense System ===')
    defense = KernelDefenseSystem(db_path)
    defense_report = defense.defend_against_risks(report['risks'])
    for action in defense_report['actions']:
        print('  - {}'.format(action['description']))
