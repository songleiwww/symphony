# 序境系统优化开发会议
import json
import requests
import time
import sys
import io
from datetime import datetime

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 核心优化团队配置
optimization_team = [
    {'name': '沈清弦', 'model': 'ark-code-latest', 'focus': '架构设计', 'role': '架构师', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
    {'name': '沈怀秋', 'model': 'deepseek-v3.2', 'focus': '用户体验', 'role': '体验设计', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
    {'name': '苏云渺', 'model': 'doubao-seed-2.0-code', 'focus': '代码优化', 'role': '开发', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
    {'name': '陆鸣镝', 'model': 'glm-4.7', 'focus': '测试验证', 'role': '测试', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
    {'name': '顾清歌', 'model': 'kimi-k2.5', 'focus': '性能优化', 'role': '性能', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
    {'name': '沈轻罗', 'model': 'glm-4.7', 'focus': '报告优化', 'role': '报告', 'api_key': '3b922877-3fbe-45d1-a298-53f2231c5224'},
]

# 优化任务
task = '''
优化任务：提升序境系统与用户交互体验

需要优化的方向：
1. 拟人化：增加人物性格设定、对话风格
2. 报告排版：优化飞书阅读排版、表格渲染
3. 真实度：确保模型调用真实、Token统计准确
4. 性格：每个成员性格设定、互动风格
5. 调度优化：模型配合工作关系优化

请结合你的专长，针对以上方向提出具体优化建议。
要求：
1. 紧扣你的专长领域
2. 提出可执行的具体方案
3. 50-150字
4. 最后附上职位述职报告
'''

API_URL = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'

# 调度记录
dispatch_records = []

def call_model(member):
    prompt = f'''你是序境团队成员「{member['name']}」，擅长「{member['focus']}」，职位「{member['role']}」。
{task}

请结合你的专长，提出具体优化建议。
'''

    start_time = time.time()
    tokens_used = 0
    
    try:
        print(f"  -> [{member['name']}] Calling {member['model']}...", end=" ", flush=True)
        
        response = requests.post(API_URL, headers={
            'Authorization': f'Bearer {member["api_key"]}',
            'Content-Type': 'application/json'
        }, json={
            'model': member['model'],
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 300
        }, timeout=120)
        
        elapsed = time.time() - start_time
        
        result = response.json()
        
        if 'usage' in result:
            tokens_used = result['usage'].get('total_tokens', 0)
        
        content = result.get('choices', [{}])[0].get('message', {}).get('content', 'Error')
        
        dispatch_records.append({
            'name': member['name'],
            'model': member['model'],
            'role': member['role'],
            'focus': member['focus'],
            'status': 'SUCCESS',
            'tokens': tokens_used,
            'elapsed': round(elapsed, 2),
            'content': content
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
            'focus': member['focus'],
            'status': 'FAILED',
            'tokens': 0,
            'elapsed': round(elapsed, 2),
            'error': error_msg
        })
        
        print(f"[FAILED] {error_msg}")
        return f"调用失败: {error_msg}"

print("="*70)
print("[XuQing] 序境系统优化开发会议")
print("="*70)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 调度团队
print("[KaiFa] 正在调度团队成员进行优化开发...")
print("-"*50)

results = []
for member in optimization_team:
    result = call_model(member)
    results.append({'member': member, 'result': result})
    time.sleep(1)

# 统计
print()
print("="*70)
print("[TongJi] 调度统计")
print("="*70)

total_tokens = sum(r['tokens'] for r in dispatch_records)
success_count = sum(1 for r in dispatch_records if r['status'] == 'SUCCESS')

print(f"总调度人数: {len(dispatch_records)}")
print(f"成功: {success_count}")
print(f"失败: {len(dispatch_records) - success_count}")
print(f"Token总消耗: {total_tokens}")
print()

# 保存记录
with open('optimization_dispatch.json', 'w', encoding='utf-8') as f:
    json.dump(dispatch_records, f, ensure_ascii=False, indent=2)
print("[BaoCun] 调度记录已保存")

# 输出结果
print()
print("="*70)
print("[JieGuo] 优化建议汇总")
print("="*70)

for r in results:
    m = r['member']
    print(f"\n{'='*50}")
    print(f"[{m['name']}] 职位: {m['role']} | 专长: {m['focus']} | 模型: {m['model']}")
    print(f"Token消耗: {dispatch_records[results.index(r)]['tokens']}")
    print("-"*50)
    print(r['result'])
