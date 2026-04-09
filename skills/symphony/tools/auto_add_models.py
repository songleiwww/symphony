# -*- coding: utf-8 -*-
# Auto-add all missing free models
import sys
sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
from model_registry import ModelRegistry

registry = ModelRegistry()
added, log = registry.add_all_missing()
print(f"Total added: {added}")
for msg in log:
    print(f"  {msg}")

