# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony')
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/Kernel')

from skills.takeover_skill import XujingTakeover
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

takeover = XujingTakeover()
response = takeover.get_xujing_response("我是用户，请和我对话")
print(response.get('content', ''))
