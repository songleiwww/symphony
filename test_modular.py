# -*- coding: utf-8 -*-
import symphony

print('Import OK')
try:
    s = symphony.Symphony()
    print('Symphony created:', type(s))
except Exception as e:
    print('Error:', str(e))
