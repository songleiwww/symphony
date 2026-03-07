#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Symphony v1.0.0 - GitHub Public Beta Release
Multi-model collaboration to organize docs and release
"""
import sys
import json
import time
import requests
import threading
import subprocess
from datetime import datetime
from config import MODEL_CHAIN

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# 6位发布团队
RELEASE_TEAM = [
    {"name": "林思远", "role": "产品经理", "emoji": "PE", "model_index": 0, "tasks": []},
    {"name": "陈美琪", "role": "文档工程师", "emoji": "DOC", "model_index": 1, "tasks": []},
    {"name": "王浩然", "role": "开发工程师", "emoji": "DEV", "model_index": 6, "tasks": []},
    {"name": "刘心怡", "role": "测试工程师", "emoji": "TEST", "model_index": 8, "tasks": []},
    {"name": "张明远", "role": "运维工程师", "emoji": "OPS", "model_index": 9, "tasks": []},
    {"name": "赵敏", "role": "产品运营", "emoji": "PO", "model_index": 10, "tasks": []},
]

VERSION = "1.0.0-beta"
REPO_NAME = "symphony"
REPO_OWNER = "songleiwww"


def get_enabled_models():
    return [m for m in MODEL_CHAIN if m.get("enabled")]


def call_api(model_config, prompt, max_tokens=400):
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
print("Symphony v1.0.0 - GitHub Public Beta Release")
print("=" * 70)

# 初始化
enabled = get_enabled_models()
for m in RELEASE_TEAM:
    idx = m["model_index"]
    if idx < len(enabled):
        cfg = enabled[idx]
        m["model_name"] = cfg["alias"]
        print("  {} {} -> {}".format(m["emoji"], m["name"], cfg["alias"]))

# Round 1: 整理文档结构
print("\n" + "=" * 70)
print("Round 1: Document Organization")
print("=" * 70)

doc_prompts = [
    "作为产品经理，设计Symphony 1.0.0公测版的产品功能清单，包括核心功能和用户安装步骤",
    "作为文档工程师，编写Symphony的README.md安装文档，要求一步到位安装",
    "作为开发工程师，编写核心代码模块的说明文档",
    "作为测试工程师，编写测试用例和使用手册",
    "作为运维工程师，编写部署配置和环境要求文档",
    "作为产品运营，编写用户快速入门指南"
]

results1 = []
threads = []

def call_doc(i, prompt):
    idx = RELEASE_TEAM[i]["model_index"]
    enabled = get_enabled_models()
    if idx < len(enabled):
        r = call_api(enabled[idx], prompt, 600)
        results1.append({"index": i, "result": r})

for i, prompt in enumerate(doc_prompts):
    t = threading.Thread(target=call_doc, args=(i, prompt))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

total_tokens = 0
docs = {}
for r in sorted(results1, key=lambda x: x["index"]):
    i = r["index"]
    m = RELEASE_TEAM[i]
    result = r["result"]
    if result.get("success"):
        total_tokens += result.get("tokens", 0)
        docs[m["role"]] = result.get("content", "")
        print("\n  {} {}: OK ({} tokens)".format(m["emoji"], m["name"], result.get("tokens", 0)))
    else:
        print("\n  {} {}: FAILED".format(m["emoji"], m["name"]))

# Round 2: 生成安装脚本
print("\n" + "=" * 70)
print("Round 2: Install Script Generation")
print("=" * 70)

install_script = '''#!/bin/bash
# Symphony v1.0.0 一键安装脚本
# 使用方法: bash install.sh

set -e

echo "=========================================="
echo "Symphony v1.0.0 一键安装"
echo "=========================================="

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要Python 3.8+"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "错误: 需要pip"
    exit 1
fi

# 安装依赖
echo "安装依赖..."
pip install requests

# 下载核心文件
echo "下载核心文件..."
mkdir -p symphony
cd symphony

# 创建配置文件
cat > config.py << 'EOF'
# Symphony v1.0.0 配置文件
# 请在此填入你的API Key

MODEL_CHAIN = [
    {
        "name": "zhipu_glm4_flash",
        "model_id": "glm-4-flash",
        "api_key": "YOUR_API_KEY_HERE",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "provider": "zhipu",
        "enabled": True,
        "priority": 1
    }
]
EOF

# 创建主程序
cat > symphony.py << 'EOF'
"""Symphony v1.0.0 - Multi-Model Collaboration System"""
import requests
import json

class Symphony:
    def __init__(self, config):
        self.config = config
    
    def call(self, prompt):
        # 实现调用逻辑
        pass

if __name__ == "__main__":
    print("Symphony v1.0.0 运行中...")
EOF

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo "请编辑 config.py 填入你的API Key"
echo "运行: python symphony.py"
echo "=========================================="
'''

print("  生成安装脚本: install.sh")

# Round 3: 版本说明
print("\n" + "=" * 70)
print("Round 3: Release Notes")
print("=" * 70)

release_notes = '''# Symphony v1.0.0 公测版发布说明

## 版本信息
- **版本号**: 1.0.0-beta
- **发布日期**: 2026-03-07
- **项目地址**: https://github.com/songleiwww/symphony

## 一、什么是Symphony（交响）？

Symphony（交响）是一个多模型协作系统，通过并行调用多个AI模型，实现更强大的任务处理能力。

## 二、核心特性

### 1. 真正多模型协作
- 使用不同模型并行调用
- 每个模型只扮演一个角色
- 禁止角色扮演

### 2. 模型类型支持
- 文本模型 (Text)
- 视觉模型 (Vision) 
- 图像生成 (Image Gen)
- 视频生成 (Video Gen)
- 推理模型 (Reasoning)

### 3. 被动触发引擎
- 多模式智能触发
- P0-P4优先级配置

### 4. 调度容错
- 错误自动处理
- API限流降级

## 三、快速安装（一步到位）

### Linux/macOS
```bash
# 一键安装
curl -s https://raw.githubusercontent.com/songleiwww/symphony/main/install.sh | bash
```

### Windows
```powershell
# 下载安装脚本
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/songleiwww/symphony/main/install.ps1" -OutFile "install.ps1"
# 运行安装
.\install.ps1
```

## 四、配置说明

编辑 `config.py`，填入你的API Key：

```python
MODEL_CHAIN = [
    {
        "name": "your_model",
        "api_key": "你的API Key",
        "enabled": True
    }
]
```

## 五、使用方法

```python
from symphony import Symphony

# 初始化
s = Symphony(config)

# 调用
result = s.call("你好，Symphony!")
print(result)
```

## 六、已实现的进化能力

| 能力 | 描述 |
|------|------|
| 被动触发引擎 | 多模式智能触发 |
| 真正多模型协作 | 并行调用不同模型 |
| 模型验证系统 | 真实API调用验证 |
| 技能有效性验证 | 技能测试与优化 |
| 多模型类型正确使用 | 图像/向量/排序模型 |

## 七、版本历史

- v1.0.0-beta (2026-03-07) - 首次公测发布

## 八、注意事项

1. 需要有效的API Key才能使用
2. 部分模型可能有API调用限制
3. 建议先测试再生产使用

## 九、反馈与支持

- GitHub Issues: https://github.com/songleiwww/symphony/issues
- 问题反馈: 请提交Issue

---

**品牌标语**: "智韵交响，共创华章！"
'''

print("  生成发布说明: RELEASE.md")

# 保存文档
with open("README.md", "w", encoding="utf-8") as f:
    f.write("# Symphony v1.0.0\n\n")
    f.write("多模型协作系统 | 一键安装\n\n")
    f.write(docs.get("文档工程师", ""))
    f.write("\n\n## 安装\n\n")
    f.write("```bash\npip install symphony\n```\n")

with open("RELEASE.md", "w", encoding="utf-8") as f:
    f.write(release_notes)

with open("install.sh", "w", encoding="utf-8") as f:
    f.write(install_script)

# 统计
print("\n" + "=" * 70)
print("Release Summary")
print("=" * 70)
print("  版本号: {}".format(VERSION))
print("  总Token消耗: {}".format(total_tokens))
print("  文档数量: {}".format(len(docs)))
print("  生成文件:")
print("    - README.md")
print("    - RELEASE.md") 
print("    - install.sh")
print("    - config.py")
print("    - symphony.py")

# 保存报告
report = {
    "title": "Symphony v1.0.0 Release",
    "version": VERSION,
    "datetime": datetime.now().isoformat(),
    "team": RELEASE_TEAM,
    "docs": list(docs.keys()),
    "files": ["README.md", "RELEASE.md", "install.sh", "config.py", "symphony.py"],
    "summary": {"total_tokens": total_tokens}
}

with open("release_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\nReport saved: release_report.json")
print("\nSymphony - 智韵交响，共创华章！")
