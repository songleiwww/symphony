# -*- coding: utf-8 -*-
"""
序境系统 - 数据库误操作恢复指南
"""
import sqlite3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
backup_dir = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/'

print("="*60)
print("【误操作挽救指南】")
print("="*60)

# 检查历史备份表
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查旧表备份
old_tables = [t for t in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_old%'").fetchall()]
print(f"\n📦 历史备份表: {len(old_tables)}个")
for t in old_tables:
    c.execute(f"SELECT COUNT(*) FROM {t[0]}")
    print(f"  - {t[0]}: {c.fetchone()[0]}条")

conn.close()

print("\n" + "="*60)
print("【误操作场景与挽救方法】")
print("="*60)

print("""
🔴 场景1: 批量删除数据
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 错误操作:
  DELETE FROM 模型配置表 WHERE 服务商='英伟达'
  (一下删除48条)

✅ 挽救方法1: 从备份表恢复
  # 检查是否有备份表
  SELECT * FROM _模型配置表_old_20260320
  
  # 从备份表恢复
  INSERT INTO 模型配置表 SELECT * FROM _模型配置表_old_20260320

✅ 挽救方法2: 从备份文件恢复
  # 复制备份文件覆盖
  copy symphony_backup.db symphony.db

✅ 挽救方法3: 导出SQL再导入
  # 导出备份
  sqlite3 symphony.db ".dump" > backup.sql
  
  # 查找删除操作前的版本
  # 从备份恢复数据后导入


🔴 场景2: 误更新数据
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 错误操作:
  UPDATE 模型配置表 SET 在线状态='offline'
  (忘记加WHERE，全部变offline)

✅ 挽救方法:
  # 如果有备份表
  UPDATE 模型配置表 
  SET 在线状态=(SELECT 在线状态 FROM _模型配置表_old_20260320 
                WHERE 模型配置表.id = _模型配置表_old_20260320.id)


🔴 场景3: 误删单条
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 错误操作:
  DELETE FROM 模型配置表 WHERE id=100
  (误删1条)

✅ 挽救方法:
  # 从备份表找回
  SELECT * FROM _模型配置表_old_20260320 WHERE id=100
  
  # 重新插入
  INSERT INTO 模型配置表 VALUES (...)


🔴 场景4: 修改表结构
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 错误操作:
  ALTER TABLE 模型配置表 DROP COLUMN 备注

✅ 挽救方法:
  # SQLite不支持DROP COLUMN
  # 只能从备份恢复整个表
""")

print("\n" + "="*60)
print("【预防措施】")
print("="*60)

print("""
✅ 批量操作前先备份
  BEGIN TRANSACTION;
  -- 先测试SELECT确认
  SELECT * FROM 表 WHERE 条件;
  -- 确认无误再DELETE/UPDATE
  COMMIT;

✅ 使用事务
  BEGIN;
  -- 你的操作
  ROLLBACK;  -- 发现错误可回滚
  COMMIT;    -- 确认无误再提交

✅ 先用SELECT测试
  -- 不要直接DELETE，先看影响多少条
  SELECT COUNT(*) FROM 表 WHERE 条件

✅ 限制影响行数
  DELETE FROM 表 WHERE 条件 LIMIT 100
""")

print("\n" + "="*60)
print("【紧急恢复】")
print("="*60)

print("""
🚨 如果刚犯错误，立即:
1. 停止所有写入操作
2. 不要关闭程序（保留journal）
3. 检查备份表
4. 从备份文件恢复

命令:
  # 查看可用的备份表
  SELECT name FROM sqlite_master WHERE name LIKE '%_old%'
  
  # 查看备份数据
  SELECT COUNT(*) FROM _模型配置表_old_20260320
""")
