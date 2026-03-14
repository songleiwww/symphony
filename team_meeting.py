# 序境全员开发建议会议
import json
import requests
import time
import sys
import io

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 团队成员配置
team = [
    {'name': '沈清弦', 'model': 'ark-code-latest', 'focus': '架构设计'},
    {'name': '沈怀秋', 'model': 'deepseek-v3.2', 'focus': '安全'},
    {'name': '苏云渺', 'model': 'doubao-seed-2.0-code', 'focus': '开发'},
    {'name': '陆鸣镝', 'model': 'glm-4.7', 'focus': '测试'},
    {'name': '顾清歌', 'model': 'kimi-k2.5', 'focus': '运维'},
    {'name': '沈轻罗', 'model': 'MiniMax-M2.5', 'focus': '策划'},
]

# 最近学习的主题
topics = '''
最近学习的关键知识点：
1. AI安全：工信部提示OpenClaw安全风险（信任边界模糊、自主决策风险）
2. 智能驾驶：自动驾驶立法、醉酒辅助驾驶刑责
3. 养老机器人：AI在养老领域的应用场景
4. 消费经济：董明珠观点「促消费先加工资」
5. 预测市场：Polymarket模式（预测市场+区块链）
6. 上海经验：法治化营商环境、文商旅融合
7. 地缘政治：美伊冲突、油价波动、滞胀风险
'''

API_URL = 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions'
API_KEY = '3b922877-3fbe-45d1-a298-53f2231c5224'

print("="*70)
print("[DianXin] XuQing Team Development Suggestion Meeting")
print("="*70)
print()

results = []
for member in team:
    prompt = f'''你是序境团队核心成员「{member['name']}」，擅长「{member['focus']}」。
{topics}

请结合你的专长，从以上学习内容中提取对序境（AI Agent多模型协作系统）开发最有价值的1-2个点，提出具体开发建议。
要求：
1. 紧扣你的专长领域
2. 结合最近学习到的知识
3. 提出可执行的具体建议
4. 50-100字
'''
    try:
        print(f"-> {member['name']} ({member['model']}) thinking...", flush=True)
        response = requests.post(API_URL, headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }, json={
            'model': member['model'],
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 200
        }, timeout=60)
        
        result = response.json()
        content = result.get('choices', [{}])[0].get('message', {}).get('content', 'Error')
        results.append({
            'name': member['name'],
            'focus': member['focus'],
            'model': member['model'],
            'suggestion': content
        })
        print(f"   [OK]")
    except Exception as e:
        print(f"   [Error]: {str(e)[:30]}")
        results.append({
            'name': member['name'],
            'focus': member['focus'],
            'model': member['model'],
            'suggestion': f'调用失败: {str(e)[:30]}'
        })

print()
print("="*70)
print("[JieGuo] XuQing Core Team Development Suggestions")
print("="*70)
for r in results:
    print(f"\n[{r['name']}] Expertise: {r['focus']} | Model: {r['model']}")
    print("-" * 50)
    print(r['suggestion'])
