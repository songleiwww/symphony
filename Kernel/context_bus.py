# -*- coding: utf-8 -*-
"""
上下文总线 - Context Bus
调度引擎阶段二实现

功能：
1. 全局上下文结构设计（根上下文 + 分片上下文）
2. 读写接口实现（子Agent只读所需分片）
3. Token预算控制
"""
import asyncio
import uuid
import time
import json
from typing import Any, Dict, List, Optional, Set, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import tiktoken


class ContextScope(Enum):
    """上下文分片范围"""
    GLOBAL = "global"       # 全局共享
    SESSION = "session"     # 会话级别
    TASK = "task"          # 任务级别
    AGENT = "agent"        # Agent私有
    SYSTEM = "system"      # 系统内部


class PermissionLevel(Enum):
    """访问权限级别"""
    READ_ONLY = "read_only"    # 只读
    READ_WRITE = "read_write"  # 读写
    ADMIN = "admin"            # 完全控制


@dataclass
class TokenBudget:
    """Token预算配置"""
    total_budget: int = 100000      # 总预算
    used_tokens: int = 0            # 已使用token
    remaining_tokens: int = 0       # 剩余token
    max_per_request: int = 4000     # 单次请求最大token
    warning_threshold: float = 0.8  # 警告阈值（比例）
    
    def __post_init__(self):
        if self.remaining_tokens == 0:
            self.remaining_tokens = self.total_budget
    
    def check_available(self, estimated_tokens: int) -> Tuple[bool, str]:
        """检查是否有足够token可用"""
        if estimated_tokens > self.max_per_request:
            return False, f"预估token {estimated_tokens} 超过单次请求上限 {self.max_per_request}"
        
        if estimated_tokens > self.remaining_tokens:
            return False, f"预估token {estimated_tokens} 超过剩余预算 {self.remaining_tokens}"
        
        return True, ""
    
    def consume(self, tokens: int) -> float:
        """消耗token，返回使用比例"""
        self.used_tokens += tokens
        self.remaining_tokens = max(0, self.total_budget - self.used_tokens)
        return self.usage_ratio()
    
    def usage_ratio(self) -> float:
        """返回使用比例"""
        if self.total_budget == 0:
            return 1.0
        return self.used_tokens / self.total_budget
    
    def should_warn(self) -> bool:
        """是否应该发出警告"""
        return self.usage_ratio() >= self.warning_threshold
    
    def reset(self):
        """重置预算"""
        self.used_tokens = 0
        self.remaining_tokens = self.total_budget
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ContextShard:
    """上下文分片"""
    id: str
    name: str
    scope: ContextScope
    owner_id: str                   # 所有者ID（session/task/agent ID）
    data: Dict[str, Any] = field(default_factory=dict)
    permission: Dict[str, PermissionLevel] = field(default_factory=dict)  # agent_id -> level
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    token_count: int = 0            # 当前分片估算token数
    
    def estimate_token_count(self) -> int:
        """估算分片数据的token数"""
        try:
            # 使用tiktoken估算
            content = json.dumps(self.data, ensure_ascii=False)
            encoding = tiktoken.get_encoding("cl100k_base")
            self.token_count = len(encoding.encode(content))
        except Exception:
            # 降级估算：约4字符一个token
            content = json.dumps(self.data, ensure_ascii=False)
            self.token_count = len(content) // 4
        return self.token_count
    
    def check_permission(self, agent_id: str, write: bool = False) -> bool:
        """检查Agent是否有访问权限"""
        # 所有者拥有全部权限
        if agent_id == self.owner_id:
            return True
        
        # 检查权限配置
        level = self.permission.get(agent_id, PermissionLevel.READ_ONLY)
        if not write:
            # 读操作：只读及以上都可以
            return True
        else:
            # 写操作：需要读写或admin
            return level in [PermissionLevel.READ_WRITE, PermissionLevel.ADMIN]
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "scope": self.scope.value,
            "owner_id": self.owner_id,
            "token_count": self.token_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class RootContext:
    """根上下文 - 全局顶级上下文"""
    session_id: str
    root_budget: TokenBudget = field(default_factory=TokenBudget)
    shards: Dict[str, ContextShard] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_total_token_usage(self) -> int:
        """获取所有分片总token使用"""
        return sum(shard.token_count for shard in self.shards.values())


