#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
序境3.0 生命周期状态机
======================
少府监·枢密使 沈清弦 主持开发

实现单元生命周期管理：加载→校验→实例化→激活→挂起→卸载
"""

import logging
import time
from enum import Enum
from typing import Dict, Optional, Any, Callable, List
from dataclasses import dataclass, field
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("序境3.0.生命周期管理器")


class UnitState(Enum):
    """单元生命周期状态枚举"""
    UNLOADED = "未加载"      # 初始状态，单元未被加载
    LOADING = "加载中"       # 正在加载单元资源
    VALIDATING = "校验中"    # 正在校验单元完整性
    INSTANTIATED = "已实例化" # 单元已创建实例
    ACTIVE = "已激活"        # 单元处于活跃运行状态
    SUSPENDED = "已挂起"     # 单元被挂起暂停
    UNLOADING = "卸载中"     # 正在卸载单元
    ERROR = "错误"           # 单元处于错误状态


class LifecycleEvent(Enum):
    """生命周期事件枚举"""
    LOAD = "加载"
    VALIDATE = "校验"
    INSTANTIATE = "实例化"
    ACTIVATE = "激活"
    SUSPEND = "挂起"
    RESUME = "恢复"
    UNLOAD = "卸载"
    RESET = "重置"


# 定义状态转换映射表
VALID_TRANSITIONS: Dict[UnitState, List[UnitState]] = {
    UnitState.UNLOADED:   [UnitState.LOADING],
    UnitState.LOADING:    [UnitState.VALIDATING, UnitState.ERROR, UnitState.UNLOADED],
    UnitState.VALIDATING: [UnitState.INSTANTIATED, UnitState.ERROR, UnitState.UNLOADED],
    UnitState.INSTANTIATED: [UnitState.ACTIVE, UnitState.UNLOADING, UnitState.ERROR],
    UnitState.ACTIVE:     [UnitState.SUSPENDED, UnitState.UNLOADING, UnitState.ERROR],
    UnitState.SUSPENDED:  [UnitState.ACTIVE, UnitState.UNLOADING, UnitState.ERROR],
    UnitState.UNLOADING:  [UnitState.UNLOADED],
    UnitState.ERROR:      [UnitState.UNLOADING, UnitState.LOADING],  # 可重试或直接卸载
}


@dataclass
class UnitMetadata:
    """单元元数据"""
    unit_id: str
    unit_name: str
    version: str
    loaded_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    instantiated_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    suspended_at: Optional[datetime] = None
    unloaded_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class LifecycleResult:
    """生命周期操作结果"""
    success: bool
    message: str
    new_state: Optional[UnitState] = None
    data: Optional[Dict[str, Any]] = None


class LifecycleManager:
    """
    生命周期管理器
    =============
    负责管理序境单元的完整生命周期
    
    状态流转: UNLOADED → LOADING → VALIDATING → INSTANTIATED → ACTIVE ↔ SUSPENDED → UNLOADING → UNLOADED
    
    示例:
        manager = LifecycleManager()
        result = manager.load_unit("unit_001")
        result = manager.validate_unit("unit_001")
        result = manager.instantiate_unit("unit_001")
        result = manager.activate_unit("unit_001")
    """
    
    def __init__(self, max_retries: int = 3):
        """
        初始化生命周期管理器
        
        Args:
            max_retries: 最大重试次数
        """
        self._units: Dict[str, UnitMetadata] = {}
        self._unit_instances: Dict[str, Any] = {}
        self._state_listeners: Dict[UnitState, List[Callable]] = {
            state: [] for state in UnitState
        }
        self._event_hooks: Dict[LifecycleEvent, List[Callable]] = {
            event: [] for event in LifecycleEvent
        }
        self._max_retries = max_retries
        logger.info("🌀 序境3.0生命周期管理器初始化完成")
    
    # ==================== 核心状态管理 ====================
    
    def get_unit_state(self, unit_id: str) -> Optional[UnitState]:
        """获取单元当前状态"""
        if unit_id not in self._units:
            return None
        
        # 根据元数据时间戳推断当前状态
        meta = self._units[unit_id]
        
        if meta.unloaded_at:
            return UnitState.UNLOADED
        if meta.error_message:
            return UnitState.ERROR
        if meta.suspended_at:
            return UnitState.SUSPENDED
        if meta.activated_at:
            return UnitState.ACTIVE
        if meta.instantiated_at:
            return UnitState.INSTANTIATED
        if meta.validated_at:
            return UnitState.VALIDATING
        if meta.loaded_at:
            return UnitState.LOADING
        
        return UnitState.UNLOADED
    
    def _can_transition(self, from_state: UnitState, to_state: UnitState) -> bool:
        """检查状态转换是否合法"""
        if from_state not in VALID_TRANSITIONS:
            return False
        return to_state in VALID_TRANSITIONS[from_state]
    
    def _transition_to(self, unit_id: str, new_state: UnitState, 
                       metadata_update: Optional[Dict[str, Any]] = None) -> bool:
        """
        执行状态转换
        
        Args:
            unit_id: 单元ID
            new_state: 目标状态
            metadata_update: 元数据更新
            
        Returns:
            转换是否成功
        """
        current_state = self.get_unit_state(unit_id)
        
        if not self._can_transition(current_state, new_state):
            logger.warning(f"⚠️ 单元 {unit_id}: 状态转换非法 {current_state.value} → {new_state.value}")
            return False
        
        # 更新元数据
        if unit_id in self._units:
            meta = self._units[unit_id]
            now = datetime.now()
            
            if new_state == UnitState.LOADING:
                meta.loaded_at = now
            elif new_state == UnitState.VALIDATING:
                meta.validated_at = now
            elif new_state == UnitState.INSTANTIATED:
                meta.instantiated_at = now
            elif new_state == UnitState.ACTIVE:
                meta.activated_at = now
                meta.suspended_at = None  # 恢复时清除挂起时间
            elif new_state == UnitState.SUSPENDED:
                meta.suspended_at = now
            elif new_state == UnitState.UNLOADING or new_state == UnitState.UNLOADED:
                meta.unloaded_at = now
            
            if metadata_update:
                for key, value in metadata_update.items():
                    setattr(meta, key, value)
        
        # 触发状态监听器
        self._notify_state_change(unit_id, new_state)
        
        logger.info(f"✓ 单元 {unit_id}: 状态转换 {current_state.value if current_state else 'N/A'} → {new_state.value}")
        return True
    
    def _notify_state_change(self, unit_id: str, new_state: UnitState):
        """触发状态变更通知"""
        listeners = self._state_listeners.get(new_state, [])
        for listener in listeners:
            try:
                listener(unit_id, new_state)
            except Exception as e:
                logger.error(f"状态监听器执行失败: {e}")
    
    # ==================== 生命周期阶段实现 ====================
    
    def load(self, unit_id: str, unit_name: str, version: str = "1.0.0",
             load_handler: Optional[Callable] = None) -> LifecycleResult:
        """
        加载阶段：加载单元资源到内存
        
        Args:
            unit_id: 单元唯一标识
            unit_name: 单元名称
            version: 单元版本
            load_handler: 自定义加载处理器
            
        Returns:
            LifecycleResult: 操作结果
        """
        if unit_id in self._units:
            current_state = self.get_unit_state(unit_id)
            if current_state != UnitState.UNLOADED:
                return LifecycleResult(
                    success=False,
                    message=f"单元 {unit_id} 已存在且状态为 {current_state.value}",
                    new_state=current_state
                )
        
        # 创建单元元数据
        meta = UnitMetadata(
            unit_id=unit_id,
            unit_name=unit_name,
            version=version,
            max_retries=self._max_retries
        )
        self._units[unit_id] = meta
        
        # 执行状态转换
        if not self._transition_to(unit_id, UnitState.LOADING):
            return LifecycleResult(
                success=False,
                message="状态转换失败",
                new_state=self.get_unit_state(unit_id)
            )
        
        # 执行加载逻辑
        try:
            if load_handler:
                load_handler(unit_id)
            else:
                # 默认加载逻辑
                logger.info(f"📦 加载单元 {unit_id} ({unit_name} v{version})")
                time.sleep(0.1)  # 模拟加载延迟
            
            # 触发加载完成事件
            self._trigger_event(LifecycleEvent.LOAD, unit_id)
            
            # 自动进入校验阶段
            return self.validate(unit_id)
            
        except Exception as e:
            logger.error(f"❌ 单元 {unit_id} 加载失败: {e}")
            meta.error_message = str(e)
            self._transition_to(unit_id, UnitState.ERROR)
            return LifecycleResult(
                success=False,
                message=f"加载失败: {e}",
                new_state=UnitState.ERROR
            )
    
    def validate(self, unit_id: str, 
                validate_handler: Optional[Callable] = None) -> LifecycleResult:
        """
        校验阶段：验证单元完整性和依赖
        
        Args:
            unit_id: 单元ID
            validate_handler: 自定义校验处理器
            
        Returns:
            LifecycleResult: 操作结果
        """
        if unit_id not in self._units:
            return LifecycleResult(
                success=False,
                message=f"单元 {unit_id} 不存在",
                new_state=None
            )
        
        meta = self._units[unit_id]
        
        # 执行状态转换
        if not self._transition_to(unit_id, UnitState.VALIDATING):
            return LifecycleResult(
                success=False,
                message="状态转换失败",
                new_state=self.get_unit_state(unit_id)
            )
        
        try:
            if validate_handler:
                validate_handler(unit_id)
            else:
                # 默认校验逻辑
                logger.info(f"🔍 校验单元 {unit_id}")
                # 模拟校验过程
                time.sleep(0.1)
                
                # 检查必要字段
                if not meta.unit_id or not meta.unit_name:
                    raise ValueError("单元缺少必要字段")
            
            # 触发校验完成事件
            self._trigger_event(LifecycleEvent.VALIDATE, unit_id)
            
            # 自动进入实例化阶段
            return self.instantiate(unit_id)
            
        except Exception as e:
            logger.error(f"❌ 单元 {unit_id} 校验失败: {e}")
            meta.error_message = str(e)
            self._transition_to(unit_id, UnitState.ERROR)
            return LifecycleResult(
                success=False,
                message=f"校验失败: {e}",
                new_state=UnitState.ERROR
            )
    
    def instantiate(self, unit_id: str,
                   instantiate_handler: Optional[Callable] = None) -> LifecycleResult:
        """
        实例化阶段：创建单元运行实例
        
        Args:
            unit_id: 单元ID
            instantiate_handler: 自定义实例化处理器
            
        Returns:
            LifecycleResult: 操作结果
        """
        if unit_id not in self._units:
            return LifecycleResult(
                success=False,
                message=f"单元 {unit_id} 不存在",
                new_state=None
            )
        
        # 执行状态转换
        if not self._transition_to(unit_id, UnitState.INSTANTIATED):
            return LifecycleResult(
                success=False,
                message="状态转换失败",
                new_state=self.get_unit_state(unit_id)
            )
        
        try:
            if instantiate_handler:
                instance = instantiate_handler(unit_id)
            else:
                # 默认实例化逻辑
                logger.info(f"🔨 实例化单元 {unit_id}")
                # 创建单元实例
                instance = {"unit_id": unit_id, "initialized": True}
            
            # 存储实例
            self._unit_instances[unit_id] = instance
            
            # 触发实例化完成事件
            self._trigger_event(LifecycleEvent.INSTANTIATE, unit_id)
            
            return LifecycleResult(
                success=True,
                message=f"单元 {unit_id} 实例化成功",
                new_state=UnitState.INSTANTIATED,
                data={"instance": instance}
            )
            
        except Exception as e:
            logger.error(f"❌ 单元 {unit_id} 实例化失败: {e}")
            meta = self._units[unit_id]
            meta.error_message = str(e)
            self._transition_to(unit_id, UnitState.ERROR)
            return LifecycleResult(
                success=False,
                message=f"实例化失败: {e}",
                new_state=UnitState.ERROR
            )
    
    def activate(self, unit_id: str,
                activate_handler: Optional[Callable] = None) -> LifecycleResult:
        """
        激活阶段：启动单元使其进入活跃状态
        
        Args:
            unit_id: 单元ID
            activate_handler: 自定义激活处理器
            
        Returns:
            LifecycleResult: 操作结果
        """
        if unit_id not in self._units:
            return LifecycleResult(
                success=False,
                message=f"单元 {unit_id} 不存在",
                new_state=None
            )
        
        current_state = self.get_unit_state(unit_id)
        
        # 从挂起状态恢复
        if current_state == UnitState.SUSPENDED:
            return self.resume(unit_id, activate_handler)
        
        # 执行状态转换
        if not self._transition_to(unit_id, UnitState.ACTIVE):
            return LifecycleResult(
                success=False,
                message="状态转换失败",
                new_state=self.get_unit_state(unit_id)
            )
        
        try:
            if activate_handler:
                activate_handler(unit_id)
            else:
                # 默认激活逻辑
                logger.info(f"⚡ 激活单元 {unit_id}")
                instance = self._unit_instances.get(unit_id)
                if instance:
                    instance["active"] = True
            
            # 触发激活完成事件
            self._trigger_event(LifecycleEvent.ACTIVATE, unit_id)
            
            return LifecycleResult(
                success=True,
                message=f"单元 {unit_id} 激活成功",
                new_state=UnitState.ACTIVE
            )
            
        except Exception as e:
            logger.error(f"❌ 单元 {unit_id} 激活失败: {e}")
            meta = self._units[unit_id]
            meta.error_message = str(e)
            self._transition_to(unit_id, UnitState.ERROR)
            return LifecycleResult(
                success=False,
                message=f"激活失败: {e}",
                new_state=UnitState.ERROR
            )
    
    def suspend(self, unit_id: str,
              suspend_handler: Optional[Callable] = None) -> LifecycleResult:
        """
        挂起阶段：暂停单元运行
        
        Args:
            unit_id: 单元ID
            suspend_handler: 自定义挂起处理器
            
        Returns:
            LifecycleResult: 操作结果
        """
        if unit_id not in self._units:
            return LifecycleResult(
                success=False,
                message=f"单元 {unit_id} 不存在",
                new_state=None
            )
        
        current_state = self.get_unit_state(unit_id)
        if current_state != UnitState.ACTIVE:
            return LifecycleResult(
                success=False,
                message=f"单元 {unit_id} 当前状态 {current_state.value} 不允许挂起",
                new_state=current_state
            )
        
        # 执行状态转换
        if not self._transition_to(unit_id, UnitState.SUSPENDED):
            return LifecycleResult(
                success=False,
                message="状态转换失败",
                new_state=self.get_unit_state(unit_id)
            )
        
        try:
            if suspend_handler:
                suspend_handler(unit_id)
            else:
                # 默认挂起逻辑
                logger.info(f"💤 挂起单元 {unit_id}")
                instance = self._unit_instances.get(unit_id)
                if instance:
                    instance["active"] = False
            
            # 触发挂起事件
            self._trigger_event(LifecycleEvent.SUSPEND, unit_id)
            
            return LifecycleResult(
                success=True,
                message=f"单元 {unit_id} 挂起成功",
                new_state=UnitState.SUSPENDED
            )
            
        except Exception as e:
            logger.error(f"❌ 单元 {unit_id} 挂起失败: {e}")
            meta = self._units[unit_id]
            meta.error_message = str(e)
            self._transition_to(unit_id, UnitState.ERROR)
            return LifecycleResult(
                success=False,
                message=f"挂起失败: {e}",
                new_state=UnitState.ERROR
            )
    
    def resume(self, unit_id: str,
             resume_handler: Optional[Callable] = None) -> LifecycleResult:
        """
        恢复阶段：从挂起状态恢复运行
        
        Args:
            unit_id: 单元ID
            resume_handler: 自定义恢复处理器
            
        Returns:
            LifecycleResult: 操作结果
        """
        if unit_id not in self._units:
            return LifecycleResult(
                success=False,
                message=f"单元 {unit_id} 不存在",
                new_state=None
            )
        
        current_state = self.get_unit_state(unit_id)
        if current_state != UnitState.SUSPENDED:
            return LifecycleResult(
                success=False,
                message=f"单元 {unit_id} 当前状态 {current_state.value} 不是挂起状态",
                new_state=current_state
            )
        
        # 执行状态转换
        if not self._transition_to(unit_id, UnitState.ACTIVE):
            return LifecycleResult(
                success=False,
                message="状态转换失败",
                new_state=self.get_unit_state(unit_id)
            )
        
        try:
            if resume_handler:
                resume_handler(unit_id)
            else:
                # 默认恢复逻辑
                logger.info(f"🔄 恢复单元 {unit_id}")
                instance = self._unit_instances.get(unit_id)
                if instance:
                    instance["active"] = True
            
            # 触发恢复事件
            self._trigger_event(LifecycleEvent.RESUME, unit_id)
            
            return LifecycleResult(
                success=True,
                message=f"单元 {unit_id} 恢复成功",
                new_state=UnitState.ACTIVE
            )
            
        except Exception as e:
            logger.error(f"❌ 单元 {unit_id} 恢复失败: {e}")
            meta = self._units[unit_id]
            meta.error_message = str(e)
            self._transition_to(unit_id, UnitState.ERROR)
            return LifecycleResult(
                success=False,
                message=f"恢复失败: {e}",
                new_state=UnitState.ERROR
            )
    
    def unload(self, unit_id: str,
             unload_handler: Optional[Callable] = None) -> LifecycleResult:
        """
        卸载阶段：完全卸载单元
        
        Args:
            unit_id: 单元ID
            unload_handler: 自定义卸载处理器
            
        Returns:
            LifecycleResult: 操作结果
        """
        if unit_id not in self._units:
            return LifecycleResult(
                success=False,
                message=f"单元 {unit_id} 不存在",
                new_state=None
            )
        
        current_state = self.get_unit_state(unit_id)
        
        # 执行状态转换到卸载中
        if not self._transition_to(unit_id, UnitState.UNLOADING):
            return LifecycleResult(
                success=False,
                message="状态转换失败",
                new_state=current_state
            )
        
        try:
            if unload_handler:
                unload_handler(unit_id)
            else:
                # 默认卸载逻辑
                logger.info(f"🗑️ 卸载单元 {unit_id}")
            
            # 清理资源
            if unit_id in self._unit_instances:
                del self._unit_instances[unit_id]
            
            # 触发卸载事件
            self._trigger_event(LifecycleEvent.UNLOAD, unit_id)
            
            # 完成状态转换
            self._transition_to(unit_id, UnitState.UNLOADED)
            
            return LifecycleResult(
                success=True,
                message=f"单元 {unit_id} 卸载成功",
                new_state=UnitState.UNLOADED
            )
            
        except Exception as e:
            logger.error(f"❌ 单元 {unit_id} 卸载失败: {e}")
            meta = self._units[unit_id]
            meta.error_message = str(e)
            self._transition_to(unit_id, UnitState.ERROR)
            return LifecycleResult(
                success=False,
                message=f"卸载失败: {e}",
                new_state=UnitState.ERROR
            )
    
    # ==================== 高级功能 ====================
    
    def full_lifecycle(self, unit_id: str, unit_name: str, version: str = "1.0.0") -> LifecycleResult:
        """
        执行完整生命周期流程：加载→校验→实例化→激活
        
        Args:
            unit_id: 单元ID
            unit_name: 单元名称
            version: 单元版本
            
        Returns:
            LifecycleResult: 最终结果
        """
        logger.info(f"🚀 开始单元 {unit_id} 完整生命周期流程")
        
        result = self.load(unit_id, unit_name, version)
        
        if result.success:
            # 后续阶段由各方法自动触发
            current_state = self.get_unit_state(unit_id)
            return LifecycleResult(
                success=True,
                message=f"单元 {unit_id} 完整生命周期流程完成，当前状态: {current_state.value if current_state else 'N/A'}",
                new_state=current_state
            )
        else:
            return result
    
    def get_unit_info(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """获取单元详细信息"""
        if unit_id not in self._units:
            return None
        
        meta = self._units[unit_id]
        state = self.get_unit_state(unit_id)
        
        return {
            "unit_id": meta.unit_id,
            "unit_name": meta.unit_name,
            "version": meta.version,
            "state": state.value if state else "未知",
            "instance": self._unit_instances.get(unit_id),
            "loaded_at": meta.loaded_at.isoformat() if meta.loaded_at else None,
            "validated_at": meta.validated_at.isoformat() if meta.validated_at else None,
            "activated_at": meta.activated_at.isoformat() if meta.activated_at else None,
            "suspended_at": meta.suspended_at.isoformat() if meta.suspended_at else None,
            "error_message": meta.error_message,
            "retry_count": meta.retry_count
        }
    
    def list_units(self) -> List[Dict[str, Any]]:
        """列出所有单元"""
        return [self.get_unit_info(uid) for uid in self._units.keys()]
    
    def register_state_listener(self, state: UnitState, 
                                listener: Callable[[str, UnitState], None]):
        """注册状态监听器"""
        if state in self._state_listeners:
            self._state_listeners[state].append(listener)
            logger.info(f"已注册状态监听器: {state.value}")
    
    def register_event_hook(self, event: LifecycleEvent,
                           hook: Callable[[str], None]):
        """注册事件钩子"""
        if event in self._event_hooks:
            self._event_hooks[event].append(hook)
            logger.info(f"已注册事件钩子: {event.value}")
    
    def _trigger_event(self, event: LifecycleEvent, unit_id: str):
        """触发事件钩子"""
        hooks = self._event_hooks.get(event, [])
        for hook in hooks:
            try:
                hook(unit_id)
            except Exception as e:
                logger.error(f"事件钩子执行失败: {e}")
    
    def reset(self, unit_id: str) -> LifecycleResult:
        """
        重置单元到初始状态
        
        Args:
            unit_id: 单元ID
            
        Returns:
            LifecycleResult: 操作结果
        """
        if unit_id not in self._units:
            return LifecycleResult(
                success=False,
                message=f"单元 {unit_id} 不存在",
                new_state=None
            )
        
        # 先卸载
        unload_result = self.unload(unit_id)
        
        # 触发重置事件
        self._trigger_event(LifecycleEvent.RESET, unit_id)
        
        # 移除单元数据
        if unit_id in self._units:
            del self._units[unit_id]
        
        return LifecycleResult(
            success=unload_result.success,
            message=f"单元 {unit_id} 已重置",
            new_state=UnitState.UNLOADED
        )


# ==================== 便捷函数 ====================

def create_manager(max_retries: int = 3) -> LifecycleManager:
    """创建生命周期管理器实例"""
    return LifecycleManager(max_retries=max_retries)


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    # 演示用法
    print("=" * 50)
    print("序境3.0 生命周期状态机演示")
    print("=" * 50)
    
    # 创建管理器
    manager = create_manager()
    
    # 完整生命周期演示
    print("\n📋 执行完整生命周期流程...")
    result = manager.full_lifecycle("unit_001", "测试单元", "1.0.0")
    print(f"结果: {result.message}")
    print(f"状态: {result.new_state.value if result.new_state else 'N/A'}")
    
    # 获取单元信息
    print("\n📊 单元信息:")
    info = manager.get_unit_info("unit_001")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 挂起演示
    print("\n💤 挂起单元...")
    result = manager.suspend("unit_001")
    print(f"结果: {result.message}")
    
    # 恢复演示
    print("\n🔄 恢复单元...")
    result = manager.activate("unit_001")  # 激活会自动从挂起恢复
    print(f"结果: {result.message}")
    
    # 卸载演示
    print("\n🗑️ 卸载单元...")
    result = manager.unload("unit_001")
    print(f"结果: {result.message}")
    
    print("\n✓ 演示完成")
