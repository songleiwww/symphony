# -*- coding: utf-8 -*-
import sys
import importlib.util

# Load module from file
spec = importlib.util.spec_from_file_location("symphony", "symphony.py")
symphony = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(symphony)
    print('Module loaded OK')
    
    if hasattr(symphony, 'Symphony'):
        s = symphony.Symphony()
        print('Symphony class created:', type(s))
        print('Status:', s.get_status())
    else:
        print('No Symphony class found')
        print('Available:', [x for x in dir(symphony) if not x.startswith('_')])
except Exception as e:
    print('Error:', str(e))
    import traceback
    traceback.print_exc()
