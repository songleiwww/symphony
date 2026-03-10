# 修复技术支援团队API调用
import json
import requests
import time
import sys
import io

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 技术支援团队配置 - 使用火山引擎API
tech_team = [
    {'name': '叶寒舟', 'model': 'glm-4.7', 'focus': '通用推理', 'role': '技术-GLM'},
    {'name': '柳烟罗', 'model': 'deepseek-v3.2', 'focus': '开源模型', 'role': '技术-DeepSeek'},
    {'name': '风无痕', 'model': 'kimi-k2.5', 'focus': '长对话', 'role': '技术-Kimi'},
    {'name': '沐清秋', 'model': 'ark-code-latest', 'focus': '多语言', 'role': '技术-Ark'},
    {'name': '凌天羽', 'model': 'doubao-seed-2.0-code', 'focus': '代码生成', 'role': '技术-代码'},
    {'name': '云浅梦', 'model': 'MiniMax-M2.5', 'focus': '推理能力', 'role': '技术-MiniMax'},
]

topics = '''
最近学习的关键知识点：
1. AI安全：工信部提示OpenClaw安全风险（信任边界模糊、自主决策风险）
2. 智能驾驶：自动驾驶立法、醉酒辅助驾驶刑责
3. 消费经济：董明珠观点「促消费先加工资」
4. AI产业规模：「十五五」末AI相关产业规模将超10万亿元
5. 全民养虾：OpenClaw为何在中国爆发（算力抽水机、数据饥渴、低价API格局）
6. 外贸数据：1-2月出口同比+21.8%，民营企业+22.8%
7. 腾讯小龙虾：WorkBuddy上线紧急扩容10倍
8. Anthropic告五角大楼：AI安全与政府合作争议
'''

API_URL = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
API_KEY = '3b922877-3fbe-45d1-a298-53f2231c5224'

dispatch_records = []

def call_model(member):
    prompt = f'''你是序境技术支援团队成员「{member['name']}」，擅长「{member['focus']}」，职位「{member['role']}」。
{topics}

请结合你的专长，从以上学习内容中提取对序境（AI Agent多模型协作系统）开发最有价值的1-2个点，提出具体开发建议。
要求：
1. 紧扣你的专长领域
2. 结合最近学习到的知识
3. 提出可执行的具体建议
4. 50-100字
5. 最后附上你的职位述职报告（姓名、职位、贡献描述）
'''

    start_time = time.time()
    tokens_used = 0
    
    try:
        print(f"  -> Calling {member['model']}...", end=" ", flush=True)
        
        response = requests.post(API_URL, headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }, json={
            'model': member['model'],
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 200
        }, timeout=90)
        
        elapsed = time.time() - start_time
        
        # 调试：打印响应状态
        print(f"[Status:{response.status_code}]", end=" ", flush=True)
        
        result = response.json()
        
        # 提取token使用情况
        if 'usage' in result:
            tokens_used = result['usage'].get('total_tokens', 0)
        
        content = result.get('choices', [{}])[0].get('message', {}).get('content', 'Error')
        
        # 记录调度
        dispatch_records.append({
            'name': member['name'],
            'model': member['model'],
            'role': member['role'],
            'status': 'SUCCESS',
            'tokens': tokens_used,
            'elapsed': round(elapsed, 2)
        })
        
        print(f"[OK] {tokens_used} tokens, {elapsed:.1f}s")
        return content
        
    except json.JSONDecodeError as e:
        elapsed = time.time() - start_time
        error_msg = f"JSON Error: {str(e)[:30]}"
        
        dispatch_records.append({
            'name': member['name'],
            'model': member['model'],
            'role': member['role'],
            'status': 'JSON_ERROR',
            'tokens': 0,
            'elapsed': round(elapsed, 2),
            'error': error_msg
        })
        
        print(f"[JSON Error] {error_msg}")
        return f"调用失败: {error_msg}"
        
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = str(e)[:50]
        
        dispatch_records.append({
            'name': member['name'],
            'model': member['model'],
            'role': member['role'],
            'status': 'FAILED',
            'tokens': 0,
            'elapsed': round(elapsed, 2),
            'error': error_msg
        })
        
        print(f"[Failed] {error_msg}")
        return f"调用失败: {error_msg}"

print("="*70)
print("[DiErPi] Tech Support Team Dispatch (Fixed)")
print("="*70)
print()

tech_results = []
for member in tech_team:
    result = call_model(member)
    tech_results.append({'member': member, 'result': result})
    time.sleep(2)  # 避免API限流

# 统计
print()
print("="*70)
print("[TongJi] Dispatch Statistics")
print("="*70)

total_tokens = sum(r['tokens'] for r in dispatch_records)
success_count = sum(1 for r in dispatch_records if r['status'] == 'SUCCESS')

print(f"Total dispatched: {len(dispatch_records)}")
print(f"Success: {success_count}")
print(f"Failed: {len(dispatch_records) - success_count}")
print(f"Total tokens: {total_tokens}")

# 输出结果
print()
print("="*70)
print("[JieGuo] Tech Support Team Suggestions")
print("="*70)

for r in tech_results:
    m = r['member']
    print(f"\n[{m['name']}] Role: {m['role']} | Model: {m['model']}")
    print("-"*40)
    print(r['result'][:300])
