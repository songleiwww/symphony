import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from brainstorm_panel_v2 import BrainstormPanel

panel = BrainstormPanel()
print('=' * 60)
print('Test: Symphony Single Model Call')

r1 = panel.call_model(prompt='用一句话介绍你自己', model_id='deepseek-ai/DeepSeek-R1-0528', max_tokens=200)
print(f'DeepSeek-R1: OK={r1.success} tokens={r1.tokens}')

r2 = panel.call_model(prompt='用一句话介绍你自己', model_id='glm-4-flash', max_tokens=200)
print(f'GLM-4-Flash: OK={r2.success} tokens={r2.tokens}')

r3 = panel.call_model(prompt='用一句话介绍你自己', model_id='deepseek-ai/DeepSeek-V3.2', max_tokens=200)
print(f'DeepSeek-V3.2: OK={r3.success} tokens={r3.tokens}')

total = sum(r.tokens for r in [r1, r2, r3] if r.success)
print(f'Total: {total} tokens')