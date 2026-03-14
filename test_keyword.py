# -*- coding: utf-8 -*-
import keyword_engine

k = keyword_engine.KeywordTrigger()
print('Test 1:', k.trigger_service('呼叫交响'))
print('Test 2:', k.trigger_service('我要开发'))
