# -*- coding: utf-8 -*-
# 修复xuyuan_responder.py
with open('xuyuan_responder.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 移除尾部 ```
content = content.rstrip().rstrip('```').rstrip()

with open('xuyuan_responder.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed!')
