# -*- coding: utf-8 -*-
"""
序境交响 - 工具说明
===================
作为Skill工具使用，内核管理各种工具指向文件
引导AI正确使用序境系统
"""
import os

# 路径配置
SKILL_DIR = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony'
KERNEL_DIR = os.path.join(SKILL_DIR, 'Kernel')
DATA_DIR = os.path.join(SKILL_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'symphony.db')


# ============ 工具指向 ============

TOOL_POINTERS = {
    'kernel_loader': {
        'file': 'Kernel/kernel_loader.py',
        'class': 'KernelLoader',
        'method': 'load_all',
        'desc': '加载内核配置',
        'usage': 'from skills.symphony.Kernel.kernel_loader import KernelLoader; kl = KernelLoader(); kl.load_all()'
    },
    'dispatch': {
        'file': 'Kernel/dispatch_manager.py',
        'class': 'DispatchManager',
        'method': 'dispatch',
        'desc': '调度官属执行任务',
        'usage': 'from skills.symphony.Kernel.dispatch_manager import DispatchManager; dm = DispatchManager(DB_PATH); dm.dispatch(office_id)'
    },
    'config': {
        'file': 'Kernel/config_manager.py',
        'class': 'ConfigManager',
        'method': 'get_rules',
        'desc': '获取内核规则',
        'usage': 'from skills.symphony.Kernel.config_manager import ConfigManager; cm = ConfigManager(DB_PATH); cm.get_rules()'
    },
    'strategy': {
        'file': 'Kernel/kernel_strategy.py',
        'class': 'KernelStrategy',
        'method': 'initialize',
        'desc': '初始化内核',
        'usage': 'from skills.symphony.Kernel.kernel_strategy import KernelStrategy; ks = KernelStrategy(); ks.initialize()'
    },
    'modular': {
        'file': 'modular_system.py',
        'class': 'ModularSystem',
        'method': 'scan_modules',
        'desc': '扫描模块状态',
        'usage': 'from skills.symphony.modular_system import ModularSystem; ms = ModularSystem(); ms.scan_modules()'
    }
}


# ============ 核心规则 ============

KERNEL_RULES = """
【内核使用规则】

1. 现在时优先
   - 读取配置只从 symphony.db
   - 不使用 old/ 任何文件
   - 内存配置优先级高于文件

2. 数据库唯一
   - 官署/官属/模型 全部来自 symphony.db
   - 修改后立即生效，无需重启

3. 模块化
   - kernel/ 必需
   - data/ 必需  
   - core/ 可选
   - old/ 禁用
"""


# ============ 使用示例 ============

USAGE_EXAMPLES = """
【使用示例】

1. 加载内核
   >>> from skills.symphony.Kernel.kernel_loader import KernelLoader
   >>> kl = KernelLoader()
   >>> kl.load_all()
   >>> print(kl.rules)    # 规则
   >>> print(kl.offices)  # 官署
   >>> print(kl.roles)    # 官属

2. 调度官属
   >>> from skills.symphony.Kernel.dispatch_manager import DispatchManager
   >>> dm = DispatchManager(DB_PATH)
   >>> dm.dispatch('office_008', '推理模型')

3. 获取统计
   >>> from skills.symphony.Kernel.kernel_strategy import KernelStrategy
   >>> ks = KernelStrategy()
   >>> ks.initialize()
   >>> print(ks.data)
"""


def get_tool_info(tool_name: str = None):
    """获取工具信息"""
    if tool_name:
        return TOOL_POINTERS.get(tool_name)
    return TOOL_POINTERS


def print_guide():
    """打印使用指南"""
    print("="*60)
    print("序境交响 - 工具使用指南")
    print("="*60)
    print(KERNEL_RULES)
    print("\n【可用工具】")
    for name, info in TOOL_POINTERS.items():
        print(f"\n• {name}")
        print(f"  文件: {info['file']}")
        print(f"  说明: {info['desc']}")
        print(f"  用法: {info['usage']}")
    print("\n" + USAGE_EXAMPLES)


if __name__ == "__main__":
    print_guide()