class ContextBus:
    """
    上下文总线 - 全局上下文管理中心
    
    架构：
    - 根上下文(RootContext)：每个会话一个根，包含全局Token预算
    - 上下文分片(ContextShard)：按scope/owner分片存储，支持权限控制
    - 读写接口：子Agent只能访问授权的分片
    - Token预算：根级别和分片级别都支持预算控制
    """
    
    def __init__(self):
        self._root_contexts: Dict[str, RootContext] = {}
        self._shard_index: Dict[str, Set[str]] = defaultdict(set)  # owner_id -> shard_ids
        self._token_encoding = None
        self._initialize_tokenizer()
        
        # 回调
        self.on_budget_exceeded: Optional[Callable[[str, TokenBudget], None]] = None
        self.on_budget_warning: Optional[Callable[[str, TokenBudget], None]] = None
        
        print("[ContextBus] 上下文总线初始化完成")
    
    def _initialize_tokenizer(self):
        """初始化token分词器"""
        try:
            self._token_encoding = tiktoken.get_encoding("cl100k_base")
            print("[ContextBus] Token分词器加载成功")
        except Exception as e:
            print(f"[ContextBus] Token分词器加载失败，使用降级估算: {e}")
    
    def estimate_tokens(self, text: str) -> int:
        """估算文本token数"""
        if self._token_encoding:
            try:
                return len(self._token_encoding.encode(text))
            except Exception:
                pass
        # 降级估算：中文字符1个token/字，英文4字符1个token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return chinese_chars + (other_chars + 3) // 4
    
    def create_root_context(
        self,
        session_id: str = None,
        total_budget: int = 100000,
        max_per_request: int = 4000
    ) -> RootContext:
        """
        创建根上下文
        
        参数:
            session_id: 会话ID，不指定则自动生成
            total_budget: 全局总token预算
            max_per_request: 单次请求最大token
        
        返回:
            根上下文对象
        """
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
        
        budget = TokenBudget(
            total_budget=total_budget,
            max_per_request=max_per_request
        )
        
        root = RootContext(
            session_id=session_id,
            root_budget=budget
        )
        
        self._root_contexts[session_id] = root
        
        # 创建全局分片
        self.create_shard(
            session_id=session_id,
            name="global_system",
            scope=ContextScope.GLOBAL,
            owner_id=session_id,
            data={"system_info": {"created_at": time.time()}},
            permissions={}
        )
        
        print(f"[ContextBus] 根上下文创建: {session_id}, 总预算: {total_budget} tokens")
        return root
    
    def create_shard(
        self,
        session_id: str,
        name: str,
        scope: ContextScope,
        owner_id: str,
        data: Dict[str, Any] = None,
        permissions: Dict[str, PermissionLevel] = None
    ) -> ContextShard:
        """
        创建上下文分片
        
        参数:
            session_id: 所属会话ID
            name: 分片名称
            scope: 分片范围
            owner_id: 所有者ID
            data: 初始数据
            permissions: 权限配置 {agent_id: level}
        
        返回:
            分片对象
        """
        if session_id not in self._root_contexts:
            raise ValueError(f"根上下文不存在: {session_id}")
        
        root = self._root_contexts[session_id]
        
        shard_id = f"{session_id}_{owner_id}_{str(uuid.uuid4())[:4]}"
        
        shard = ContextShard(
            id=shard_id,
            name=name,
            scope=scope,
            owner_id=owner_id,
            data=data or {},
            permission=permissions or {}
        )
        
        # 估算token
        shard.estimate_token_count()
        
        # 检查全局预算
        if shard.token_count > 0:
            self._consume_tokens(root, shard.token_count)
        
        # 存储分片
        root.shards[shard_id] = shard
        self._shard_index[owner_id].add(shard_id)
        
        print(f"[ContextBus] 分片创建: {shard_id} ({name}), token: {shard.token_count}")
        return shard
    
    def _consume_tokens(self, root: RootContext, tokens: int) -> bool:
        """消耗全局token预算"""
        ok, msg = root.root_budget.check_available(tokens)
        if not ok:
            if self.on_budget_exceeded:
                self.on_budget_exceeded(root.session_id, root.root_budget)
            print(f"[ContextBus] 预算不足: {msg}")
            return False
        
        ratio = root.root_budget.consume(tokens)
        
        # 检查是否需要警告
        if root.root_budget.should_warn() and self.on_budget_warning:
            self.on_budget_warning(root.session_id, root.root_budget)
            print(f"[ContextBus] 预算警告: 使用比例 {ratio:.1%}")
        
        return True
    
    def get_shard(
        self,
        session_id: str,
        shard_id: str,
        agent_id: str,
        write: bool = False
    ) -> Optional[ContextShard]:
        """
        获取分片（带权限检查）
        
        参数:
            session_id: 会话ID
            shard_id: 分片ID
            agent_id: 请求的Agent ID
            write: 是否写操作
        
        返回:
            分片对象，无权限或不存在返回None
        """
        if session_id not in self._root_contexts:
            return None
        
        root = self._root_contexts[session_id]
        shard = root.shards.get(shard_id)
        
        if not shard:
            return None
        
        if not shard.check_permission(agent_id, write):
            print(f"[ContextBus] 权限拒绝: {agent_id} -> {shard_id} (write={write})")
            return None
        
        return shard
    
    def get_shards_by_owner(
        self,
        session_id: str,
        owner_id: str,
        agent_id: str
    ) -> List[ContextShard]:
        """获取所有者的所有分片（带权限过滤）"""
        if session_id not in self._root_contexts:
            return []
        
        root = self._root_contexts[session_id]
        shard_ids = self._shard_index.get(owner_id, set())
        
        result = []
        for shard_id in shard_ids:
            shard = root.shards.get(shard_id)
            if shard and shard.check_permission(agent_id, False):
                result.append(shard)
        
        return result
    
    def get_accessible_shards(
        self,
        session_id: str,
        agent_id: str
    ) -> List[ContextShard]:
        """获取Agent可访问的所有分片"""
        if session_id not in self._root_contexts:
            return []
        
        root = self._root_contexts[session_id]
        result = []
        
        for shard in root.shards.values():
            if shard.check_permission(agent_id, False):
                result.append(shard)
        
        return result
    
    def read(
        self,
        session_id: str,
        shard_id: str,
        agent_id: str,
        key: str = None
    ) -> Any:
        """
        读取分片数据
        
        参数:
            session_id: 会话ID
            shard_id: 分片ID
            agent_id: 请求Agent ID
            key: 数据键，不指定则返回整个分片数据
        
        返回:
            数据值，无权限/不存在返回None
        """
        shard = self.get_shard(session_id, shard_id, agent_id, write=False)
        if not shard:
            return None
        
        if key is None:
            return shard.data.copy()
        
        return shard.data.get(key)
    
    def write(
        self,
        session_id: str,
        shard_id: str,
        agent_id: str,
        key: str,
        value: Any,
        estimate_tokens: int = None
    ) -> bool:
        """
        写入分片数据
        
        参数:
            session_id: 会话ID
            shard_id: 分片ID
            agent_id: 请求Agent ID
            key: 数据键
            value: 数据值
            estimate_tokens: 预估值token，不指定则自动估算
        
        返回:
            是否写入成功（权限不足或token不够返回False）
        """
        if session_id not in self._root_contexts:
            return False
        
        root = self._root_contexts[session_id]
        shard = self.get_shard(session_id, shard_id, agent_id, write=True)
        
        if not shard:
            return False
        
        # 计算新增token
        old_token = shard.token_count
        
        # 更新数据
        shard.data[key] = value
        shard.updated_at = time.time()
        new_token = shard.estimate_token_count()
        
        token_delta = new_token - old_token
        
        if token_delta > 0:
            if not self._consume_tokens(root, token_delta):
                # token不够，回滚
                del shard.data[key]
                shard.token_count = old_token
                return False
        
        print(f"[ContextBus] 写入成功: {shard_id}.{key}, +{token_delta} tokens")
        return True
    
    def delete(
        self,
        session_id: str,
        shard_id: str,
        agent_id: str
    ) -> bool:
        """
        删除分片
        
        参数:
            session_id: 会话ID
            shard_id: 分片ID
            agent_id: 请求Agent ID
        
        返回:
            是否删除成功
        """
        if session_id not in self._root_contexts:
            return False
        
        root = self._root_contexts[session_id]
        shard = self.get_shard(session_id, shard_id, agent_id, write=True)
        
        if not shard:
            return False
        
        # 回收token
        if shard.token_count > 0:
            # 增加回剩余预算
            root.root_budget.used_tokens = max(0, root.root_budget.used_tokens - shard.token_count)
            root.root_budget.remaining_tokens += shard.token_count
        
        # 删除分片
        del root.shards[shard_id]
        if shard.owner_id in self._shard_index:
            self._shard_index[shard.owner_id].discard(shard_id)
        
        print(f"[ContextBus] 分片删除: {shard_id}")
        return True
    
    def check_budget(
        self,
        session_id: str,
        estimated_tokens: int
    ) -> Tuple[bool, str]:
        """
        检查预算是否足够
        
        参数:
            session_id: 会话ID
            estimated_tokens: 预估需要的token
        
        返回:
            (是否足够, 错误信息)
        """
        if session_id not in self._root_contexts:
            return False, f"根上下文不存在: {session_id}"
        
        root = self._root_contexts[session_id]
        return root.root_budget.check_available(estimated_tokens)
    
    def get_budget_status(self, session_id: str) -> Optional[Dict]:
        """获取预算状态"""
        if session_id not in self._root_contexts:
            return None
        
        root = self._root_contexts[session_id]
        budget = root.root_budget
        
        return {
            "total": budget.total_budget,
            "used": budget.used_tokens,
            "remaining": budget.remaining_tokens,
            "usage_ratio": budget.usage_ratio(),
            "warning": budget.should_warn(),
            "max_per_request": budget.max_per_request
        }
    
    def get_context_summary(self, session_id: str, agent_id: str) -> Dict:
        """
        获取Agent可见的上下文摘要
        
        参数:
            session_id: 会话ID
            agent_id: Agent ID
        
        返回:
            摘要信息
        """
        if session_id not in self._root_contexts:
            return {"error": "session not found"}
        
        root = self._root_contexts[session_id]
        accessible = self.get_accessible_shards(session_id, agent_id)
        
        total_tokens = sum(s.token_count for s in accessible)
        
        return {
            "session_id": session_id,
            "accessible_shards": len(accessible),
            "total_shards": len(root.shards),
            "total_tokens_accessible": total_tokens,
            "global_budget": self.get_budget_status(session_id),
            "shards": [s.to_dict() for s in accessible]
        }
    
    def merge_context_for_agent(
        self,
        session_id: str,
        agent_id: str,
        include_scopes: List[ContextScope] = None
    ) -> Dict[str, Any]:
        """
        合并Agent可访问的所有上下文到一个字典
        
        参数:
            session_id: 会话ID
            agent_id: Agent ID
            include_scopes: 只包含指定范围，None表示所有
        
        返回:
            合并后的上下文
        """
        accessible = self.get_accessible_shards(session_id, agent_id)
        
        result = {
            "_meta": {
                "agent_id": agent_id,
                "session_id": session_id,
                "merged_at": time.time()
            }
        }
        
        for shard in accessible:
            if include_scopes and shard.scope not in include_scopes:
                continue
            
            result[shard.name] = shard.data.copy()
        
        return result
    
    def delete_root_context(self, session_id: str) -> bool:
        """删除整个根上下文（会话结束）"""
        if session_id not in self._root_contexts:
            return False
        
        root = self._root_contexts[session_id]
        
        # 清理分片索引
        for shard_id in root.shards:
            shard = root.shards[shard_id]
            if shard.owner_id in self._shard_index:
                self._shard_index[shard.owner_id].discard(shard_id)
        
        del self._root_contexts[session_id]
        print(f"[ContextBus] 根上下文删除: {session_id}")
        return True
    
    def list_sessions(self) -> List[str]:
        """列出所有活跃会话"""
        return list(self._root_contexts.keys())
    
    def statistics(self) -> Dict:
        """获取全局统计"""
        total_sessions = len(self._root_contexts)
        total_shards = sum(len(root.shards) for root in self._root_contexts.values())
        total_tokens = sum(
            root.root_budget.used_tokens
            for root in self._root_contexts.values()
        )
        total_budget = sum(
            root.root_budget.total_budget
            for root in self._root_contexts.values()
        )
        
        return {
            "active_sessions": total_sessions,
            "total_shards": total_shards,
            "total_tokens_used": total_tokens,
            "total_budget_allocated": total_budget,
            "overall_usage_ratio": total_tokens / total_budget if total_budget > 0 else 0
        }


