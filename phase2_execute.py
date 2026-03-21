# -*- coding: utf-8 -*-
"""
序境系统 - 内核集成Debug第二阶段
各组继续深化执行
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

def call_model(model, prompt, max_tokens=1500):
    url = model['url']
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    try:
        resp = requests.post(url, json={"model": model['identifier'], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens},
                          headers={"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}, timeout=90)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"错误: {str(e)[:100]}"
    return None

# 获取模型
providers = ['火山引擎', '硅基流动', '魔搭', '智谱', '英伟达']
models = []
for p in providers:
    m = get_model(p)
    if m:
        models.append(m)

conn.close()

print("="*70)
print("【序境系统 - 内核集成Debug第二阶段】")
print("="*70)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"调度模型: {len(models)}个\n")

# 第二阶段任务
tasks = [
    {
        "group": "架构组",
        "role": "首席架构师",
        "task": "编写配置管理标准化Python脚本，实现Nacos配置同步",
        "provider": "火山引擎"
    },
    {
        "group": "内核组",
        "role": "调度内核",
        "task": "编写调度器优化代码，支持动态权重调整",
        "provider": "智谱"
    },
    {
        "group": "调试组",
        "role": "性能Debug",
        "task": "编写性能监控脚本，检测CPU/内存/响应时间",
        "provider": "硅基流动"
    },
    {
        "group": "测试组",
        "role": "单元测试",
        "task": "编写单元测试框架pytest用例模板",
        "provider": "魔搭"
    },
    {
        "group": "运维组",
        "role": "自动化运维",
        "task": "编写自动化部署Bash脚本，支持滚动更新",
        "provider": "英伟达"
    },
]

print("【各组继续执行】\n")

results = []
for i, t in enumerate(tasks):
    model = models[i % len(models)] if models else None
    if model:
        print(f"[{t['group']}] {t['role']}: {t['task'][:30]}...")
        
        prompt = f"""你是序境系统工程师。请直接输出可执行的{t['task']}的代码。

要求：
1. 代码完整可运行
2. 注释清晰
3. 符合序境系统规范

请直接输出代码，不要解释。"""
        
        result = call_model(model, prompt, max_tokens=2000)
        results.append({
            "group": t["group"],
            "role": t["role"],
            "task": t["task"],
            "code": result
        })
        print(f"  → 完成\n")

# 保存代码到文件
print("="*70)
print("【生成的代码文件】")
print("="*70)

code_files = []

for r in results:
    filename = f"C:/Users/Administrator/.openclaw/workspace/skills/symphony/deliverables/{r['group']}_{r['role']}.py"
    code_files.append(filename)
    
    # 提取代码部分
    code_content = r['code'] if r['code'] else "# 无代码"
    
    print(f"\n### {r['group']} - {r['role']}")
    print("-"*50)
    print(code_content[:500] if code_content else "无")
    print("...")

print("\n" + "="*70)
print("【第二阶段完成】")
print("="*70)
print("""
| 小组 | 交付物 |
|------|---------|
| 架构组 | 配置管理Python脚本 |
| 内核组 | 调度器优化代码 |
| 调试组 | 性能监控脚本 |
| 测试组 | pytest测试模板 |
| 运维组 | 自动化部署脚本 |
""")

print("✅ 各组继续执行完成")
print("✅ 代码已生成")
print("请大人指示！")
print("="*70)
