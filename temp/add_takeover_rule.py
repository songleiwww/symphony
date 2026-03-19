import sqlite3
from datetime import datetime
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# 添加接管模式规则
rule_content = """【用户切换接管模式】
1. 用户发送"接管"或"由序境调度"即可切换到序境接管模式
2. 接管后用户消息通过序境Skill处理
3. 序境从官署角色表读取绑定模型，调用真实API返回结果

【回报处理规则】
1. 每次API调用结果必须返回给用户
2. 如调用失败，尝试备用人员（故障转移）
3. 备用也失败时，返回错误原因

【接管失败调整】
1. 检测API返回401/403: 报告密钥问题，请用户检查配置
2. 检测API返回404: 模型不存在，报告并跳过
3. 检测API返回500+: 服务商问题，自动切换备用
4. 连续3次失败: 标记当前模型熔断，切到备用

【故障转移流程】
主角色失败 -> 依次尝试备用角色 -> 都失败返回错误"""

c.execute('''
    INSERT INTO 内核规则表 (id, 规则名称, 规则内容, 优先级, 状态, 创建时间, 更新时间)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('rule_004', '接管模式规则', rule_content, 1, '启用', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

conn.commit()
print('OK - 规则已添加')

# 验证
c.execute('SELECT id, 规则名称, 状态 FROM 内核规则表')
print('\n=== 内核规则表 ===')
for row in c.fetchall():
    print(f'  {row[0]}: {row[1]} - {row[2]}')

conn.close()