# ============== 便捷封装 ==============

class ContextBusAgentInterface:
    """
    面向Agent的上下文接口
    子Agent只需要通过这个接口访问上下文，遵循只读原则
    """
    
    def __init__(self, context_bus: ContextBus, session_id: str, agent_id: str):
        self._context_bus = context_bus
        self._session_id = session_id
        self._agent_id = agent_id
    
    def read_global(self, key: str = None) -> Any:
        """读取全局分片数据"""
        # 找到全局分片
        summary = self._context_bus.get_context_summary(self._session_id, self._agent_id)
        if "shards" not in summary:
            return None
        
        global_shard = None
        for shard_info in summary["shards"]:
            if shard_info["name"] == "global_system":
                global_shard = self._context_bus.get_shard(
                    self._session_id,
                    shard_info["id"],
                    self._agent_id,
                    write=False
                )
                break
        
        if not global_shard:
            return None
        
        if key is None:
            return global_shard.data.copy()
        
        return global_shard.data.get(key)
    
    def read_my_context(self) -> Dict[str, Any]:
        """读取Agent自己的所有分片数据（合并）"""
        return self._context_bus.merge_context_for_agent(
            self._session_id,
            self._agent_id
        )
    
    def read_shard(self, shard_id: str, key: str = None) -> Any:
        """读取指定分片"""
        return self._context_bus.read(
            self._session_id,
            shard_id,
            self._agent_id,
            key
        )
    
    def list_accessible(self) -> Dict:
        """列出可访问的分片"""
        return self._context_bus.get_context_summary(
            self._session_id,
            self._agent_id
        )
    
    def check_budget(self, estimated_tokens: int) -> Tuple[bool, str]:
        """检查预算"""
        return self._context_bus.check_budget(
            self._session_id,
            estimated_tokens
        )
    
    def get_budget_status(self) -> Optional[Dict]:
        """获取预算状态"""
        return self._context_bus.get_budget_status(self._session_id)
    
    def write_my_context(
        self,
        name: str,
        key: str,
        value: Any,
        session_id: str = None
    ) -> bool:
        """
        在自己的所有者下写入数据
        如果分片不存在会自动创建
        """
        # 查找是否已有此名称的分片
        summary = self._context_bus.get_context_summary(
            self._session_id,
            self._agent_id
        )
        
        target_shard = None
        for shard_info in summary.get("shards", []):
            if shard_info["name"] == name and shard_info["owner_id"] == self._agent_id:
                target_shard = self._context_bus.get_shard(
                    self._session_id,
                    shard_info["id"],
                    self._agent_id,
                    write=True
                )
                break
        
        if not target_shard:
            # 创建新分片
            target_shard = self._context_bus.create_shard(
                session_id=self._session_id,
                name=name,
                scope=ContextScope.AGENT,
                owner_id=self._agent_id,
                data={key: value},
                permissions={self._agent_id: PermissionLevel.READ_WRITE}
            )
            return True
        else:
            # 写入现有分片
            return self._context_bus.write(
                self._session_id,
                target_shard.id,
                self._agent_id,
                key,
                value
            )


