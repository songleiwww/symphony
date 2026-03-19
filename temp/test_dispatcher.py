# -*- coding: utf-8 -*-
import sys
import os
import sqlite3

db_path = r'C:\Users\Administrator\.openclaw\workspace\skills\symphony\data\symphony.db'

print('=== Test: XujingDispatcher ===')

# Test dispatcher
try:
    sys.path.insert(0, r'C:\Users\Administrator\.openclaw\workspace\skills\symphony')
    from dispatcher import XujingDispatcher
    dispatcher = XujingDispatcher(db_path)
    print('1. Dispatcher init: OK')
    
    # Check experts
    print('2. Experts loaded:', len(dispatcher.experts))
    for cat, exps in dispatcher.experts.items():
        print(f'   {cat}: {len(exps)} models')
        for e in exps[:2]:
            print(f'      - {e["model"]}')
    
    # Test select_expert
    expert = dispatcher.select_expert('逻辑推理')
    print('3. Select expert (logic):', expert['model'] if expert else 'None')
    
    expert = dispatcher.select_expert('代码生成')
    print('4. Select expert (code):', expert['model'] if expert else 'None')
    
    # Test dispatch
    result = dispatcher.dispatch('Hello, how are you?')
    print('5. Dispatch result keys:', list(result.keys()) if isinstance(result, dict) else 'error')
    
except Exception as e:
    print('Error:', str(e)[:300])
    import traceback
    traceback.print_exc()
