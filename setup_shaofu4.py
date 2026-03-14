# -*- coding: utf-8 -*-
"""
直接使用 kernel_loader 来配置少府监完整架构
"""
import sys
import os
import importlib.util
import time

# 设置项目路径
os.chdir(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

# 加载内核
spec = importlib.util.spec_from_file_location('kernel_loader', 'Kernel/kernel_loader.py')
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)

# 获取内核
kernel = kl.get_kernel()

# 唐代少府监完整架构
# 格式: id, 官名, 性别, 职位, 职能, 专长, 模型名称, 模型服务商, 角色等级
officials = [
    # 本部 (11人)
    ('shaofu_001', '少府监', '男', '监', '总领百工伎巧', '统筹管理', 'glm-4.7', '火山引擎', 1),
    ('shaofu_002', '少府少监', '男', '少监', '辅佐监务', '监督协调', 'glm-4.7', '火山引擎', 2),
    ('shaofu_003', '少府少监', '男', '少监', '辅佐监务', '监督协调', 'glm-4.7', '火山引擎', 2),
    ('shaofu_004', '少府丞', '男', '丞', '判监事之职', '事务管理', 'glm-4-flash', '智谱', 3),
    ('shaofu_005', '少府丞', '男', '丞', '判监事之职', '事务管理', 'glm-4-flash', '智谱', 3),
    ('shaofu_006', '少府丞', '男', '丞', '判监事之职', '事务管理', 'glm-4-flash', '智谱', 3),
    ('shaofu_007', '少府丞', '男', '丞', '判监事之职', '事务管理', 'glm-4-flash', '智谱', 3),
    ('shaofu_008', '少府主簿', '男', '主簿', '勾检稽失', '文书档案', 'glm-4-flash', '智谱', 4),
    ('shaofu_009', '少府主簿', '男', '主簿', '勾检稽失', '文书档案', 'glm-4-flash', '智谱', 4),
    ('shaofu_010', '少府录事', '男', '录事', '文书收发', '文书处理', 'glm-4-flash', '智谱', 5),
    ('shaofu_011', '少府录事', '男', '录事', '文书收发', '文书处理', 'glm-4-flash', '智谱', 5),
    
    # 五署 (10人)
    ('zhongshang_001', '中尚署令', '男', '令', '掌郊祀圭璧', '礼仪器物', 'Qwen2.5-14B', '硅基流动', 3),
    ('zhongshang_002', '中尚署丞', '男', '丞', '辅佐令职务', '工艺管理', 'glm-4-flash', '智谱', 4),
    ('zuoshang_001', '左尚署令', '男', '令', '掌天子五辂', '车辇制造', 'Qwen2.5-14B', '硅基流动', 3),
    ('zuoshang_002', '左尚署丞', '男', '丞', '辅佐令职务', '车辆管理', 'glm-4-flash', '智谱', 4),
    ('youshang_001', '右尚署令', '男', '令', '掌鞍辔兵器', '兵器制造', 'Qwen2.5-14B', '硅基流动', 3),
    ('youshang_002', '右尚署丞', '男', '丞', '辅佐令职务', '物料管理', 'glm-4-flash', '智谱', 4),
    ('zhiran_001', '织染署令', '男', '令', '掌纺织印染', '纺织印染', 'Qwen2.5-14B', '硅基流动', 3),
    ('zhiran_002', '织染署丞', '男', '丞', '辅佐令职务', '丝绸工艺', 'glm-4-flash', '智谱', 4),
    ('zhangye_001', '掌冶署令', '男', '令', '掌铜铁冶铸', '冶金铸造', 'Qwen2.5-14B', '硅基流动', 3),
    ('zhangye_002', '掌冶署丞', '男', '丞', '辅佐令职务', '金属工艺', 'glm-4-flash', '智谱', 4),
    
    # 附属 (3人)
    ('zhuye_001', '诸冶监', '男', '监', '掌金属冶炼', '冶金管理', 'glm-4-flash', '智谱', 3),
    ('zhuzhuqian_001', '诸铸钱监', '男', '监', '掌铸币事务', '货币铸造', 'glm-4-flash', '智谱', 3),
    ('hushi_001', '互市监', '男', '监', '掌边境贸易', '国际贸易', 'glm-4-flash', '智谱', 3),
]

print(f'准备添加: {len(officials)} 位官属')

# 使用 sqlite3 直接插入
import sqlite3
conn = sqlite3.connect(kernel.db_path)
cursor = conn.cursor()

now = time.strftime('%Y-%m-%d %H:%M:%S')

# 尝试使用位置插入
for o in officials:
    # 先检查是否存在
    cursor.execute('SELECT id FROM 官属角色表 WHERE id = ?', (o[0],))
    if cursor.fetchone():
        # 更新
        cursor.execute('''
            UPDATE 官属角色表 
            SET 官名=?, 性别=?, 职位=?, 职能=?, 专长=?, 模型名称=?, 模型服务商=?, 角色等级=?, 更新时间=?
            WHERE id=?
        ''', (o[1], o[2], o[3], o[4], o[5], o[6], o[7], o[8], now, o[0]))
    else:
        # 插入
        cursor.execute('''
            INSERT INTO 官属角色表 
            (id, 官名, 性别, 职位, 职能, 专长, 模型名称, 模型服务商, 角色等级, 状态, 创建时间, 更新时间)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*o, '正常', now, now))

conn.commit()

# 验证
cursor.execute('SELECT COUNT(*) FROM 官属角色表')
print(f'最终官属数量: {cursor.fetchone()[0]}')

# 按服务商统计
cursor.execute('SELECT 模型服务商, COUNT(*) as cnt FROM 官属角色表 GROUP BY 模型服务商')
print('\n按服务商:')
for r in cursor.fetchall():
    print(f'  {r[0]}: {r[1]}人')

conn.close()
print('\n少府监架构配置完成!')
