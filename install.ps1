# Symphony v1.1.0-beta 一键安装脚本 (Windows PowerShell)
# 使用: .\install.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Symphony v1.1.0-beta 一键安装" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 检查Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ 需要 Python 3.8+" -ForegroundColor Red
    exit 1
}

# 安装依赖
Write-Host "📦 安装依赖..." -ForegroundColor Yellow
pip install requests

# 创建目录
New-Item -ItemType Directory -Force -Path symphony | Out-Null
Set-Location symphony

# 创建配置
Write-Host "📝 创建配置..." -ForegroundColor Yellow
@"
# Symphony 配置文件
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
"@ | Out-File -FilePath config.py -Encoding utf8

Write-Host ""
Write-Host "✅ 安装完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "下一步：" -ForegroundColor White
Write-Host "1. 编辑 config.py 填入API Key" -ForegroundColor White
Write-Host "2. 运行: python symphony_core.py" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
