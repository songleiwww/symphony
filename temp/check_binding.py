import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

print("=" * 70)
print("🔍 官署角色表 与 模型配置表 绑定检查")
print("=" * 70)

# 1. 检查所有角色的绑定情况
print("\n【1】绑定统计")
print("-" * 50)

c.execute("""
    SELECT 
        CASE 
            WHEN r.模型配置表_ID IS NULL THEN '未绑定'
            WHEN m.id IS NULL THEN '配置缺失'
            ELSE '正常'
        END as 状态,
        COUNT(*) as 数量
    FROM 官署角色表 r
    LEFT JOIN 模型配置表 m ON r.模型配置表_ID = m.id
    GROUP BY 状态
""")

for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}条")

# 2. 检查一一绑定（一个角色一个模型）
print("\n【2】一一绑定检查")
print("-" * 50)

# 检查是否有重复绑定
c.execute("""
    SELECT  模型配置表_ID, COUNT(*) as 数量
    FROM 官署角色表
    WHERE 模型配置表_ID IS NOT NULL
    GROUP BY 模型配置表_ID
    HAVING COUNT(*) > 1
""")

duplicates = c.fetchall()
if duplicates:
    print("  ⚠️ 发现重复绑定:")
    for row in duplicates:
        c.execute("SELECT 模型名称 FROM 模型配置表 WHERE id = ?", (row[0],))
        model = c.fetchone()[0]
        print(f"    模型ID {row[0]}({model}) 被 {row[1]}个角色共用")
else:
    print("  ✅ 每个模型只绑定一个角色")

# 检查反向重复（一个角色多个模型 - 不可能，但检查）
c.execute("""
    SELECT id, 姓名, 官职
    FROM 官署角色表
    WHERE 模型配置表_ID IS NOT NULL
    ORDER BY id
    LIMIT 10
""")

print("\n  前10个角色绑定:")
for row in c.fetchall():
    print(f"    {row[0]}: {row[1]}({row[2]})")

# 3. 有效人员列表（可接管的）
print("\n【3】有效人员列表（可接管）")
print("-" * 50)

c.execute("""
    SELECT r.id, r.姓名, r.官职, m.模型名称, m.服务商
    FROM 官署角色表 r
    JOIN 模型配置表 m ON r.模型配置表_ID = m.id
    WHERE m.API地址 IS NOT NULL AND m.API密钥 IS NOT NULL
    AND r.状态 = '正常'
    LIMIT 20
""")

valid_count = 0
for row in c.fetchall():
    valid_count += 1
    print(f"  ✅ {row[1]}({row[2]}) → {row[3]}({row[4]})")

print(f"\n  有效人员总数: {valid_count}")

conn.close()
