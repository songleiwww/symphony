import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

print("=" * 70)
print("🔧 修复重复绑定问题")
print("=" * 70)

# 找出重复绑定的角色
print("\n【查找重复绑定】")
print("-" * 50)

c.execute("""
    SELECT r.id, r.姓名, r.官职, r.模型配置表_ID, m.模型名称
    FROM 官署角色表 r
    JOIN 模型配置表 m ON r.模型配置表_ID = m.id
    WHERE r.模型配置表_ID IN (
        SELECT 模型配置表_ID 
        FROM 官署角色表 
        WHERE 模型配置表_ID IS NOT NULL
        GROUP BY 模型配置表_ID 
        HAVING COUNT(*) > 1
    )
    ORDER BY r.模型配置表_ID
""")

duplicates = c.fetchall()
print("重复绑定记录:")
for row in duplicates:
    print(f"  {row[0]}: {row[1]}({row[2]}) → 模型{row[3]}({row[4]})")

# 解决方案：为重复的角色分配其他可用模型
print("\n【修复方案】")
print("-" * 50)

# 获取可用的模型ID列表
c.execute("""
    SELECT id FROM 模型配置表 
    WHERE API地址 IS NOT NULL AND API密钥 IS NOT NULL
    AND id NOT IN (SELECT 模型配置表_ID FROM 官署角色表 WHERE 模型配置表_ID IS NOT NULL)
    ORDER BY id
""")

available_models = [row[0] for row in c.fetchall()]
print(f"可用模型数量: {len(available_models)}")

# 为重复角色重新分配
if duplicates and available_models:
    print("\n执行修复:")
    for i, row in enumerate(duplicates[1:], 1):  # 从第二个开始重新分配
        if i < len(available_models):
            new_model_id = available_models[i-1]
            c.execute("UPDATE 官署角色表 SET 模型配置表_ID = ? WHERE id = ?", (new_model_id, row[0]))
            print(f"  {row[0]}({row[1]}) → 模型{new_model_id}")
    
    conn.commit()
    print("\n✅ 修复完成")

# 验证修复结果
print("\n【验证修复结果】")
print("-" * 50)

c.execute("""
    SELECT 模型配置表_ID, COUNT(*) as 数量
    FROM 官署角色表
    WHERE 模型配置表_ID IS NOT NULL
    GROUP BY 模型配置表_ID
    HAVING COUNT(*) > 1
""")

still_dup = c.fetchall()
if still_dup:
    print("  ⚠️ 仍有重复:")
    for row in still_dup:
        print(f"    模型ID {row[0]}: {row[1]}个角色")
else:
    print("  ✅ 已无重复绑定")

conn.close()
