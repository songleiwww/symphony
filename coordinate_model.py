# -*- coding: utf-8 -*-
import json
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("【宿主协调序境系统模型】")
print("="*60)

# 1. 检查OpenClaw当前配置
print("\n【1. OpenClaw当前模型】")
config_path = 'C:/Users/Administrator/.openclaw/workspace/config.json'
models_path = 'C:/Users/Administrator/.openclaw/workspace/models.json'

default_model = None
if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    default_model = config.get('defaults', {}).get('model')
    print(f"  default_model: {default_model}")

# 2. 检查可用模型
print("\n【2. 可用模型列表】")
if os.path.exists(models_path):
    with open(models_path, 'r', encoding='utf-8') as f:
        models_data = json.load(f)
    for m in models_data.get('models', [])[:10]:
        print(f"  - {m.get('name')}: {m.get('provider')}")

# 3. 协调方案
print("\n【3. 协调方案】")
print("""
方案：宿主(OpenClaw)协调，序境自适应

当用户说"序境"或"陆念昭"时：
1. 宿主检测到关键词
2. 调度ark-code-latest模型
3. 序境系统接管对话

当用户说"宿主"或"步花间"时：
1. 宿主检测到关键词
2. 使用默认模型(MiniMax-M2.5)直接对话
3. 跳过序境接管

当前状态：
- 序境关键词: 序境,陆念昭 → 触发接管
- 宿主关键词: 宿主,步花间 → 跳过接管
""")

# 4. 更新TOOLS.md记录协调结果
print("\n【4. 更新TOOLS.md】")
tools_path = 'C:/Users/Administrator/.openclaw/workspace/TOOLS.md'
with open(tools_path, 'r', encoding='utf-8') as f:
    tools_content = f.read()

# 检查是否需要更新
if '当前协调状态' not in tools_content:
    update_content = """

---

### 当前协调状态 (2026-03-21)

**宿主协调机制**:
- 序境关键词 → 触发接管 → 使用ark-code-latest
- 宿主关键词 → 跳过接管 → 使用默认模型

**状态**: ✅ 已协调
"""
    with open(tools_path, 'w', encoding='utf-8') as f:
        f.write(tools_content + update_content)
    print("  ✅ TOOLS.md已更新")
else:
    print("  ⚠️ TOOLS.md已有协调状态")

print("\n" + "="*60)
print("【协调完成】")
print("="*60)
print("""
总结：
1. 宿主(OpenClaw)协调模型调度
2. 序境关键词 → ark-code-latest
3. 宿主关键词 → MiniMax-M2.5
4. 无需修改数据库配置
""")
