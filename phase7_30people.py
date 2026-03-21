# -*- coding: utf-8 -*-
"""
序境系统 - 第七阶段：30人团队实施+API速度测试
"""
import sys
import io
import sqlite3
import requests
import time
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data/symphony.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

def get_model(provider):
    c.execute("SELECT 模型名称, 模型标识符, API地址, API密钥 FROM 模型配置表 WHERE 服务商=? AND 在线状态='online' LIMIT 1", (provider,))
    r = c.fetchone()
    if r:
        return {"name": r[0], "identifier": r[1], "url": r[2], "key": r[3], "provider": provider}
    return None

def call_model_and_test_speed(model, prompt="你好"):
    """调用模型并测试响应速度"""
    url = model['url']
    if '/chat/completions' not in url:
        url = url.rstrip('/') + '/chat/completions'
    
    start_time = time.time()
    
    try:
        resp = requests.post(url, json={"model": model['identifier'], "messages": [{"role": "user", "content": prompt}], "max_tokens": 50},
                          headers={"Authorization": f"Bearer {model['key']}", "Content-Type": "application/json"}, timeout=30)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        if resp.status_code == 200:
            return {
                "success": True,
                "elapsed_ms": int(elapsed * 1000),
                "content": resp.json()['choices'][0]['message']['content'][:50]
            }
        else:
            return {
                "success": False,
                "elapsed_ms": int(elapsed * 1000),
                "error": f"HTTP {resp.status_code}"
            }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "elapsed_ms": int((end_time - start_time) * 1000),
            "error": str(e)[:50]
        }

# 获取所有服务商模型
providers = ['火山引擎', '硅基流动', '魔搭', '智谱', '英伟达']
models = []
for p in providers:
    m = get_model(p)
    if m:
        models.append(m)

conn.close()

print("="*70)
print("【序境系统 - 第七阶段：30人团队+API速度测试】")
print("="*70)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 30人团队分组
teams = {
    "实施组": [
        {"role": "实施负责人", "task": "覆盖率提升实施", "provider": "火山引擎"},
        {"role": "实施工程师", "task": "新增角色开发", "provider": "火山引擎"},
        {"role": "实施工程师", "task": "弱边界用例开发", "provider": "火山引擎"},
        {"role": "实施工程师", "task": "覆盖率统计模块", "provider": "火山引擎"},
        {"role": "实施工程师", "task": "自动化测试集成", "provider": "火山引擎"},
        {"role": "实施工程师", "task": "回归测试执行", "provider": "火山引擎"},
    ],
    "接管组": [
        {"role": "接管负责人", "task": "全自动接管方案", "provider": "智谱"},
        {"role": "AI工程师", "task": "AI模型集成", "provider": "智谱"},
        {"role": "AI工程师", "task": "自动决策引擎", "provider": "智谱"},
        {"role": "AI工程师", "task": "场景测试用例", "provider": "智谱"},
        {"role": "AI工程师", "task": "边缘情况处理", "provider": "智谱"},
        {"role": "AI工程师", "task": "接管日志分析", "provider": "智谱"},
    ],
    "健康组": [
        {"role": "健康负责人", "task": "动态阈值方案", "provider": "硅基流动"},
        {"role": "算法工程师", "task": "基线算法实现", "provider": "硅基流动"},
        {"role": "算法工程师", "task": "阈值计算模块", "provider": "硅基流动"},
        {"role": "算法工程师", "task": "告警策略配置", "provider": "硅基流动"},
        {"role": "算法工程师", "task": "监控面板集成", "provider": "硅基流动"},
        {"role": "算法工程师", "task": "阈值调优验证", "provider": "硅基流动"},
    ],
    "运维组": [
        {"role": "运维负责人", "task": "CI/CD流水线", "provider": "英伟达"},
        {"role": "运维工程师", "task": "自动化部署脚本", "provider": "英伟达"},
        {"role": "运维工程师", "task": "回滚机制实现", "provider": "英伟达"},
        {"role": "运维工程师", "task": "监控告警配置", "provider": "英伟达"},
        {"role": "运维工程师", "task": "日志分析系统", "provider": "英伟达"},
        {"role": "运维工程师", "task": "性能优化实施", "provider": "英伟达"},
    ],
    "测试组": [
        {"role": "测试负责人", "task": "测试计划制定", "provider": "魔搭"},
        {"role": "测试工程师", "task": "单元测试编写", "provider": "魔搭"},
        {"role": "测试工程师", "task": "集成测试执行", "provider": "魔搭"},
        {"role": "测试工程师", "task": "压力测试执行", "provider": "魔搭"},
        {"role": "测试工程师", "task": "测试报告编写", "provider": "魔搭"},
        {"role": "测试工程师", "task": "缺陷跟踪管理", "provider": "魔搭"},
    ],
}

print("【30人团队编制】")
print(f"总人数: {sum(len(v) for v in teams.values())}人\n")

for group, members in teams.items():
    print(f"  {group}: {len(members)}人")

print()
print("="*70)
print("【API响应速度测试】")
print("="*70)

# 测试每个模型的速度
speed_results = []

print("\n测试各服务商API响应速度...\n")

for model in models:
    print(f"测试: {model['name']} ({model['provider']})...")
    
    # 多次测试取平均值
    times = []
    for i in range(3):
        result = call_model_and_test_speed(model, "你好")
        times.append(result['elapsed_ms'])
        print(f"  第{i+1}次: {result['elapsed_ms']}ms - {'✅' if result['success'] else '❌'}")
    
    avg_time = sum(times) // len(times)
    
    speed_results.append({
        "provider": model['provider'],
        "model": model['name'],
        "avg_ms": avg_time,
        "times": times
    })
    
    print(f"  平均: {avg_time}ms\n")

# 排序
speed_results.sort(key=lambda x: x['avg_ms'])

print()
print("="*70)
print("【速度测试结果排名】")
print("="*70)

print("\n| 排名 | 服务商 | 模型 | 平均响应时间 |")
print("|------|--------|------|-------------|")

for i, r in enumerate(speed_results, 1):
    print(f"| {i} | {r['provider']} | {r['model'][:15]} | {r['avg_ms']}ms |")

# 统计
total_avg = sum(r['avg_ms'] for r in speed_results) // len(speed_results)
fastest = speed_results[0]
slowest = speed_results[-1]

print(f"\n**最快**: {fastest['provider']} ({fastest['avg_ms']}ms)")
print(f"**最慢**: {slowest['provider']} ({slowest['avg_ms']}ms)")
print(f"**平均**: {total_avg}ms")

print()
print("="*70)
print("【30人团队任务分配】")
print("="*70)

print("""
| 小组 | 人数 | 任务 | 状态 |
|------|------|------|------|
| 实施组 | 6人 | 覆盖率提升 | 待执行 |
| 接管组 | 6人 | 全自动接管 | 待执行 |
| 健康组 | 6人 | 动态健康阈值 | 待执行 |
| 运维组 | 6人 | CI/CD流水线 | 待执行 |
| 测试组 | 6人 | 测试执行 | 待执行 |
""")

print("="*70)
print("【第七阶段完成】")
print("="*70)
print("✅ 30人团队已编制")
print("✅ API速度测试完成")
print("请大人指示！")
print("="*70)
