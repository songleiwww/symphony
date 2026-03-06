#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
try:
    from openai import OpenAI

    client = OpenAI(
        base_url='https://integrate.api.nvidia.com/v1',
        api_key='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'
    )

    print('Testing NVIDIA DeepSeek-V3.2...', flush=True)
    
    completion = client.chat.completions.create(
        model='deepseek-ai/deepseek-v3.2',
        messages=[{'content': 'hi', 'role': 'user'}],
        max_tokens=100
    )

    print('Model: ' + completion.model, flush=True)
    content = completion.choices[0].message.content
    print('Response: ' + str(content), flush=True)
    print('SUCCESS', flush=True)
except Exception as e:
    print('ERROR: ' + str(e), flush=True)
    import traceback
    traceback.print_exc()
