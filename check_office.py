# -*- coding: utf-8 -*-
"""
检查官署 - 隶属部门
"""
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 官署(部门)映射
OFFICE_MAP = {
    # 本部
    'shaofu_001': {'官署': '少府监本部', '官名': '少府监'},
    'shaofu_002': {'官署': '少府监本部', '官名': '少府少监1'},
    'shaofu_003': {'官署': '少府监本部', '官名': '少府少监2'},
    'shaofu_004': {'官署': '少府监本部', '官名': '少府丞1'},
    'shaofu_005': {'官署': '少府监本部', '官名': '少府丞2'},
    'shaofu_006': {'官署': '少府监本部', '官名': '少府丞3'},
    'shaofu_007': {'官署': '少府监本部', '官名': '少府丞4'},
    'shaofu_008': {'官署': '少府监本部', '官名': '少府主簿1'},
    'shaofu_009': {'官署': '少府监本部', '官名': '少府主簿2'},
    'shaofu_010': {'官署': '少府监本部', '官名': '少府录事1'},
    'shaofu_011': {'官署': '少府监本部', '官名': '少府录事2'},
    
    # 五署
    'zhongshang_001': {'官署': '中尚署', '官名': '中尚署令'},
    'zhongshang_002': {'官署': '中尚署', '官名': '中尚署丞'},
    'zuoshang_001': {'官署': '左尚署', '官名': '左尚署令'},
    'zuoshang_002': {'官署': '左尚署', '官名': '左尚署丞'},
    'youshang_001': {'官署': '右尚署', '官名': '右尚署令'},
    'youshang_002': {'官署': '右尚署', '官名': '右尚署丞'},
    'zhiran_001': {'官署': '织染署', '官名': '织染署令'},
    'zhiran_002': {'官署': '织染署', '官名': '织染署丞'},
    'zhangye_001': {'官署': '掌冶署', '官名': '掌冶署令'},
    'zhangye_002': {'官署': '掌冶署', '官名': '掌冶署丞'},
    
    # 附属
    'zhuye_001': {'官署': '诸冶监', '官名': '诸冶监'},
    'zhuzhuqian_001': {'官署': '诸铸钱监', '官名': '诸铸钱监'},
    'hushi_001': {'官署': '互市监', '官名': '互市监'},
    
    # 核心团队
    'evolve_001': {'官署': '枢密院', '官名': '沈清弦'},
    'evolve_002': {'官署': '少府监', '官名': '陆念昭'},
    'evolve_003': {'官署': '工部', '官名': '苏云渺'},
    'evolve_004': {'官署': '翰林院', '官名': '顾清歌'},
    'evolve_005': {'官署': '中书省', '官名': '顾至尊'},
    'evolve_006': {'官署': '枢密院', '官名': '沈星衍'},
    'evolve_007': {'官署': '门下省', '官名': '叶轻尘'},
    'evolve_008': {'官署': '工部', '官名': '林码'},
}

print("=" * 60)
print("少府监官署(隶属部门)一览表")
print("=" * 60)
print()

# 按官署分组
offices = {}
for oid, info in OFFICE_MAP.items():
    office = info['官署']
    if office not in offices:
        offices[office] = []
    offices[office].append(f"{info['官名']}")

for office, members in offices.items():
    print(f"【{office}】")
    for m in members:
        print(f"  · {m}")
    print()

print("=" * 60)
conn.close()
