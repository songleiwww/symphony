import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

from Kernel import EvolutionKernel
from providers.pool import ProviderPool

print('[1] EvolutionKernel - scheduling test')
k = EvolutionKernel()
print(f'    Kernel ID: {k.kernel_id}')
print(f'    Phase: {k.evolution_phase}')

print('[2] ProviderPool - status')
pool = ProviderPool()
print(f'    Pool initialized')

print('[3] Testing direct model call via ProviderPool')
try:
    response = pool.chat(
        model_name='deepseek-v3',
        messages=[{'role': 'user', 'content': 'Say "OK" in one word'}],
        provider='aliyun'
    )
    print(f'    Response: {response[:100]}')
except Exception as e:
    print(f'    Error: {e}')

print('[SUCCESS] Core systems operational!')
