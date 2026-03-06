#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实模型调用 - 输出到文件版本
调用真实模型并保存结果到JSON文件
"""

import sys
import io

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
import time
from datetime import datetime
from pathlib import Path

try:
    from real_model_caller import RealModelCaller, ModelCallResult
    REAL_MODEL_AVAILABLE = True
except ImportError:
    REAL_MODEL_AVAILABLE = False


def main():
    """主程序"""
    print("=" * 80)
    print("🤖 真实模型调用器 - 输出到文件")
    print("=" * 80)
    
    output_file = Path("real_call_result.json")
    
    if not REAL_MODEL_AVAILABLE:
        result = {
            "success": False,
            "error": "real_model_caller.py 未找到",
            "timestamp": datetime.now().isoformat()
        }
        output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"❌ 错误已保存到: {output_file}")
        return
    
    try:
        caller = RealModelCaller()
        
        prompt = "你好，请介绍一下你自己，用中文回答"
        
        print(f"\n📝 提示词: {prompt}")
        print("🔄 正在调用真实模型...")
        
        result = caller.call_model("ark-code-latest", prompt)
        
        output_data = {
            "success": result.success,
            "model_name": result.model_name,
            "model_alias": result.model_alias,
            "provider": result.provider,
            "prompt": result.prompt,
            "response": result.response,
            "error": result.error,
            "latency": result.latency,
            "timestamp": result.timestamp.isoformat() if result.timestamp else None,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "total_tokens": result.total_tokens
        }
        
        output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding='utf-8')
        
        print(f"\n✅ 调用成功!")
        print(f"   模型: {result.model_alias}")
        print(f"   延迟: {result.latency:.2f}秒")
        print(f"   Token: {result.prompt_tokens}+{result.completion_tokens}={result.total_tokens}")
        print(f"   结果已保存到: {output_file}")
        
        if result.response:
            print(f"\n📝 响应: {result.response[:200]}...")
        
    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"\n❌ 调用失败!")
        print(f"   错误: {e}")
        print(f"   错误已保存到: {output_file}")
    
    print("\n" + "=" * 80)
    print("完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
