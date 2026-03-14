# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from config import EMBEDDING_CONFIG, RERANK_CONFIG

print('='*60)
print('Vector Embedding Models')
print('='*60)
for name, cfg in EMBEDDING_CONFIG.items():
    print(name)
    print('  Provider:', cfg['provider'])
    print('  Model:', cfg['model'])
    print('  Dimension:', cfg['dimension'])
    print()

print('='*60)
print('Rerank Models')
print('='*60)
for name, cfg in RERANK_CONFIG.items():
    print(name)
    print('  Provider:', cfg['provider'])
    print('  Model:', cfg['model'])
    print('  Description:', cfg['description'])
    print()
