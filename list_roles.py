# -*- coding: utf-8 -*-
import sys, os, importlib.util
os.chdir(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
spec = importlib.util.spec_from_file_location('kl', 'Kernel/kernel_loader.py')
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)
k = kl.get_kernel()
print('可用官属:', len(k.roles))
for r in k.roles[:10]:
    print(f'  {r.get("id")}: 模型={r.get("模型名称")}, 服务商={r.get("模型服务商")}')
