#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化脚本 - 迁移原JSON花名册数据到数据库
"""
import json
import os
from permission_manager import get_permission_manager

def migrate_roster_to_db():
    """将原JSON花名册数据迁移到数据库"""
    perm_manager = get_permission_manager()
    
    # 原JSON文件路径
    old_roster_path = os.path.join(os.path.dirname(__file__), "sf_team_roster.json")
    
    if not os.path.exists(old_roster_path):
        print("未找到原JSON花名册文件，跳过迁移")
        return False
    
    # 读取原数据
    with open(old_roster_path, 'r', encoding='utf-8') as f:
        old_roster = json.load(f)
    
    print(f"读取到原花名册共 {len(old_roster)} 位官属")
    
    # 初始化基础权限
    base_permissions = [
        ("model_call", "模型调用", "允许调用AI模型"),
        ("task_exec", "任务执行", "允许执行分配的任务"),
        ("log_view", "日志查看", "允许查看操作日志"),
        ("config_view", "配置查看", "允许查看系统配置"),
        ("config_edit", "配置修改", "允许修改系统配置"),
        ("role_manage", "角色管理", "允许管理官属角色"),
        ("system_update", "系统更新", "允许执行系统更新")
    ]
    
    for perm_id, perm_name, perm_desc in base_permissions:
        perm_manager.add_permission(perm_id, perm_name, perm_desc)
    
    print("✅ 基础权限初始化完成")
    
    # 迁移角色数据
    success_count = 0
    for member in old_roster:
        role_data = {
            "id": member.get("id"),
            "姓名": member.get("姓名"),
            "性别": member.get("性别", "男"),
            "官职": member.get("官职"),
            "职务": member.get("职务"),
            "描述": member.get("描述"),
            "模型名称": member.get("模型"),
            "模型服务商": member.get("模型服务商"),
            "角色等级": member.get("等级", 1),
            "状态": "正常"
        }
        
        if perm_manager.add_role(role_data):
            success_count += 1
            
            # 授予基础权限
            perm_manager.grant_permission(role_data["id"], "model_call")
            perm_manager.grant_permission(role_data["id"], "task_exec")
            perm_manager.grant_permission(role_data["id"], "log_view")
            perm_manager.grant_permission(role_data["id"], "config_view")
            
            # 高级权限授予管理员
            if role_data["官职"] in ["少府监", "枢密使", "刑部尚书"]:
                perm_manager.grant_permission(role_data["id"], "config_edit")
                perm_manager.grant_permission(role_data["id"], "role_manage")
                perm_manager.grant_permission(role_data["id"], "system_update")
    
    print(f"✅ 成功迁移 {success_count} 位官署角色到数据库")
    
    # 验证迁移结果
    conn = perm_manager.db_path
    import sqlite3
    conn = sqlite3.connect(conn)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM 官署角色表")
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f"✅ 数据库中共有 {count} 位官署角色")
    
    return True

if __name__ == "__main__":
    print("开始迁移花名册数据到数据库...")
    if migrate_roster_to_db():
        print("\n🎉 迁移完成！内核已去除JSON文件依赖，所有配置已存储到数据库")
    else:
        print("\n❌ 迁移失败")
