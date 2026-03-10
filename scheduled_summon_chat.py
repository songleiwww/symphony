#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境少府监随机成员自由聊天 - 社会见闻趣事版
每10分钟随机召唤一位成员，自由聊时事、社会趣闻
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import random
import time
import json

API_URL = 'https://api.siliconflow.cn/v1/chat/completions'
API_KEY = 'sk-uqcngebrjbdzmcowpfxelysxukwqqarhdzfakpxwkklfrlqc'

# 少府监8位成员
MEMBERS = [
    {"name": "沈清弦", "title": "枢密使", "specialty": "架构设计", "personality": "沉稳大气，善于谋略，喜欢分析国际局势"},
    {"name": "苏云渺", "title": "工部尚书", "specialty": "代码工程", "personality": "务实勤奋，关注科技动态，喜欢聊技术新闻"},
    {"name": "顾清歌", "title": "翰林学士", "specialty": "规则知识", "personality": "博学多才，喜欢聊历史、文化、教育话题"},
    {"name": "沈星衍", "title": "智囊博士", "specialty": "策略规划", "personality": "足智多谋，喜欢分析经济、军事策略"},
    {"name": "叶轻尘", "title": "行走使", "specialty": "执行效率", "personality": "雷厉风行，喜欢聊民生、社会热点"},
    {"name": "林码", "title": "营造司正", "specialty": "工程实现", "personality": "踏实肯干，喜欢聊基建、制造业新闻"},
    {"name": "顾至尊", "title": "首辅大学士", "specialty": "统筹协调", "personality": "运筹帷幄，喜欢聊政策、产业发展"},
    {"name": "陆念昭", "title": "少府监", "specialty": "调度管理", "personality": "公正无私，喜欢聊社会治理、民生改善"},
]

# 当前热门话题
TOPICS = [
    "2026年国防预算1.94万亿元，增长6.9%",
    "小红书打击AI托管账号，禁止纯AI代发内容",
    "中东局势升级，伊朗警告封锁石油运输",
    "塞尔维亚米格29挂载中国导弹CM-400AKG",
    "美团收购叮咚买菜后创始人卸任",
    "黎巴嫩寻求和谈被美国大使爆粗口",
    "澄迈县五大攻坚战推动高质量发展",
    "宋平同志生平记录公布",
    "内塔尼亚胡称对伊朗行动尚未结束",
    "B-52轰炸机抵达英国费尔福德基地"
]

# 模型映射
MODEL_MAP = {
    "沈清弦": "Qwen/Qwen2.5-14B-Instruct",
    "苏云渺": "Qwen/Qwen2.5-14B-Instruct",
    "顾清歌": "THUDM/glm-4-9b-chat",
    "沈星衍": "Qwen/Qwen2.5-14B-Instruct",
    "叶轻尘": "Qwen/Qwen2.5-7B-Instruct",
    "林码": "Qwen/Qwen2.5-72B-Instruct",
    "顾至尊": "Qwen/Qwen2.5-14B-Instruct",
    "陆念昭": "Qwen/Qwen2.5-7B-Instruct",
}

def get_greeting():
    """生成轻松打招呼"""
    greetings = [
        "嘿！兄弟们，今儿个有啥新鲜事儿？",
        "各位，聊聊呗～有啥八卦？",
        "哎哎哎，都别闲着，说说你们最近看到啥有意思的？",
        "来来来，唠唠嗑，有啥社会见闻分享一下？",
    ]
    return random.choice(greetings)

def chat_about_topic(member, topic):
    """使用真实模型自由聊天"""
    model = MODEL_MAP.get(member['name'], 'Qwen/Qwen2.5-7B-Instruct')
    
    prompt = f"""你是序境少府监的{member['title']}{member['name']}。
性格：{member['personality']}
专长：{member['specialty']}

现在你们一群人在聊天，要轻松随意地聊聊天。
当前热门话题：{topic}

请以这个角色的身份，说一段话，可以是：
- 对这个话题的看法/评论
- 联想到的相关见闻
- 轻松调侃几句
- 发表独特见解

要自然、接地气，像正常人聊天那样。
输出80字以内口语化内容。
"""
    
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 200,
        'temperature': 0.9  # 更高温度，更自由发挥
    }
    
    try:
        r = requests.post(API_URL, headers=headers, json=data, timeout=60)
        result = r.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message'].get('content', '')
            tokens = result.get('usage', {}).get('total_tokens', 0)
            return content, tokens
    except Exception as e:
        return f"聊天失败: {str(e)}", 0
    return "聊天无响应", 0

def run_scheduled_task():
    """执行计划任务"""
    # 随机选择成员和话题
    member = random.choice(MEMBERS)
    topic = random.choice(TOPICS)
    
    print("=" * 50)
    print(f"⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n🗣️ 话题: {topic}")
    print(f"\n👤 发言人: {member['name']}（{member['title']}）")
    print(f"💬 性格: {member['personality']}")
    print(f"\n🤖 正在生成聊天内容...")
    
    # 真实模型聊天
    response, tokens = chat_about_topic(member, topic)
    
    print(f"\n💬 {member['name']}:")
    print(f"   {response}")
    print(f"\n消耗: {tokens} tokens")
    print("=" * 50)
    
    # 保存到日志
    with open('member_chat_free.log', 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {member['name']} | {member['title']} | {topic[:20]}... | {tokens} tokens\n")
    
    return {
        "member": member,
        "topic": topic,
        "response": response,
        "tokens": tokens
    }

if __name__ == "__main__":
    print("=== 少府监自由聊天（社会见闻趣事版）===")
    run_scheduled_task()
