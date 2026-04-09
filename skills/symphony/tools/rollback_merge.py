# -*- coding: utf-8 -*-
"""
回滚合并，恢复到合并前的状?"""
import shutil, os
from datetime import datetime

BACKUP_DIR = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\backup'
NEW_DB = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony_working.db'

# 找到合并前的备份
backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith('symphony_working_pre_merge')]
backups.sort(reverse=True)
print('找到合并前备?')
for b in backups:
    print(f'  {b}')

# 恢复最近的备份
if backups:
    src = os.path.join(BACKUP_DIR, backups[0])
    shutil.copy2(src, NEW_DB)
    print(f'\n已回滚到: {backups[0]}')

