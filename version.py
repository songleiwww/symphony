# -*- coding: utf-8 -*-
"""
序境系统 - 版本管理
记录模块版本和更新历史
"""

VERSION = "3.2.0"
UPDATE_TIME = "2026-03-18"
BUILD = "优化版"

# 模块版本
MODULES = {
    "core": "1.0.0",
    "infra": "1.0.0", 
    "rules": "1.0.0",
    "monitor": "1.0.0",
    "logs": "1.0.0",
    "multi_agent": "1.0.0",
    "health": "1.0.0",
    "skills": "1.0.0",
    "progress": "1.0.0",
    "evolution": "1.0.0"
}

# 更新日志
CHANGELOG = [
    {
        "version": "3.2.0",
        "date": "2026-03-18",
        "changes": [
            "清理废弃模块到backup目录",
            "建立统一模块加载器",
            "优化接管技能标识",
            "添加symphony状态查询"
        ]
    },
    {
        "version": "3.1.0",
        "date": "2026-03-17",
        "changes": [
            "新增多Agent协作系统",
            "新增检测后组队系统",
            "新增接管技能模块"
        ]
    }
]

def get_version():
    """获取版本信息"""
    return {
        "version": VERSION,
        "update_time": UPDATE_TIME,
        "build": BUILD,
        "modules": MODULES
    }

def get_changelog():
    """获取更新日志"""
    return CHANGELOG

if __name__ == '__main__':
    print("=== Xujing Kernel Version ===")
    print("Version:", VERSION)
    print("Update:", UPDATE_TIME)
    print("Build:", BUILD)
    print()
    print("Modules:")
    for name, ver in MODULES.items():
        print(" -", name + ":", ver)
