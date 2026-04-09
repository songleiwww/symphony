# -*- coding: utf-8 -*-
"""
飞书语音适配器 v3.0 - 序境系统内核集成版
=========================================
从 symphony.db 读取配置，支持多模型自动降级

特性：
- 配置外置：所有配置从数据库读取
- 多模型支持：Edge TTS / DashScope SDK
- 自动降级：主模型失败自动切换备模型
- 模型健康检查：执行前验证模型可用性

配置来源: symphony.db (tool_registry)
"""

import os
import sys
import json
import time
import sqlite3
import tempfile
import subprocess
import requests
from typing import Optional, Dict, Any, List

# 数据库路径
DB_PATH = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'


class VoiceModelConfig:
    """语音模型配置 - 支持多模型自动降级"""
    
    # 模型注册表（可扩展）
    MODELS = {
        'edge_tts': {
            'provider': 'edge',
            'voice_param': 'voice',
            'default_voice': 'zh-CN-XiaoxiaoNeural',
            'format': 'mp3',
            'synthesize_func': '_synthesize_edge_tts'
        },
        'dashscope_tts': {
            'provider': 'dashscope',
            'voice_param': 'model',
            'default_voice': 'sambert-zhinan-v1',
            'format': 'mp3',
            'synthesize_func': '_synthesize_dashscope'
        }
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """获取语音工具配置"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT config FROM tool_registry 
                WHERE tool_name = 'feishu_voice_v3' AND is_enabled = 1
            """)
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return json.loads(row[0])
        except Exception as e:
            print(f'[VoiceModel] 读取配置失败: {e}')
        
        return cls._default_config()
    
    @classmethod
    def _default_config(cls) -> Dict[str, Any]:
        """默认配置"""
        return {
            'version': 'v3',
            'provider': 'edge_tts',           # 主模型
            'fallback_provider': 'dashscope_tts',  # 备用模型
            'models': {
                'edge_tts': {
                    'enabled': True,
                    'voice': 'zh-CN-XiaoxiaoNeural',
                    'temp_dir': 'C:\\Users\\Administrator\\voice_tmp'
                },
                'dashscope_tts': {
                    'enabled': True,
                    'model': 'sambert-zhinan-v1',
                    'format': 'mp3',
                    'sample_rate': 24000,
                    'temp_dir': 'C:\\Users\\Administrator\\voice_tmp'
                }
            },
            'feishu': {
                'app_id': 'cli_a94c91048e781cd6',
                'app_secret': 'fm3Ey2RmbL75K523T0nZlcJDmCt67il1',
                'user_open_id': 'ou_698e215c481e88b814e628a92592eca5'
            },
            'max_retries': 2,  # 每个模型最多重试2次
            'timeout': 30
        }
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]) -> bool:
        """保存配置到数据库"""
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
                VALUES ('feishu_voice_v3', ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(tool_name) 
                DO UPDATE SET config = excluded.config, updated_at = CURRENT_TIMESTAMP
            """, (config_json,))
            
            conn.commit()
            conn.close()
            print('[VoiceModel] 配置已保存到 symphony.db')
            return True
        except Exception as e:
            print(f'[VoiceModel] 保存配置失败: {e}')
            return False


class AdaptiveVoiceSynthesizer:
    """
    自适应语音合成器
    - 支持多模型自动降级
    - 模型健康检查
    - 失败自动切换
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or VoiceModelConfig.get_config()
        self.current_provider = self.config['provider']
        self.fallback_provider = self.config['fallback_provider']
        self._token = None
        self._token_expire = 0
    
    def synthesize(self, text: str, voice: str = None) -> bytes:
        """
        自适应语音合成
        失败时自动降级到备用模型
        """
        errors = []
        
        # 尝试主模型
        try:
            return self._synthesize_with_provider(
                self.current_provider, text, voice
            )
        except Exception as e:
            errors.append(f'{self.current_provider}: {e}')
            print(f'[AdaptiveTTS] 主模型 {self.current_provider} 失败: {e}')
        
        # 尝试备用模型
        if self.fallback_provider:
            try:
                print(f'[AdaptiveTTS] 切换到备用模型: {self.fallback_provider}')
                return self._synthesize_with_provider(
                    self.fallback_provider, text, voice
                )
            except Exception as e:
                errors.append(f'{self.fallback_provider}: {e}')
                print(f'[AdaptiveTTS] 备用模型 {self.fallback_provider} 也失败: {e}')
        
        # 全部失败
        raise Exception(f'TTS 全部失败: {errors}')
    
    def _synthesize_with_provider(self, provider: str, text: str, voice: str = None) -> bytes:
        """使用指定模型合成"""
        model_info = self.config['models'].get(provider)
        if not model_info or not model_info.get('enabled'):
            raise Exception(f'模型 {provider} 未启用')
        
        if provider == 'edge_tts':
            return self._synthesize_edge_tts(
                text, voice or model_info.get('voice', 'zh-CN-XiaoxiaoNeural'),
                model_info['temp_dir']
            )
        elif provider == 'dashscope_tts':
            return self._synthesize_dashscope(
                text, voice or model_info.get('model', 'sambert-zhinan-v1'),
                model_info.get('sample_rate', 24000),
                model_info['temp_dir']
            )
        else:
            raise Exception(f'未知模型: {provider}')
    
    def _synthesize_edge_tts(self, text: str, voice: str, temp_dir: str) -> bytes:
        """Edge TTS 合成"""
        mp3_path = os.path.join(temp_dir, f'tts_{int(time.time() * 1000)}.mp3')
        
        edge_tts_path = r'C:\Users\Administrator\AppData\Roaming\npm\node_modules\node-edge-tts\bin.js'
        
        result = subprocess.run([
            'node', edge_tts_path,
            '-t', text,
            '-f', mp3_path,
            '-v', voice
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f'Edge TTS failed: {result.stderr}')
        
        with open(mp3_path, 'rb') as f:
            audio_data = f.read()
        
        os.unlink(mp3_path)
        return audio_data
    
    def _synthesize_dashscope(self, text: str, model: str, sample_rate: int, temp_dir: str) -> bytes:
        """DashScope SDK 合成"""
        try:
            from dashscope.audio.tts import SpeechSynthesizer
            
            result = SpeechSynthesizer.call(
                model=model,
                text=text,
                format='mp3',
                sample_rate=sample_rate
            )
            
            resp = result.get_response()
            if resp.status_code != 200:
                raise Exception(f'DashScope error: {resp.status_code} - {resp.message}')
            
            return result.get_audio_data()
            
        except ImportError:
            raise Exception('dashscope SDK 未安装')
        except Exception as e:
            raise Exception(f'DashScope failed: {e}')


class FeishuVoiceSender:
    """飞书语音气泡发送器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or VoiceModelConfig.get_config()
        self._token = None
        self._token_expire = 0
    
    def _get_token(self) -> str:
        """获取飞书 access token"""
        current_time = time.time()
        if self._token and current_time < self._token_expire:
            return self._token
        
        feishu_cfg = self.config['feishu']
        resp = requests.post(
            'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/',
            json={
                'app_id': feishu_cfg['app_id'],
                'app_secret': feishu_cfg['app_secret']
            },
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        if result.get('code') == 0:
            self._token = result['tenant_access_token']
            self._token_expire = current_time + result.get('expire', 7200) - 300
            return self._token
        else:
            raise Exception(f'获取 token 失败: {result.get("msg")}')
    
    def send_audio(self, receive_id: str, audio_data: bytes, duration_ms: int) -> Dict:
        """发送语音消息"""
        # 上传文件
        file_key = self._upload_file(audio_data, 'voice.opus', duration_ms)
        
        # 发送消息
        url = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id'
        resp = requests.post(
            url,
            headers={
                'Authorization': f'Bearer {self._get_token()}',
                'Content-Type': 'application/json'
            },
            json={
                'receive_id': receive_id,
                'msg_type': 'audio',
                'content': json.dumps({'file_key': file_key})
            },
            timeout=15
        )
        resp.raise_for_status()
        result = resp.json()
        
        if result.get('code') == 0:
            return {'success': True, 'message_id': result['data']['message_id']}
        else:
            raise Exception(f'发送失败: {result.get("msg")}')
    
    def _upload_file(self, audio_data: bytes, file_name: str, duration: int) -> str:
        """上传音频文件"""
        boundary = f'----FeishuBoundary{int(time.time() * 1000)}'
        
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
            audio_data,
            b'\r\n--' + boundary.encode() + b'--\r\n'
        ]
        body = b''.join(parts)
        
        resp = requests.post(
            'https://open.feishu.cn/open-apis/im/v1/files',
            headers={
                'Authorization': f'Bearer {self._get_token()}',
                'Content-Type': f'multipart/form-data; boundary={boundary}'
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


def convert_to_opus(mp3_data: bytes, temp_dir: str) -> tuple:
    """将 MP3 转换为 Opus 格式"""
    mp3_path = os.path.join(temp_dir, f'temp_{int(time.time() * 1000)}.mp3')
    opus_path = os.path.join(temp_dir, f'voice_{int(time.time() * 1000)}.opus')
    
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(mp3_path, 'wb') as f:
        f.write(mp3_data)
    
    try:
        # 获取时长
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', mp3_path
        ], capture_output=True, text=True, timeout=10)
        duration_ms = int(float(result.stdout.strip()) * 1000)
        
        # 转换格式
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


def send_voice_bubble(text: str, receive_id: str = None) -> Dict[str, Any]:
    """
    发送飞书语音气泡 - 自适应版本
    自动选择可用模型，失败时自动降级
    """
    config = VoiceModelConfig.get_config()
    receive_id = receive_id or config['feishu']['user_open_id']
    
    try:
        print(f'[VoiceBubble] 使用自适应合成器...')
        synthesizer = AdaptiveVoiceSynthesizer(config)
        
        print(f'[VoiceBubble] 合成语音: {text[:30]}...')
        mp3_data = synthesizer.synthesize(text)
        
        print(f'[VoiceBubble] 转换格式...')
        temp_dir = config['models'][config['provider']]['temp_dir']
        opus_data, duration = convert_to_opus(mp3_data, temp_dir)
        
        print(f'[VoiceBubble] 发送至 {receive_id}...')
        sender = FeishuVoiceSender(config)
        result = sender.send_audio(receive_id, opus_data, duration)
        
        if result['success']:
            print(f'[VoiceBubble] 发送成功! Message ID: {result["message_id"]}')
            return result
        else:
            return {'success': False, 'error': '发送失败'}
            
    except Exception as e:
        print(f'[VoiceBubble] 错误: {str(e)}')
        return {'success': False, 'error': str(e)}


def register_adaptive_voice_tool() -> bool:
    """注册自适应语音工具到 symphony.db"""
    config = VoiceModelConfig._default_config()
    return VoiceModelConfig.save_config(config)


if __name__ == '__main__':
    print('=== 序境系统 - 自适应语音气泡发送测试 ===')
    print('注册自适应语音工具...')
    register_adaptive_voice_tool()
    print('\n发送语音气泡（自动选择模型）...')
    result = send_voice_bubble('自适应语音合成测试，自动降级验证')
    print('结果:', result)
