# -*- coding: utf-8 -*-
"""
自动生成少府监官属 - 每个模型对应一个官属
基于 symphony.db 的模型配置自动生成官属
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'

# 官职模板
OFFICE_TEMPLATES = {
    '通用模型': [
        '中书侍郎', '门下侍郎', '尚书左丞', '尚书右丞',
        '吏部郎中', '户部郎中', '礼部郎中', '兵部郎中',
        '刑部郎中', '工部郎中', '大理寺丞', '太常寺丞',
    ],
    '推理模型': [
        '枢密院编修', '军师参议', '智囊博士', '策略博士',
        '推官', '判官', '议郎', '谏议大夫',
    ],
    '代码模型': [
        '营造司正', '工部司务', '司天监正', '军器监丞',
        '将作监丞', '文思院使', '绫锦院使', '染坊使',
    ],
    '视觉模型': [
        '图画待诏', '丹青博士', '待诏', '画院学士',
    ],
    '视频模型': [
        '影视博士', '乐府令', '大乐令',
    ],
    '图像模型': [
        '图画待诏', '图像博士',
    ],
    'Agent模型': [
        '首辅大学士', '少府监', '枢密使',
    ],
    '多语言模型': [
        '通事舍人', '翻译博士', '外语博士',
    ],
}

# 服务商对应的署
PROVIDER_OFFICE = {
    '火山引擎': '中书省',
    '智谱': '翰林院',
    '魔搭': '工部',
    '硅基流动': '枢密院',
    '英伟达': '军器监',
    '魔力方舟': '少府监',
    'OpenRouter': '礼部',
}

def get_office_name(provider, model_type):
    """获取官署名"""
    office = PROVIDER_OFFICE.get(provider, '未央宫')
    return office

def get_title(model_type, index):
    """获取官职"""
    templates = OFFICE_TEMPLATES.get(model_type, OFFICE_TEMPLATES['通用模型'])
    return templates[index % len(templates)]

def generate_officials():
    """自动生成官属"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有模型
    cursor.execute("""
        SELECT id, 模型名称, 服务商, 模型类型, url, key, 限制说明, 是否在线
        FROM 模型配置表 
        WHERE 状态='正常'
        ORDER BY id
    """)
    models = cursor.fetchall()
    
    print(f"=== 准备生成 {len(models)} 位官属 ===\n")
    
    # 获取现有官属数量
    cursor.execute("SELECT COUNT(*) FROM 官属角色表")
    existing_count = cursor.fetchone()[0]
    print(f"现有官属: {existing_count} 人\n")
    
    # 按服务商分组
    providers = {}
    for m in models:
        provider = m[2]
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(m)
    
    # 生成官属
    new_officials = []
    model_index = 0
    
    for provider, provider_models in providers.items():
        office = PROVIDER_OFFICE.get(provider, '未央宫')
        
        for m in provider_models:
            model_id = m[0]
            model_name = m[1]
            model_type = m[3]
            
            # 生成官属ID
            role_id = f"model_{model_id:03d}"
            
            # 分配官职
            title = get_title(model_type, model_index)
            
            # 生成姓名 (使用历史人物)
            names = ['李太白', '杜子美', '王摩诘', '孟浩然', '高常侍', 
                    '岑嘉州', '王昌龄', '贾浪仙', '刘禹锡', '元微之',
                    '白乐天', '柳子厚', '韩昌黎', '李义山', '温飞卿',
                    '杜牧之', '李商隐', '王次回', '纳兰性德', '曹雪芹']
            
            name = names[model_index % len(names)]
            
            official = {
                'id': role_id,
                '姓名': name,
                '性别': '男',
                '官职': title,
                '职务': f'负责{office}{model_type}任务',
                '描述': f'{provider}{model_name}模型绑定官属',
                '模型名称': model_name,
                '模型服务商': provider,
                '角色等级': 2,
                '状态': '正常',
                '创建时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '更新时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            new_officials.append(official)
            model_index += 1
    
    # 插入新官属
    print("=== 生成的官属 ===")
    for i, off in enumerate(new_officials[:10], 1):
        print(f"{i}. {off['姓名']} | {off['官职']} | {off['模型名称']} | {off['模型服务商']}")
    print(f"... 共 {len(new_officials)} 人")
    
    # 插入数据库
    cursor.execute("DELETE FROM 官属角色表 WHERE id LIKE 'model_%'")
    
    for off in new_officials:
        cursor.execute("""
            INSERT INTO 官属角色表 (
                id, 姓名, 性别, 官职, 职务, 描述,
                模型名称, 模型服务商, 角色等级, 状态, 创建时间, 更新时间
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            off['id'], off['姓名'], off['性别'], off['官职'], off['职务'], off['描述'],
            off['模型名称'], off['模型服务商'], off['角色等级'], off['状态'],
            off['创建时间'], off['更新时间']
        ))
    
    conn.commit()
    
    # 验证
    cursor.execute("SELECT COUNT(*) FROM 官属角色表")
    new_count = cursor.fetchone()[0]
    
    print(f"\n✅ 更新完成!")
    print(f"   现有官属: {existing_count} 人")
    print(f"   新增官属: {len(new_officials)} 人")
    print(f"   总计: {new_count} 人")
    
    conn.close()


if __name__ == "__main__":
    generate_officials()
