# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
from datetime import datetime

memory_path = 'C:/Users/Administrator/.openclaw/workspace/memory/'
today = datetime.now().strftime('%Y-%m-%d')
memory_file = memory_path + today + '.md'

# 学习内容
content = """

## 浏览器自动学习 02:41
*(使用浏览器访问AI资讯网站)*

### 36kr AI资讯
- 访问页面: 36氪AI报道
- 来源: https://www.36kr.com/information/aireport/
- 学习方式: 浏览器抓取

### 观察到的内容
- 36氪AI专栏：智能涌现
- 栏目分类：AI快讯、AI报道、自助报道
- 涵盖：AI公司动态、AI产品发布、AI融资新闻

### 下一步建议
1. 定期访问AI专业网站
2. 使用浏览器自动化抓取
3. 保存到记忆库
"""

# 追加到记忆文件
if os.path.exists(memory_file):
    with open(memory_file, 'r', encoding='utf-8') as f:
        existing = f.read()
    with open(memory_file, 'w', encoding='utf-8') as f:
        f.write(content)
else:
    with open(memory_file, 'w', encoding='utf-8') as f:
        f.write(f"# {today} 记忆\n")
        f.write(content)

print("✅ 浏览器学习记录已保存")
print(f"📁 {memory_file}")
