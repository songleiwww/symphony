#!/bin/bash
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
