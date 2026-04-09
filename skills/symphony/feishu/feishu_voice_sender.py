# -*- coding: utf-8 -*-
"""
飞书语音气泡发送器 v2.0 - 序境系统内核集成版
=============================================
从 symphony.db 读取配置，支持 TTS 提供商选择和语音发送

配置来源: symphony.db (model_config, tool_registry)
"""

import os
import sys
import json
import time
import sqlite3
import tempfile
import subprocess
import requests
from typing import Optional, Dict, Any

# 数据库路径
DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'


class SymphonyVoiceConfig:
    """从 symphony.db 读取语音配置"""
    
    @staticmethod
    def get_voice_config() -> Dict[str, Any]:
        """
        获取语音工具配置
        从 symphony.db 的 tool_registry 表读取，无则返回默认值
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT config FROM tool_registry 
                WHERE tool_name = 'feishu_voice' AND is_enabled = 1
            """)
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return json.loads(row[0])
        except Exception as e:
            print(f'[VoiceConfig] 读取配置失败: {e}')
        
        return SymphonyVoiceConfig._default_config()
    
    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """默认配置"""
        return {
            'provider': 'edge_tts',
            'voice': 'zh-CN-XiaoxiaoNeural',
            'format': 'opus',
            'sample_rate': 16000,
            'bitrate': '16k',
            'feishu_app_id': 'cli_a94c91048e781cd6',
            'feishu_app_secret': 'fm3Ey2RmbL75K523T0nZlcJDmCt67il1',
            'user_open_id': 'ou_698e215c481e88b814e628a92592eca5',
            'temp_dir': 'C:\\Users\\Administrator\\voice_tmp',
            'max_retries': 3,
            'timeout': 30
        }
    
    @staticmethod
    def save_voice_config(config: Dict[str, Any]) -> bool:
        """保存语音配置到 symphony.db"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT UNIQUE NOT NULL,
                    config TEXT,
                    is_enabled INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            config_json = json.dumps(config, ensure_ascii=False)
            cursor.execute("""
                INSERT INTO tool_registry (tool_name, config, is_enabled, updated_at)
                VALUES ('feishu_voice', ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(tool_name) 
                DO UPDATE SET config = excluded.config, updated_at = CURRENT_TIMESTAMP
            """, (config_json,))
            
            conn.commit()
            conn.close()
            print('[VoiceConfig] 配置已保存到 symphony.db')
            return True
        except Exception as e:
            print(f'[VoiceConfig] 保存配置失败: {e}')
            return False


class SymphonyTTSAdapter:
    """TTS 适配器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self.config = SymphonyVoiceConfig.get_voice_config()
    
    def synthesize(self, text: str, voice: str = None) -> bytes:
        """
        合成语音
        当前使用 edge_tts（通过 subprocess 调用 node-edge-tts）
        未来可扩展为 aliyun WebSocket SDK
        """
        provider = self.config.get('provider', 'edge_tts')
        voice = voice or self.config.get('voice', 'zh-CN-XiaoxiaoNeural')
        
        if provider == 'edge_tts':
            return self._synthesize_edge_tts(text, voice)
        else:
            raise Exception(f'Provider {provider} not implemented, use edge_tts')
    
    def _synthesize_edge_tts(self, text: str, voice: str) -> bytes:
        """使用 edge_tts 合成语音"""
        temp_dir = self.config.get('temp_dir', 'C:\\Users\\Administrator\\voice_tmp')
        os.makedirs(temp_dir, exist_ok=True)
        mp3_file = os.path.join(temp_dir, f'tts_{int(time.time() * 1000)}.mp3')
        
        # 使用 node 直接运行 edge-tts 模块
        edge_tts_path = r'C:\Users\Administrator\AppData\Roaming\npm\node_modules\node-edge-tts\bin.js'
        
        try:
            result = subprocess.run([
                'node', edge_tts_path, 
                '-t', text,
                '-f', mp3_file,
                '-v', voice
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise Exception(f'TTS failed: {result.stderr}')
            
            with open(mp3_file, 'rb') as f:
                audio_data = f.read()
            
            return audio_data
            
        finally:
            try:
                if os.path.exists(mp3_file):
                    os.unlink(mp3_file)
            except:
                pass


class FeishuVoiceSender:
    """飞书语音气泡发送器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or SymphonyVoiceConfig.get_voice_config()
        self.access_token = None
        self.token_expire_time = 0
    
    def _get_token(self) -> str:
        """获取飞书 access token"""
        current_time = time.time()
        if self.access_token and current_time < self.token_expire_time:
            return self.access_token
        
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/'
        resp = requests.post(url, json={
            'app_id': self.config['feishu_app_id'],
            'app_secret': self.config['feishu_app_secret']
        }, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get('code') == 0:
            self.access_token = result['tenant_access_token']
            self.token_expire_time = current_time + result.get('expire', 7200) - 300
            return self.access_token
        else:
            raise Exception(f'获取 token 失败: {result.get("msg")}')
    
    def _upload_file(self, file_content: bytes, file_name: str, duration: int) -> str:
        """上传音频文件获取 file_key"""
        boundary = '----FeishuBoundary' + str(int(time.time() * 1000))
        
        parts = [
            b'--' + boundary.encode() + b'\r\n',
            b'Content-Disposition: form-data; name="file_type"\r\n\r\n',
            b'opus\r\n',
            b'--' + boundary.encode() + b'\r\n',
            b'Content-Disposition: form-data; name="file_name"\r\n\r\n',
            file_name.encode() + b'\r\n',
            b'--' + boundary.encode() + b'\r\n',
            b'Content-Disposition: form-data; name="duration"\r\n\r\n',
            str(duration).encode() + b'\r\n',
            b'--' + boundary.encode() + b'\r\n',
            b'Content-Disposition: form-data; name="file"; filename="' + file_name.encode() + b'"\r\n',
            b'Content-Type: audio/opus\r\n\r\n',
            file_content,
            b'\r\n--' + boundary.encode() + b'--\r\n'
        ]
        body = b''.join(parts)
        
        resp = requests.post(
            'https://open.feishu.cn/open-apis/im/v1/files',
            headers={
                'Authorization': f'Bearer {self._get_token()}',
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Content-Length': str(len(body))
            },
            data=body,
            timeout=15
        )
        resp.raise_for_status()
        result = resp.json()
        
        if result.get('code') == 0:
            return result['data']['file_key']
        else:
            raise Exception(f'文件上传失败: {result.get("msg")}')
    
    def send_audio(self, receive_id: str, file_key: str) -> Dict:
        """发送语音消息"""
        url = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id'
        headers = {
            'Authorization': f'Bearer {self._get_token()}',
            'Content-Type': 'application/json'
        }
        data = {
            'receive_id': receive_id,
            'msg_type': 'audio',
            'content': json.dumps({'file_key': file_key})
        }
        
        resp = requests.post(url, headers=headers, json=data, timeout=15)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get('code') == 0:
            return {'success': True, 'message_id': result['data']['message_id']}
        else:
            raise Exception(f'发送失败: {result.get("msg")}')


def convert_to_opus(mp3_data: bytes, temp_dir: str) -> tuple:
    """将 MP3 转换为 Opus 格式"""
    mp3_path = os.path.join(temp_dir, f'temp_{int(time.time() * 1000)}.mp3')
    opus_path = os.path.join(temp_dir, f'voice_{int(time.time() * 1000)}.opus')
    
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(mp3_path, 'wb') as f:
        f.write(mp3_data)
    
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', mp3_path
        ], capture_output=True, text=True, timeout=10)
        duration_ms = int(float(result.stdout.strip()) * 1000)
        
        subprocess.run([
            'ffmpeg', '-i', mp3_path,
            '-acodec', 'libopus', '-ac', '1', '-ar', '16000', '-b:a', '16k',
            '-vn', opus_path, '-y'
        ], check=True, capture_output=True, timeout=30)
        
        with open(opus_path, 'rb') as f:
            opus_data = f.read()
        
        return opus_data, duration_ms
        
    finally:
        try:
            if os.path.exists(mp3_path):
                os.unlink(mp3_path)
            if os.path.exists(opus_path):
                os.unlink(opus_path)
        except:
            pass


def send_voice_bubble(text: str, receive_id: str = None, voice: str = None) -> Dict[str, Any]:
    """
    发送飞书语音气泡 - 序境系统内核接口
    
    从 symphony.db 读取配置，生成语音并发送为飞书气泡
    
    Args:
        text: 要转换的文本
        receive_id: 接收者 open_id（默认使用配置中的用户）
        voice: 语音角色（可选）
        
    Returns:
        {'success': bool, 'message_id': str, 'error': str}
    """
    config = SymphonyVoiceConfig.get_voice_config()
    receive_id = receive_id or config.get('user_open_id')
    
    try:
        print(f'[VoiceBubble] 正在合成语音: {text[:30]}...')
        tts = SymphonyTTSAdapter()
        mp3_data = tts.synthesize(text, voice)
        
        print(f'[VoiceBubble] 正在转换格式...')
        temp_dir = config.get('temp_dir', 'C:\\Users\\Administrator\\voice_tmp')
        opus_data, duration = convert_to_opus(mp3_data, temp_dir)
        
        print(f'[VoiceBubble] 正在发送至 {receive_id}...')
        sender = FeishuVoiceSender()
        file_key = sender._upload_file(opus_data, 'voice.opus', duration)
        result = sender.send_audio(receive_id, file_key)
        
        if result['success']:
            print(f'[VoiceBubble] 发送成功! Message ID: {result["message_id"]}')
            return result
        else:
            return {'success': False, 'error': '发送失败'}
            
    except Exception as e:
        print(f'[VoiceBubble] 错误: {str(e)}')
        return {'success': False, 'error': str(e)}


def register_voice_tool() -> bool:
    """
    注册语音工具到 symphony.db
    执行一次即可将默认配置写入数据库
    """
    config = SymphonyVoiceConfig._default_config()
    return SymphonyVoiceConfig.save_voice_config(config)


if __name__ == '__main__':
    print('=== 序境系统 - 飞书语音气泡发送测试 ===')
    print('注册语音工具到 symphony.db...')
    register_voice_tool()
    print('\n发送语音气泡...')
    result = send_voice_bubble('你好，这是序境系统内核集成的语音气泡测试')
    print('结果:', result)
