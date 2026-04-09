# -*- coding: utf-8 -*-
import sqlite3, re, os

# Check which db the kernel actually uses
kernel_file = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\Kernel\evolution_kernel.py'
with open(kernel_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find db path references
db_refs = re.findall(r'symphony[_a-z]*\.db|data[\\/][^"\']+\.db', content)
print('DB references in evolution_kernel.py:')
for r in set(db_refs):
    print(f'  {r}')

# Also check which tables/fields the kernel queries
model_queries = re.findall(r'SELECT.*FROM.*model[_\w]*', content, re.IGNORECASE)
print('\nModel queries in kernel:')
for q in set(model_queries):
    print(f'  {q}')

