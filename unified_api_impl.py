# Symphony Unified Api Impl
# 开发者: 林思远 (API架构师)
# 生成时间: 2026-03-08T01:57:37.907006
# 版本: 1.5.1

import requests
import json

class UnifiedAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    def call_model(self, model_id, data):
        url = f"{self.base_url}/models/{model_id}/call"
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps(data)
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            return self.parse_response(response)
        except requests.RequestException as e:
            return {'error': str(e)}

    def get_status(self, task_id):
        url = f"{self.base_url}/tasks/{task_id}/status"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return self.parse_response(response)
        except requests.RequestException as e:
            return {'error': str(e)}

    def cancel_task(self, task_id):
        url = f"{self.base_url}/tasks/{task_id}/cancel"
        try:
            response = requests.delete(url)
            response.raise_for_status()
            return self.parse_response(response)
        except requests.RequestException as e:
            return {'error': str(e)}

    def parse_response(self, response):
        try:
            data = response.json()
            token_count = sum([len(token) for token in data.get('tokens', [])])
            return {'data': data, 'token_count': token_count}
        except json.JSONDecodeError:
            return {'error': 'Invalid JSON response'}

# 示例用法
if __name__ == "__main__":
    api = UnifiedAPI('https://api.symphony.com')
    # 假设模型ID和数据
    model_id = '123'
    data = {'input': 'Hello, Symphony!'}
    # 调用模型
    call_response = api.call_model(model_id, data)
    print("Call Model Response:", call_response)

    # 获取任务状态
    task_id = 'abc'
    status_response = api.get_status(task_id)
    print("Get Status Response:", status_response)

    # 取消任务
    cancel_response = api.cancel_task(task_id)
    print("Cancel Task Response:", cancel_response)