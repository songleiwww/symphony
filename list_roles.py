#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from kernel_loader import KernelLoader

loader = KernelLoader()
loader.load_all()

print('=== 少府监花名册 ===')
for role in loader.office_roles[:10]:
    print(role.get('id'), '-', role.get('姓名'), '-', role.get('官职'))
