# -*- coding: utf-8 -*-
import sys, os, importlib.util
os.chdir(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
spec = importlib.util.spec_from_file_location('kl', 'Kernel/kernel_loader.py')
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)
k = kl.get_kernel()
for r in k.roles:
    if r.get('id') == 'evolve_002':
        print('=== 陆念昭 述职报告 ===')
        print('ID:', r.get('id'))
        print('官名:', r.get('官名'))
        print('职位:', r.get('职位'))
        print('职能:', r.get('职能'))
        print('专长:', r.get('专长'))
        print('模型:', r.get('模型名称'))
        print('服务商:', r.get('模型服务商'))
        print('等级:', r.get('角色等级'))
