# -*- coding: utf-8 -*-
import sys
import os
import importlib.util

# Change to project dir
os.chdir(r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')

# Load kernel
spec = importlib.util.spec_from_file_location('kernel_loader', 'Kernel/kernel_loader.py')
kl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kl)

kernel = kl.KernelLoader()
kernel.load_all()

print(f'Loaded: {len(kernel.roles)} roles')
print(f'Models: {len(kernel.models)}')

# Show roles
for role in kernel.roles:
    print(f'  {role.get("id")}: {role.get("官名")} - {role.get("模型名称")}')
