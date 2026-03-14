# -*- coding: utf-8 -*-
# Clean symphony.py
with open('symphony.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove any ``` markers
content = content.replace('```python', '')
content = content.replace('```', '')

# Strip whitespace
content = content.strip()

with open('symphony.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Cleaned symphony.py')
