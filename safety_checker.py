# -*- coding: utf-8 -*-
"""
序境系统 - 安全检测模块（全面监管版）
内核内置，任何有风险的操作都会被监管
"""
import sqlite3
import re

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

RISK_HIGH = 'HIGH'
RISK_MEDIUM = 'MEDIUM'
RISK_LOW = 'LOW'
RISK_NONE = 'NONE'

# === 风险操作检测 ===

def check_delete(provider, model_id):
    """1. 模型删除检测"""
    if not provider or not model_id:
        return False, RISK_HIGH, '缺少关键字段'
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM 模型配置表 WHERE 服务商 = ?', (provider,))
    count = c.fetchone()[0]
    conn.close()
    
    if count <= 3:
        return False, RISK_HIGH, f'{provider}仅{count}个模型，禁止删除'
    return True, RISK_NONE, '检测通过'

def check_update(provider, old_url, new_url):
    """2. 配置变更检测"""
    if old_url and new_url and old_url != new_url:
        return True, RISK_MEDIUM, f'API地址变更'
    return True, RISK_NONE, '检测通过'

def check_insert(provider, model_id):
    """3. 新增模型检测"""
    if not provider or not model_id:
        return True, RISK_MEDIUM, '建议提供完整信息'
    
    # 检查重复
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM 模型配置表 WHERE 服务商 = ? AND 模型标识符 = ?', 
              (provider, model_id))
    exists = c.fetchone()[0] > 0
    conn.close()
    
    if exists:
        return False, RISK_HIGH, f'模型{provider}/{model_id}已存在'
    return True, RISK_NONE, '检测通过'

def check_exec(command):
    """4. 执行命令检测"""
    dangerous = ['rm -rf', 'del /', 'format', 'shutdown', 'reboot', 'kill -9']
    cmd_lower = command.lower()
    
    for d in dangerous:
        if d in cmd_lower:
            return False, RISK_HIGH, f'危险命令: {d}'
    
    # 检查sudo/admin
    if 'sudo' in cmd_lower or 'admin' in cmd_lower:
        return True, RISK_MEDIUM, '需要提权'
    
    return True, RISK_NONE, '检测通过'

def check_send(target, content):
    """5. 发送消息检测"""
    # 检查敏感词
    sensitive = ['密码', '密钥', 'token', 'api_key', 'secret']
    content_lower = content.lower()
    
    for s in sensitive:
        if s in content_lower:
            return True, RISK_MEDIUM, f'包含敏感词: {s}'
    
    # 检查外部链接
    if 'http' in content_lower and target != 'internal':
        return True, RISK_MEDIUM, '外部链接需确认'
    
    return True, RISK_NONE, '检测通过'

def check_file(path):
    """6. 文件操作检测"""
    # 路径穿越检测
    if '..' in path or path.startswith('/'):
        if '/etc/' in path or '/Windows/' in path or 'C:\\' in path:
            return False, RISK_HIGH, '系统路径，禁止访问'
    
    # 危险后缀
    dangerous_ext = ['.exe', '.dll', '.bat', '.sh', '.ps1']
    for ext in dangerous_ext:
        if path.endswith(ext):
            return True, RISK_MEDIUM, f'可执行文件: {ext}'
    
    return True, RISK_NONE, '检测通过'

def check_db(operation, count=None):
    """7. 数据库操作检测"""
    if operation == 'BATCH_DELETE' or operation == 'BATCH_UPDATE':
        if count and count > 10:
            return False, RISK_HIGH, f'批量操作超过10条: {count}'
        return True, RISK_MEDIUM, f'批量{operation}需确认'
    
    if operation == 'DROP' or operation == 'TRUNCATE':
        return False, RISK_HIGH, f'危险操作: {operation}'
    
    return True, RISK_NONE, '检测通过'

def check_api(endpoint):
    """8. 外部API检测"""
    sensitive = ['/billing', '/payment', '/admin', '/root']
    
    for s in sensitive:
        if s in endpoint:
            return True, RISK_MEDIUM, f'敏感API: {s}'
    
    return True, RISK_NONE, '检测通过'

# === 统一调度接口 ===

def intercept(op_type, params):
    """统一拦截器"""
    handlers = {
        'DELETE': lambda: check_delete(params.get('服务商'), params.get('模型标识符')),
        'UPDATE': lambda: check_update(params.get('服务商'), params.get('old_API地址'), params.get('new_API地址')),
        'INSERT': lambda: check_insert(params.get('服务商'), params.get('模型标识符')),
        'EXEC': lambda: check_exec(params.get('命令')),
        'SEND': lambda: check_send(params.get('target'), params.get('content')),
        'FILE': lambda: check_file(params.get('path')),
        'DB': lambda: check_db(params.get('operation'), params.get('count')),
        'API': lambda: check_api(params.get('endpoint')),
    }
    
    handler = handlers.get(op_type)
    if handler:
        return handler()
    
    return True, RISK_NONE, '未知操作类型'

# === 便捷函数 ===

def safe_delete(model_info):
    return intercept('DELETE', model_info)

def safe_update(model_info):
    return intercept('UPDATE', model_info)

def safe_insert(model_info):
    return intercept('INSERT', model_info)

def safe_exec(command_info):
    return intercept('EXEC', command_info)

def safe_send(send_info):
    return intercept('SEND', send_info)

def safe_file(file_info):
    return intercept('FILE', file_info)

def safe_db(db_info):
    return intercept('DB', db_info)

def safe_api(api_info):
    return intercept('API', api_info)