# ============== 测试 ==============
if __name__ == "__main__":
    print("=== 上下文总线 测试 ===\n")
    
    # 1. 创建上下文总线
    bus = ContextBus()
    
    # 2. 创建根上下文（会话）
    root = bus.create_root_context(
        session_id="test_session_001",
        total_budget=10000,
        max_per_request=2000
    )
    
    print(f"根上下文创建: {root.session_id}")
    print(f"初始预算: {root.root_budget.to_dict()}")
    print()
    
    # 3. 创建不同分片
    # 任务分片
    task_shard = bus.create_shard(
        session_id="test_session_001",
        name="task_implementation",
        scope=ContextScope.TASK,
        owner_id="task_001",
        data={
            "task_name": "开发上下文总线",
            "requirements": ["设计结构", "实现接口", "token控制"],
            "progress": 0
        },
        permissions={
            "agent_suyunmiao": PermissionLevel.READ_WRITE,
            "agent_lunianzhao": PermissionLevel.READ_ONLY
        }
    )
    
    # Agent 私有分片
    agent1_shard = bus.create_shard(
        session_id="test_session_001",
        name="suyunmiao_private",
        scope=ContextScope.AGENT,
        owner_id="agent_suyunmiao",
        data={
            "notes": "苏云渺的开发笔记",
            "completed_steps": ["结构设计"]
        }
    )
    
    print()
    
    # 4. 测试权限控制
    print("--- 权限测试 ---")
    
    # 苏云渺（读写权限）读取任务分片
    data = bus.read("test_session_001", task_shard.id, "agent_suyunmiao")
    print(f"[agent_suyunmiao] 读取任务分片: {data is not None}")
    if data:
        print(f"  任务名称: {data.get('task_name')}")
    
    # 陆念昭（只读）尝试写入
    write_ok = bus.write(
        "test_session_001",
        task_shard.id,
        "agent_lunianzhao",
        "progress",
        100
    )
    print(f"[agent_lunianzhao] 写入任务分片（应该失败）: {write_ok}")
    
    # 苏云渺写入
    write_ok = bus.write(
        "test_session_001",
        task_shard.id,
        "agent_suyunmiao",
        "progress",
        50
    )
    print(f"[agent_suyunmiao] 写入进度: {write_ok}")
    
    progress = bus.read("test_session_001", task_shard.id, "agent_suyunmiao", "progress")
    print(f"  更新后进度: {progress}")
    
    print()
    
    # 5. 测试Token预算
    print("--- Token预算测试 ---")
    status = bus.get_budget_status("test_session_001")
    print(f"当前预算状态:")
    print(f"  总预算: {status['total']}")
    print(f"  已使用: {status['used']}")
    print(f"  剩余: {status['remaining']}")
    print(f"  使用比例: {status['usage_ratio']:.1%}")
    
    print()
    
    # 6. 测试Agent接口
    print("--- Agent接口测试 ---")
    agent_if = ContextBusAgentInterface(bus, "test_session_001", "agent_suyunmiao")
    
    # 写入自己的上下文
    ok = agent_if.write_my_context("development_notes", "today_progress", "完成了上下文总线核心接口")
    print(f"写入自己上下文: {ok}")
    
    # 读取可访问分片
    summary = agent_if.list_accessible()
    print(f"可访问分片数: {summary['accessible_shards']}")
    print(f"总token: {summary['total_tokens_accessible']}")
    
    print()
    
    # 7. 合并上下文
    print("--- 合并上下文测试 ---")
    merged = agent_if.read_my_context()
    print(f"合并后keys: {list(merged.keys())}")
    
    print()
    
    # 8. 全局统计
    print("--- 全局统计 ---")
    stats = bus.statistics()
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.1%}")
        else:
            print(f"  {k}: {v}")
    
    print()
    print("=== 测试完成 ===")
    print("上下文总线阶段二开发完成！")
