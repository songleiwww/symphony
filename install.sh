#!/bin/bash
# Symphony v1.1.0-beta 一键安装脚本 (Linux/macOS)
# 使用: bash install.sh

set -e

echo "=========================================="
echo "Symphony v1.1.0-beta 一键安装"
echo "=========================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3.8+"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
pip3 install requests

# 创建目录
mkdir -p symphony
cd symphony

# 下载配置文件
echo "📥 下载配置..."
cat > config.py << 'EOF'
# Symphony 配置文件
# 请填入你的API Key

MODEL_CHAIN = [
    {
        "name": "zhipu_glm4_flash",
        "model_id": "glm-4-flash",
        "api_key": "YOUR_API_KEY",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "provider": "zhipu",
        "enabled": True,
        "priority": 1
    }
]
EOF

# 下载核心文件
echo "📥 下载核心文件..."
curl -sL https://raw.githubusercontent.com/songleiwww/symphony/main/symphony_core.py -o symphony_core.py
curl -sL https://raw.githubusercontent.com/songleiwww/symphony/main/model_manager.py -o model_manager.py
curl -sL https://raw.githubusercontent.com/songleiwww/symphony/main/fault_isolator.py -o fault_isolator.py

echo ""
echo "✅ 安装完成！"
echo "=========================================="
echo "下一步："
echo "1. 编辑 config.py 填入API Key"
echo "2. 运行: python symphony_core.py"
echo "=========================================="
