# -*- coding: utf-8 -*-
"""
feishu - 飞书模块

导出:
- send_voice_bubble: 发送语音气泡（自适应版本，主入口）
- VoiceModelConfig: 语音模型配置（支持多模型自动降级）
- AdaptiveVoiceSynthesizer: 自适应语音合成器
"""

__all__ = [
    'send_voice_bubble',
    'VoiceModelConfig',
    'AdaptiveVoiceSynthesizer'
]

from .feishu_voice_adapter import (
    send_voice_bubble,
    VoiceModelConfig,
    AdaptiveVoiceSynthesizer
)
