import sys
import os
import sqlite3
import requests
sys.path.insert(0, os.path.dirname(__file__))
from db.database import SymphonyDatabase

db = SymphonyDatabase()

# 获取MiniMax配置
conn = db.get_connection()
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT * FROM provider_registry WHERE provider_code='minimax'")
provider = dict(cursor.fetchone())
conn.close()

api_key = provider['api_key']
base_url = provider['base_url']
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 生成语音回复
text = "宋磊你好，MiniMax服务已经全部配置完成，所有可用模型都已经测试通过，系统运行稳定，后续有任何调整需求随时告诉我哦。"
payload = {
    "model": "speech-2.8-hd",
    "text": text,
    "voice_name": "female-shaonv",
    "audio_format": "mp3"
}

response = requests.post(f"{base_url}/text_to_speech", json=payload, headers=headers, timeout=15)
if response.status_code == 200:
    # 保存语音文件
    output_path = "C:\\Users\\Administrator\\.openclaw\\workspace\\minimax_reply.mp3"
    with open(output_path, "wb") as f:
        f.write(response.content)
    print("语音回复已生成，保存到：" + output_path)
    print("内容：" + text)
else:
    print("语音生成失败，状态码：" + str(response.status_code) + "，错误：" + response.text)
