#!/bin/bash
# ============================================================================
# 🎼 Symphony v2.1.2 Linux/Mac 安装脚本
# ============================================================================

echo ""
echo "========================================"
echo "  交响 Symphony 安装程序"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python，请先安装Python 3.8+"
    exit 1
fi

echo "[1/4] 创建目录..."
mkdir -p ~/.openclaw/workspace/skills/symphony

echo "[2/4] 复制文件..."
cp -r symphony/* ~/.openclaw/workspace/skills/symphony/

echo "[3/4] 配置模板..."
if [ ! -f ~/.openclaw/workspace/skills/symphony/config.py ]; then
    cp config.template.py ~/.openclaw/workspace/skills/symphony/config.py
    echo "[注意] 请编辑 config.py 填写API密钥"
fi

echo "[4/4] 完成安装!"
echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "下一步："
echo "1. 编辑 config.py 填写API密钥"
echo "2. 开始使用：呼叫\"交响\"即可"
echo ""
