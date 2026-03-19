# -*- coding: utf-8 -*-
import os

# 读取原文件
file_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\Kernel\kernel_integration.py'

# 读取所有行
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 "return 进化完成" 之后的位置
# 查找包含 "return 进化完成" 的行
for i, line in enumerate(lines):
    if 'return "进化完成"' in line or "return '进化完成'" in line:
        # 找到这一行，保留它之前的所有内容 + 这一行
        new_lines = lines[:i+1]
        break
else:
    # 如果没找到，保留前271行
    new_lines = lines[:271]

# 要添加的预处理函数代码
preprocess_code = '''

# ============================================================================
# 消息预处理 - 集成接管检测
# ============================================================================

def preprocess_message(user_message: str, context: dict = None) -> dict:
    """
    消息预处理函数 - 在处理消息前先检查是否需要接管
    """
    try:
        from dialog_takeover import intercept_message, get_dialog_handler
        
        takeover_result = intercept_message(user_message, context)
        
        if takeover_result.get('taken_over'):
            handler = get_dialog_handler()
            signed_response = handler.add_takeover_signature(takeover_result.get('response', ''))
            takeover_result['response'] = signed_response
            
            return {
                'should_takeover': True,
                'takeover_result': takeover_result,
                'original_result': None
            }
        else:
            return {
                'should_takeover': False,
                'takeover_result': None,
                'original_result': None
            }
    except Exception as e:
        print(f'[预处理] 接管检测失败: {e}')
        return {
            'should_takeover': False,
            'takeover_result': None,
            'original_result': None
        }


def process_with_takeover(user_message: str, context: dict = None, normal_handler=None):
    """
    带接管检测的消息处理函数
    """
    preprocess_result = preprocess_message(user_message, context)
    
    if preprocess_result['should_takeover']:
        return preprocess_result['takeover_result']
    else:
        if normal_handler:
            return normal_handler(user_message, context)
        return None
'''

# 组合新内容
new_content = ''.join(new_lines) + preprocess_code

# 写入文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done")
