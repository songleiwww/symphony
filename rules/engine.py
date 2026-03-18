"""
序境内核 - 规则引擎
"""

from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RuleType(Enum):
    SCHEDULING = "scheduling"


class RuleStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class Rule:
    rule_id: str
    name: str
    rule_type: RuleType
    condition: Callable[[Dict], bool]
    action: Callable[[Dict], Any]
    priority: int = 0
    status: RuleStatus = RuleStatus.ACTIVE
    enabled: bool = True


class RuleEngine:
    def __init__(self):
        self.rules: Dict[str, Rule] = {}
    
    def add_rule(self, rule: Rule):
        self.rules[rule.rule_id] = rule
        logger.info(f"添加规则: {rule.name}")
    
    def evaluate(self, context: Dict) -> Optional[Any]:
        active = [r for r in self.rules.values() if r.enabled and r.status == RuleStatus.ACTIVE]
        active.sort(key=lambda r: r.priority, reverse=True)
        for rule in active:
            try:
                if rule.condition(context):
                    return rule.action(context)
            except Exception as e:
                logger.error(f"规则执行失败: {rule.name}, {e}")
        return None


_engine: Optional[RuleEngine] = None


def get_rule_engine() -> RuleEngine:
    global _engine
    if _engine is None:
        _engine = RuleEngine()
    return _engine
