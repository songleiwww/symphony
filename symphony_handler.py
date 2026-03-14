# -*- coding: utf-8 -*-
"""
序境系统 - 加入官署信息
"""
import sys, os, importlib.util, requests, time, json
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_CONFIGS = {
    '火山引擎': {
        'url': 'https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions',
        'key': '3b922877-3fbe-45d1-a298-53f2231c5224',
        'models': {'glm-4.7': 'glm-4.7', 'glm-4-flash': 'glm-4-flash'}
    },
    'NVIDIA': {
        'url': 'https://integrate.api.nvidia.com/v1/chat/completions',
        'key': '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',
        'models': {'glm-4.7': 'mistralai/mixtral-8x7b-instruct-v0.1', 'glm-4-flash': 'mistralai/mixtral-8x7b-instruct-v0.1', 'Qwen2.5-14B': 'Qwen/Qwen2.5-14B-Instruct'}
    }
}

# 官属完整信息：包含官署(隶属部门)
OFFICIALS = {
    'evolve_001': {'name': '沈清弦', 'title': '枢密使', 'office': '枢密院', 'level': 1},
    'evolve_002': {'name': '陆念昭', 'title': '少府监', 'office': '少府监本部', 'level': 1},
    'evolve_003': {'name': '苏云渺', 'title': '工部尚书', 'office': '工部', 'level': 2},
    'evolve_004': {'name': '顾清歌', 'title': '翰林学士', 'office': '翰林院', 'level': 2},
    'evolve_005': {'name': '顾至尊', 'title': '首辅大学士', 'office': '中书省', 'level': 1},
    'evolve_006': {'name': '沈星衍', 'title': '智囊博士', 'office': '枢密院', 'level': 2},
    'evolve_007': {'name': '叶轻尘', 'title': '行走使', 'office': '门下省', 'level': 3},
    'evolve_008': {'name': '林码', 'title': '营造司正', 'office': '工部', 'level': 3},
}

FALLBACK_ORDER = ['NVIDIA', '火山引擎']

def dispatch_official(user_message):
    keywords = {
        '写代码': 'evolve_003', '编程': 'evolve_003',
        '分析': 'evolve_006', '策略': 'evolve_006',
        '饿了': 'evolve_002', '吃饭': 'evolve_002',
        '累': 'evolve_002', '困': 'evolve_002', '不好': 'evolve_002',
        '诗': 'evolve_004', '写诗': 'evolve_004',
    }
    msg = user_message.replace('序境', '').strip()
    for kw, oid in keywords.items():
        if kw in msg:
            return oid
    return 'evolve_002'

def call_model(api_config, model_name, messages):
    url = api_config['url']
    api_key = api_config['key']
    model_map = api_config.get('models', {})
    actual_model = model_map.get(model_name, model_name)
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": actual_model, "messages": messages, "max_tokens": 150}
    
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            usage = result.get('usage', {})
            provider_name = '火山引擎'
            for k, v in API_CONFIGS.items():
                if v['url'] == api_config['url']:
                    provider_name = k
                    break
            return {'success': True, 'reply': result['choices'][0]['message']['content'], 'provider': provider_name, 'model': actual_model, 'elapsed': elapsed, 'tokens': {'prompt': usage.get('prompt_tokens', 0), 'completion': usage.get('completion_tokens', 0), 'total': usage.get('total_tokens', 0)}}
        return {'success': False, 'error': f"HTTP {resp.status_code}"}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def process_message(user_message):
    role_id = dispatch_official(user_message)
    official = OFFICIALS.get(role_id, {'name': '未知', 'title': '未知', 'office': '未知', 'level': 1})
    original_model = 'glm-4.7'
    original_provider = '火山引擎'
    msg = user_message.replace('序境', '').strip()
    system_prompt = f"你是中国古代唐朝的{official['title']}，用文言文简洁回复。"
    
    for provider in [original_provider] + [p for p in FALLBACK_ORDER if p != original_provider]:
        if provider not in API_CONFIGS: continue
        if not API_CONFIGS[provider].get('key'): continue
        
        result = call_model(API_CONFIGS[provider], original_model, [{"role": "system", "content": system_prompt}, {"role": "user", "content": msg}])
        
        if result['success']:
            # 保存日志
            log_entry = {"timestamp": time.strftime('%Y-%m-%d %H:%M:%S'), "user_message": user_message, "official": {"id": role_id, "name": official['name'], "title": official['title'], "office": official['office'], "level": official['level']}, "model_info": {"provider": result['provider'], "model": result['model']}, "tokens": result['tokens'], "elapsed": result['elapsed'], "reply": result['reply']}
            log_file = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\call_log.json'
            logs = json.load(open(log_file, 'r', encoding='utf-8')) if os.path.exists(log_file) else []
            logs.append(log_entry)
            json.dump(logs, open(log_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            
            # 输出格式
            print("【回复】")
            print(result['reply'])
            print("---")
            # 这里加入官署信息
            print(f"任职：{official['name']}（{official['office']}）· {official['title']}")
            print(f"{result['provider']}/{result['model']} | {result['elapsed']:.1f}秒 | {result['tokens']['total']}tokens")
            return result['reply']
    
    print("【系统繁忙】请稍后再试")
    return "请稍后再试"

if __name__ == "__main__":
    process_message("序境 不好")
