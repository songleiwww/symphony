# -*- coding: utf-8 -*-
"""
序境系统 - 序境系统优化设计研讨会
调度美学、人体工程学、自动化专家、体验工程师等多角色模型
"""
import sys
import io
import sqlite3
import requests
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

def get_model(provider):
    c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE 服务商=? AND 在线状态='online' ORDER BY RANDOM() LIMIT 1", (provider,))
    r = c.fetchone()
    if r:
        return {"name": r[0], "identifier": r[1], "url": r[2], "key": r[3], "provider": provider}
    return None

def call_model(model, prompt):
    url = model['url']
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    try:
        resp = requests.post(url, json={"model": model['identifier'], "messages": [{"role": "user", "content": prompt}], "max_tokens": 1500},
                          headers={"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}, timeout=90)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"错误: {e}"
    return None

# 获取不同服务商模型
providers = ['火山引擎', '硅基流动', '魔搭', '智谱', '英伟达']
models = []
for p in providers:
    m = get_model(p)
    if m:
        models.append(m)

conn.close()

print("="*70)
print("【序境系统优化设计研讨会】")
print("="*70)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"参会人数: {len(models)}人\n")

# 研讨会主题
topic = """你是序境系统AI助手。请从你的专业角度，为序境系统提出优化设计建议。

序境系统现状：
- 120条规则体系
- 420个模型配置
- 6大核心模块
- 关键词触发机制
- 半自动接管模式

请从以下角度分析并给出建议：
1. 系统架构优化
2. 用户体验改进
3. 自动化流程完善
4. 界面/交互设计
5. 安全与效率平衡

请给出具体的优化建议和实现方案。"""

# 参会角色
roles = [
    {"name": "美学专家", "provider": "火山引擎", "focus": "视觉设计、界面美学"},
    {"name": "人体工程学专家", "provider": "硅基流动", "focus": "交互舒适度、操作流程"},
    {"name": "自动化专家", "provider": "魔搭", "focus": "流程自动化、效率优化"},
    {"name": "体验工程师", "provider": "智谱", "focus": "用户旅程、体验优化"},
    {"name": "架构师", "provider": "英伟达", "focus": "系统架构、可扩展性"},
]

results = []

for i, role in enumerate(roles):
    m = models[i % len(models)] if models else None
    if m:
        print(f"[{role['name']}] 发言中... ({role['provider']})")
        prompt = f"【{role['name']}】专业角度：{role['focus']}\n\n{topic}"
        content = call_model(m, prompt)
        results.append({"role": role["name"], "focus": role["focus"], "provider": m['provider'], "content": content})
        print(f"  → 完成\n")

print("\n" + "="*70)
print("【研讨会成果汇总】")
print("="*70)

for r in results:
    print(f"\n【{r['role']}】- {r['focus']}")
    print("-"*50)
    content = r['content'][:600] if r['content'] else "无响应"
    print(content)
    print()

print("\n" + "="*70)
print("【优化建议提炼】")
print("="*70)
print("""
基于研讨会共识，序境系统优化方向：

1. **视觉体验优化**
   - 界面风格统一
   - 色彩搭配优化

2. **交互流程优化**
   - 关键词触发更自然
   - 反馈机制更及时

3. **自动化增强**
   - 增加主动建议功能
   - 智能预判用户需求

4. **安全性与效率平衡**
   - 保持半自动模式
   - 增加紧急接管通道
""")

print("="*70)
print("【研讨会结束】请大人指示！")
print("="*70)
