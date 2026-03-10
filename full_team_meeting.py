# 序境全员开发建议会议 - 真实调度版
import json
import requests
import time
import sys
import io
import os

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 核心团队配置
core_team = [
    {'name': '沈清弦', 'model': 'ark-code-latest', 'focus': '架构设计', 'role': '核心-架构师', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
    {'name': '沈怀秋', 'model': 'deepseek-v3.2', 'focus': '安全', 'role': '核心-安全', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
    {'name': '苏云渺', 'model': 'doubao-seed-2.0-code', 'focus': '开发', 'role': '核心-开发', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
    {'name': '陆鸣镝', 'model': 'glm-4.7', 'focus': '测试', 'role': '核心-测试', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
    {'name': '顾清歌', 'model': 'kimi-k2.5', 'focus': '运维', 'role': '核心-运维', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
    {'name': '沈轻罗', 'model': 'MiniMax-M2.5', 'focus': '策划', 'role': '核心-策划', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
]

# 技术支援团队配置
tech_team = [
    {'name': '叶寒舟', 'model': 'cherry-nvidia/glm-4.7', 'focus': '通用推理', 'role': '技术-GLM', 'api_key': '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'},
    {'name': '柳烟罗', 'model': 'cherry-nvidia/llama-3.1-405b', 'focus': '开源模型', 'role': '技术-Llama', 'api_key': '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'},
    {'name': '风无痕', 'model': 'cherry-nvidia/nemotron', 'focus': '长对话', 'role': '技术-Nemotron', 'api_key': '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'},
    {'name': '沐清秋', 'model': 'cherry-nvidia/mistral-large-3', 'focus': '多语言', 'role': '技术-Mistral', 'api_key': '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'},
    {'name': '凌天羽', 'model': 'cherry-nvidia/qwen3-coder-480b', 'focus': '代码生成', 'role': '技术-千问', 'api_key': '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'},
    {'name': '云浅梦', 'model': 'cherry-nvidia/deepseek-v3.2', 'focus': '推理能力', 'role': '技术-DeepSeek', 'api_key': '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'},
]

# 最近学习的主题
topics = '''
最近学习的关键知识点：
1. AI安全：工信部提示OpenClaw安全风险（信任边界模糊、自主决策风险）
2. 智能驾驶：自动驾驶立法、醉酒辅助驾驶刑责
3. 养老机器人：AI在养老领域的应用场景
4. 消费经济：董明珠观点「促消费先加工资」
5. AI产业规模：「十五五」末AI相关产业规模将超10万亿元
6. 全民养虾：OpenClaw为何在中国爆发（算力抽水机、数据饥渴、低价API格局）
7. 外贸数据：1-2月出口同比+21.8%，民营企业+22.8%
'''

API_URL = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
NVIDIA_URL = 'https://integrate.api.nvidia.com/v1/chat/completions'

# 调度记录
dispatch_records = []

def call_model(member):
    prompt = f'''你是序境团队成员「{member['name']}」，擅长「{member['focus']}」，职位「{member['role']}」。
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
        # 判断使用哪个API
        if 'nvidia' in member['model'].lower() or 'cherry-nvidia' in member['model'].lower():
            url = NVIDIA_URL
            api_key = member['api_key']
            model = member['model'].replace('cherry-nvidia/', '')
        else:
            url = API_URL
            api_key = member['api_key']
            model = member['model']
        
        print(f"  -> Calling {model}...", end=" ", flush=True)
        
        response = requests.post(url, headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }, json={
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 200
        }, timeout=90)
        
        elapsed = time.time() - start_time
        
        result = response.json()
        
        # 提取token使用情况
        if 'usage' in result:
            tokens_used = result['usage'].get('total_tokens', 0)
        
        content = result.get('choices', [{}])[0].get('message', {}).get('content', 'Error')
        
        # 记录调度
        dispatch_records.append({
            'name': member['name'],
            'model': model,
            'role': member['role'],
            'status': 'SUCCESS',
            'tokens': tokens_used,
            'elapsed': round(elapsed, 2),
            'content': content[:200]
        })
        
        print(f"[OK] {tokens_used} tokens, {elapsed:.1f}s")
        return content
        
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
        
        print(f"[FAILED] {error_msg}")
        return f"调用失败: {error_msg}"

print("="*70)
print("[DiYiTi] XuQing Core Team Development Suggestion Meeting")
print("="*70)
print()

# 调度核心团队
print("[JiaDui] Dispatching Core Team (6 members)...")
print("-"*50)
core_results = []
for member in core_team:
    result = call_model(member)
    core_results.append({'member': member, 'result': result})
    time.sleep(1)  # 避免API限流

print()
print("="*70)
print("[DiErTi] Dispatching Tech Support Team (6 members)...")
print("-"*50)
tech_results = []
for member in tech_team:
    result = call_model(member)
    tech_results.append({'member': member, 'result': result})
    time.sleep(1)

# 统计
print()
print("="*70)
print("[TongJi] Dispatch Statistics")
print("="*70)

total_tokens = sum(r['tokens'] for r in dispatch_records)
success_count = sum(1 for r in dispatch_records if r['status'] == 'SUCCESS')
failed_count = sum(1 for r in dispatch_records if r['status'] == 'FAILED')

print(f"Total dispatched: {len(dispatch_records)}")
print(f"Success: {success_count}")
print(f"Failed: {failed_count}")
print(f"Total tokens: {total_tokens}")
print()

# 保存调度记录
with open('dispatch_records.json', 'w', encoding='utf-8') as f:
    json.dump(dispatch_records, f, ensure_ascii=False, indent=2)
print("[BaoCun] Dispatch records saved to dispatch_records.json")

# 输出结果
print()
print("="*70)
print("[JieGuo] Team Suggestions Summary")
print("="*70)

print("\n>>> Core Team Results >>>")
for r in core_results:
    m = r['member']
    print(f"\n[{m['name']}] Role: {m['role']} | Model: {m['model']}")
    print("-"*40)
    print(r['result'][:300])

print("\n\n>>> Tech Support Results >>>")
for r in tech_results:
    m = r['member']
    print(f"\n[{m['name']}] Role: {m['role']} | Model: {m['model']}")
    print("-"*40)
    print(r['result'][:300])
