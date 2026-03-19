import sqlite3
db = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'
conn = sqlite3.connect(db)
c = conn.cursor()

print("=" * 70)
print("🔍 三大基础表梳理")
print("=" * 70)

# 1. 官署表
print("\n【1】官署表 (6个)")
print("-" * 50)
c.execute("SELECT id, 名称, 级别, 官品, 职责 FROM 官署表 ORDER BY 级别")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]} | 级别:{row[2]} | 官品:{row[3]} | {row[4] or ''}")

# 2. 官署角色表
print("\n【2】官署角色表")
print("-" * 50)
c.execute("SELECT COUNT(*), COUNT(模型配置表_ID), COUNT(所属官署) FROM 官署角色表")
row = c.fetchone()
print(f"  总角色: {row[0]}")
print(f"  已绑定模型: {row[1]}")
print(f"  已分配官署: {row[2]}")

# 按官署统计
print("\n  按官署分布:")
c.execute("""
    SELECT o.名称, COUNT(r.id) as 人数
    FROM 官署角色表 r
    JOIN 官署表 o ON r.所属官署 = o.id
    GROUP BY o.名称
    ORDER BY 人数 DESC
""")
for row in c.fetchall():
    print(f"    {row[0]}: {row[1]}人")

# 3. 模型配置表
print("\n【3】模型配置表")
print("-" * 50)
c.execute("SELECT COUNT(*), COUNT(API地址), COUNT(API密钥) FROM 模型配置表")
row = c.fetchone()
print(f"  总模型: {row[0]}")
print(f"  有API地址: {row[1]}")
print(f"  有API密钥: {row[2]}")

# 按服务商统计
print("\n  按服务商分布:")
c.execute("SELECT 服务商, COUNT(*) FROM 模型配置表 GROUP BY 服务商 ORDER BY COUNT(*) DESC")
for row in c.fetchall():
    print(f"    {row[0]}: {row[1]}个")

# 4. 三表关联关系
print("\n【4】三表关联关系")
print("-" * 50)
print("  官署表.id = 官署角色表.所属官署")
print("  模型配置表.id = 官署角色表.模型配置表_ID")

# 5. 验证关联完整性
print("\n【5】关联完整性验证")
print("-" * 50)

# 检查孤立角色
c.execute("""
    SELECT COUNT(*) FROM 官署角色表 
    WHERE 所属官署 IS NULL OR 模型配置表_ID IS NULL
""")
orphan = c.fetchone()[0]
print(f"  孤立角色(无绑定): {orphan}")

# 检查未使用的模型
c.execute("""
    SELECT COUNT(*) FROM 模型配置表 m
    WHERE m.id NOT IN (SELECT 模型配置表_ID FROM 官署角色表 WHERE 模型配置表_ID IS NOT NULL)
""")
unused = c.fetchone()[0]
print(f"  未使用模型: {unused}")

# 检查不存在的官署引用
c.execute("""
    SELECT COUNT(*) FROM 官署角色表 r
    WHERE r.所属官署 IS NOT NULL 
    AND r.所属官署 NOT IN (SELECT id FROM 官署表)
""")
invalid = c.fetchone()[0]
print(f"  无效官署引用: {invalid}")

# 6. 展示绑定样例
print("\n【6】绑定样例")
print("-" * 50)
c.execute("""
    SELECT r.姓名, r.官职, o.名称 as 官署, m.模型名称, m.服务商
    FROM 官署角色表 r
    JOIN 官署表 o ON r.所属官署 = o.id
    JOIN 模型配置表 m ON r.模型配置表_ID = m.id
    WHERE r.状态 = '正常'
    LIMIT 10
""")
for row in c.fetchall():
    print(f"  {row[0]}({row[1]}) → {row[2]} → {row[3]}({row[4]})")

print("\n" + "=" * 70)
print("✅ 三大基础表梳理完成 - 等待内核适配")
print("=" * 70)

conn.close()
