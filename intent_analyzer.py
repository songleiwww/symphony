# -*- coding: utf-8 -*-
"""
Xujing System - Intent Analyzer
Strict intent matching, adaptive user habits
"""

# Intent keyword patterns
INTENT_PATTERNS = {
    'dispatch': ['dispatch', 'arrange', 'allocate', 'call', 'send', 'order'],
    'query': ['query', 'check', 'view', 'what', 'which', 'how many'],
    'add': ['add', 'create', 'new', 'establish', 'setup'],
    'delete': ['delete', 'remove', 'drop', 'cut'],
    'update': ['update', 'modify', 'change', 'revise'],
    'confirm': ['confirm', 'agree', 'approve', 'ok'],
    'learn': ['learn', 'study', 'research', 'prepare'],
    'security': ['security', 'check', 'inspect', 'audit'],
    'config': ['config', 'setup', 'setting'],
    'report': ['report', 'summary', 'review'],
}

class IntentAnalyzer:
    def __init__(self):
        self.user_habits = {
            'style': 'ancient',
            'formality': 'formal',
            'detail': 'concise',
        }
    
    def analyze_intent(self, text):
        text = text.lower()
        scores = {}
        for intent, patterns in INTENT_PATTERNS.items():
            score = 0
            for p in patterns:
                if p in text:
                    score += 1
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return 'unknown', 0
        
        intent = max(scores.items(), key=lambda x: x[1])
        return intent[0], intent[1]
    
    def analyze(self, text):
        intent, score = self.analyze_intent(text)
        return {
            'intent': intent,
            'confidence': score,
            'style': self.user_habits['style']
        }

_analyzer = IntentAnalyzer()

def analyze(text):
    return _analyzer.analyze(text)

def get_intent(text):
    return _analyzer.analyze_intent(text)
