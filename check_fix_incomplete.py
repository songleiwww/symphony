#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.5.0 - Check & Fix Incomplete Items
检查未完成/未完善项目并修复
"""
import sys
import json
import time
import requests
import threading
from datetime import datetime
from config import MODEL_CHAIN
import os

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# 检查清单
CHECKLIST = {
    "核心模块": {
        "fault_isolator.py": "故障隔离器",
        "fallback.py": "降级策略",
        "config.py": "配置文件",
        "model_manager.py": "模型管理器"
    },
    "文档": {
        "README.md": "README",
        "RELEASE.md": "发布说明",
        "USER_GUIDE.md": "用户指南",
        "INSTALLATION.md": "安装文档"
    },
    "脚本": {
        "true_multi_model_v4.py": "多模型脚本",
        "dynamic_dispatcher.py": "动态调度",
        "intelligent_dispatcher.py": "智能调度",
        "passive_trigger_engine.py": "触发引擎"
    }
}


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_config, prompt, max_tokens=300):
    url = model_config["base_url"] + "/chat/completions"
    headers = {"Authorization": "Bearer " + model_config["api_key"], "Content-Type": "application/json"}
    data = {"model": model_config["model_id"], "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
    t0 = time.time()
    try:
        r = requests.post(url, headers=headers, json=data, timeout=25)
        elapsed = time.time() - t0
        if r.status_code == 200:
            j = r.json()
            return {"success": True, "content": j["choices"][0]["message"]["content"], "tokens": j.get("usage", {}).get("total_tokens", 0), "time": elapsed}
        else:
            return {"success": False, "error": "HTTP " + str(r.status_code)}
    except Exception as e:
        return {"success": False, "error": str(e)}


print("=" * 70)
print("Symphony v1.5.0 - Check & Fix Incomplete Items")
print("=" * 70)

# Phase 1: 检查文件完整性
print("\n" + "=" * 70)
print("Phase 1: Checking File Completeness")
print("=" * 70)

workspace = r"C:\Users\Administrator\.openclaw\workspace\skills\symphony"

missing_files = []
existing_files = []

for category, files in CHECKLIST.items():
    print("\n[{}]".format(category))
    for filename, desc in files.items():
        filepath = os.path.join(workspace, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print("  ✅ {} ({})".format(filename, size))
            existing_files.append(filename)
        else:
            print("  ❌ {} - 缺失".format(filename))
            missing_files.append({"category": category, "file": filename, "desc": desc})

# Phase 2: 分析未完善项
print("\n" + "=" * 70)
print("Phase 2: Analyze Incomplete Items")
print("=" * 70)

# 分析缺少的核心模块
if missing_files:
    print("\n需要补充的文件:")
    for item in missing_files:
        print("  - {} ({})".format(item["file"], item["desc"]))

# Phase 3: 生成缺失文件
print("\n" + "=" * 70)
print("Phase 3: Generate Missing Files")
print("=" * 70)

# 补充缺失的模型管理器
model_manager_code = '''"""
Symphony Model Manager - 模型管理器
管理多模型配置、调用和调度
"""
import requests
import threading
from typing import List, Dict, Any, Optional

class ModelManager:
    """模型管理器"""
    
    def __init__(self, model_chain: List[Dict]):
        self.model_chain = model_chain
        self.enabled_models = [m for m in model_chain if m.get("enabled")]
        self.current_index = 0
    
    def get_model(self, index: int) -> Optional[Dict]:
        """获取指定索引的模型"""
        if 0 <= index < len(self.enabled_models):
            return self.enabled_models[index]
        return None
    
    def get_next_model(self) -> Optional[Dict]:
        """获取下一个可用模型"""
        if not self.enabled_models:
            return None
        model = self.enabled_models[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.enabled_models)
        return model
    
    def call(self, prompt: str, model_index: int = 0) -> Dict[str, Any]:
        """调用模型"""
        model = self.get_model(model_index)
        if not model:
            return {"success": False, "error": "Model not found"}
        
        url = model["base_url"] + "/chat/completions"
        headers = {"Authorization": "Bearer " + model["api_key"], "Content-Type": "application/json"}
        data = {
            "model": model["model_id"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        try:
            r = requests.post(url, headers=headers, json=data, timeout=30)
            if r.status_code == 200:
                j = r.json()
                return {
                    "success": True,
                    "content": j["choices"][0]["message"]["content"],
                    "tokens": j.get("usage", {}).get("total_tokens", 0),
                    "model": model.get("alias", model.get("name"))
                }
            else:
                return {"success": False, "error": "HTTP " + str(r.status_code)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def parallel_call(self, prompts: List[str]) -> List[Dict[str, Any]]:
        """并行调用多个模型"""
        results = [None] * len(prompts)
        threads = []
        
        def call_model(i, prompt):
            model = self.get_next_model()
            if model:
                result = self.call(prompt)
                results[i] = result
        
        for i, prompt in enumerate(prompts):
            t = threading.Thread(target=call_model, args=(i, prompt))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        return results
    
    def get_model_info(self) -> List[Dict]:
        """获取所有模型信息"""
        return [
            {
                "name": m.get("alias", m.get("name")),
                "provider": m.get("provider"),
                "enabled": m.get("enabled"),
                "priority": m.get("priority")
            }
            for m in self.enabled_models
        ]


if __name__ == "__main__":
    from config import MODEL_CHAIN
    manager = ModelManager(MODEL_CHAIN)
    print("可用模型数量:", len(manager.enabled_models))
    print("模型列表:", manager.get_model_info())
'''

# 补充缺失的触发引擎
trigger_engine_code = '''"""
Symphony Passive Trigger Engine - 被动触发引擎
根据用户输入自动触发交响模式
"""

# 触发词配置
TRIGGER_CONFIG = {
    "P0_核心": {
        "keywords": ["交响", "symphony", "多模型", "协作"],
        "team_size": 6,
        "description": "完整多模型协作"
    },
    "P1_开发": {
        "keywords": ["开发", "研发", "编程", "代码"],
        "team_size": 3,
        "description": "开发团队协作"
    },
    "P2_优化": {
        "keywords": ["优化", "改进", "提升"],
        "team_size": 2,
        "description": "技术优化"
    },
    "P3_分析": {
        "keywords": ["分析", "调研", "评估"],
        "team_size": 3,
        "description": "分析调研"
    },
    "P4_文档": {
        "keywords": ["文档", "说明", "指南"],
        "team_size": 2,
        "description": "文档编写"
    },
    "P5_运维": {
        "keywords": ["部署", "运维", "监控"],
        "team_size": 2,
        "description": "运维支持"
    }
}


class TriggerEngine:
    """触发引擎"""
    
    def __init__(self, config: dict = None):
        self.config = config or TRIGGER_CONFIG
    
    def match(self, user_input: str) -> tuple:
        """匹配触发词，返回(优先级, 配置)"""
        input_lower = user_input.lower()
        
        for level, cfg in self.config.items():
            for keyword in cfg["keywords"]:
                if keyword in input_lower:
                    return level, cfg
        
        return None, None
    
    def should_trigger(self, user_input: str) -> bool:
        """判断是否应该触发"""
        level, _ = self.match(user_input)
        return level is not None
    
    def get_team_config(self, user_input: str) -> dict:
        """获取团队配置"""
        level, cfg = self.match(user_input)
        if level:
            return {"level": level, **cfg}
        return {"level": None, "team_size": 0}


def create_trigger_handler():
    """创建触发处理器"""
    engine = TriggerEngine()
    
    def handle(user_input: str) -> dict:
        """处理用户输入"""
        if engine.should_trigger(user_input):
            config = engine.get_team_config(user_input)
            return {
                "triggered": True,
                "config": config
            }
        return {"triggered": False}
    
    return handle


if __name__ == "__main__":
    handler = create_trigger_handler()
    
    test_inputs = [
        "交响 开发一个系统",
        "交响 优化性能",
        "分析用户行为",
        "普通对话"
    ]
    
    for inp in test_inputs:
        result = handler(inp)
        print(f"输入: {inp}")
        print(f"触发: {result}")
        print()
'''

generated_files = []

# 生成缺失文件
if any(f["file"] == "model_manager.py" for f in missing_files):
    with open("model_manager.py", "w", encoding="utf-8") as f:
        f.write(model_manager_code)
    print("  ✅ model_manager.py")
    generated_files.append("model_manager.py")

if any(f["file"] == "passive_trigger_engine.py" for f in missing_files):
    with open("passive_trigger_engine.py", "w", encoding="utf-8") as f:
        f.write(trigger_engine_code)
    print("  ✅ passive_trigger_engine.py")
    generated_files.append("passive_trigger_engine.py")

# Phase 4: 验证修复
print("\n" + "=" * 70)
print("Phase 4: Verification")
print("=" * 70)

# 验证生成的文件
for filename in generated_files:
    filepath = os.path.join(workspace, filename)
    if os.path.exists(filepath):
        print("  ✅ {} 验证通过".format(filename))
    else:
        print("  ❌ {} 验证失败".format(filename))

# Phase 5: 总结报告
print("\n" + "=" * 70)
print("Phase 5: Summary Report")
print("=" * 70)

print("\n  检查结果:")
print("    缺失文件: {} 个".format(len(missing_files)))
print("    已生成: {} 个".format(len(generated_files)))
print("    现有文件: {} 个".format(len(existing_files)))

# 保存报告
report = {
    "title": "Symphony v1.5.0 Check & Fix",
    "version": "1.5.0",
    "datetime": datetime.now().isoformat(),
    "checklist": CHECKLIST,
    "missing_files": missing_files,
    "generated_files": generated_files,
    "existing_files": existing_files,
    "summary": {
        "total_checked": sum(len(v) for v in CHECKLIST.values()),
        "missing_count": len(missing_files),
        "generated_count": len(generated_files)
    }
}

with open("check_fix_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\nReport saved: check_fix_report.json")
print("\nSymphony - 智韵交响，共创华章！")
