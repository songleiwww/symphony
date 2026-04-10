"""
序境内核 - 规则热更新引擎
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """规则类型"""
    SCHEDULING = "scheduling"
    MODEL_SELECTION = "model_selection"
    FALLBACK = "fallback"
    RATE_LIMIT = "rate_limit"


class RuleStatus(Enum):
    """规则状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"


@dataclass
class Rule:
    """调度规则"""
    rule_id: str
    name: str
    rule_type: RuleType
    condition: Callable[[Dict], bool]
    action: Callable[[Dict], Any]
    priority: int = 0
    status: RuleStatus = RuleStatus.ACTIVE
    enabled: bool = True
    version: int = 1
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class HotReloadRuleEngine:
    """热更新规则引擎"""
    
    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self._lock = threading.RLock()
        self._version = 0
        self._watchers: List[Callable] = []
    
    def add_rule(self, rule: Rule):
        """添加规则"""
        with self._lock:
            self.rules[rule.rule_id] = rule
            self._version += 1
            rule.updated_at = time.time()
            logger.info(f"添加规则: {rule.name} (v{rule.version})")
            
            # 通知观察者
            self._notify_watchers("add", rule)
    
    def update_rule(self, rule_id: str, new_rule: Rule):
        """更新规则 (热更新)"""
        with self._lock:
            if rule_id in self.rules:
                old_rule = self.rules[rule_id]
                new_rule.version = old_rule.version + 1
                new_rule.created_at = old_rule.created_at
                new_rule.updated_at = time.time()
                self.rules[rule_id] = new_rule
                self._version += 1
                
                logger.info(f"热更新规则: {rule_id} -> v{new_rule.version}")
                self._notify_watchers("update", new_rule)
            else:
                logger.warning(f"规则不存在: {rule_id}")
    
    def remove_rule(self, rule_id: str):
        """删除规则"""
        with self._lock:
            if rule_id in self.rules:
                rule = self.rules.pop(rule_id)
                self._version += 1
                logger.info(f"删除规则: {rule_id}")
                self._notify_watchers("remove", rule)
    
    def enable_rule(self, rule_id: str):
        """启用规则"""
        with self._lock:
            if rule_id in self.rules:
                self.rules[rule_id].enabled = True
                self.rules[rule_id].status = RuleStatus.ACTIVE
                self._version += 1
                logger.info(f"启用规则: {rule_id}")
    
    def disable_rule(self, rule_id: str):
        """禁用规则"""
        with self._lock:
            if rule_id in self.rules:
                self.rules[rule_id].enabled = False
                self.rules[rule_id].status = RuleStatus.INACTIVE
                self._version += 1
                logger.info(f"禁用规则: {rule_id}")
    
    def evaluate(self, context: Dict) -> Optional[Any]:
        """评估规则"""
        with self._lock:
            active_rules = [
                r for r in self.rules.values()
                if r.enabled and r.status == RuleStatus.ACTIVE
            ]
            active_rules.sort(key=lambda r: r.priority, reverse=True)
        
        for rule in active_rules:
            try:
                if rule.condition(context):
                    result = rule.action(context)
                    logger.debug(f"规则触发: {rule.name}")
                    return result
            except Exception as e:
                logger.error(f"规则执行失败: {rule.name}, 错误: {e}")
        
        return None
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """获取规则"""
        return self.rules.get(rule_id)
    
    def get_all_rules(self) -> List[Dict]:
        """获取所有规则"""
        return [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "type": r.rule_type.value,
                "status": r.status.value,
                "enabled": r.enabled,
                "priority": r.priority,
                "version": r.version
            }
            for r in self.rules.values()
        ]
    
    def add_watcher(self, watcher: Callable):
        """添加观察者"""
        self._watchers.append(watcher)
    
    def _notify_watchers(self, event: str, rule: Rule):
        """通知观察者"""
        for watcher in self._watchers:
            try:
                watcher(event, rule)
            except Exception as e:
                logger.error(f"观察者通知失败: {e}")
    
    def reload_from_config(self, config: List[Dict]):
        """从配置重载规则"""
        with self._lock:
            for cfg in config:
                rule_id = cfg.get("rule_id")
                if rule_id and rule_id in self.rules:
                    # 更新现有规则
                    self.update_rule(rule_id, self._build_rule(cfg))
                else:
                    # 添加新规则
                    self._build_rule(cfg)
    
    def _build_rule(self, cfg: Dict) -> Rule:
        """从配置构建规则"""
        return Rule(
            rule_id=cfg["rule_id"],
            name=cfg["name"],
            rule_type=RuleType(cfg.get("type", "scheduling")),
            condition=cfg.get("condition", lambda ctx: True),
            action=cfg.get("action", lambda ctx: ctx),
            priority=cfg.get("priority", 0),
            enabled=cfg.get("enabled", True)
        )
    
    def export_config(self) -> str:
        """导出配置"""
        config = self.get_all_rules()
        return json.dumps(config, indent=2, ensure_ascii=False)


# 全局热更新引擎
_engine: Optional[HotReloadRuleEngine] = None


def get_hot_engine() -> HotReloadRuleEngine:
    global _engine
    if _engine is None:
        _engine = HotReloadRuleEngine()
    return _engine
