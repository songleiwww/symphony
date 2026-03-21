# -*- coding: utf-8 -*-
"""
Xujing System - Term Mapper
Modern/Ancient term mapping
"""

# Term mapping
TERM_MAPPING = {
    'dispatch': {'ancient': 'order', 'office': 'shaofu'},
    'model': {'ancient': 'model', 'office': 'sili'},
    'api': {'ancient': 'relay', 'office': 'gongbu'},
    'test': {'ancient': 'verify', 'office': 'xingbu'},
    'delete': {'ancient': 'remove', 'office': 'libu'},
    'add': {'ancient': 'add', 'office': 'libu'},
    'update': {'ancient': 'revise', 'office': 'libu'},
    'query': {'ancient': 'check', 'office': 'hanlin'},
    'security': {'ancient': 'security', 'office': 'security'},
    'learn': {'ancient': 'study', 'office': 'qintian'},
}

PROVIDER_OFFICE = {
    'zhipu': 'sili',
    'volcengine': 'gongbu',
    'siliconflow': 'qintian',
    'nvidia': 'bingbu',
    'mofang': 'libu',
    'modao': 'zhongshu',
}

class TermMapper:
    @staticmethod
    def map_term(term):
        info = TERM_MAPPING.get(term, {'ancient': term, 'office': 'unknown'})
        return info
    
    @staticmethod
    def map_provider(provider):
        return PROVIDER_OFFICE.get(provider, 'unknown')

_mapper = TermMapper()

def map_term(term):
    return _mapper.map_term(term)

def map_provider(provider):
    return _mapper.map_provider(provider)
