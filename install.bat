@echo off
REM ============================================================================
REM 🎼 Symphony v2.1.2 Windows 安装脚本
REM ============================================================================

echo.
echo ========================================
echo  交响 Symphony Windows 安装程序
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 创建目录...
if not exist "%USERPROFILE%\.openclaw\workspace\skills\symphony" (
    mkdir "%USERPROFILE%\.openclaw\workspace\skills\symphony"
)

echo [2/4] 复制文件...
copy /Y symphony\* "%USERPROFILE%\.openclaw\workspace\skills\symphony\"

echo [3/4] 配置模板...
if not exist "%USERPROFILE%\.openclaw\workspace\skills\symphony\config.py" (
    copy /Y config.template.py "%USERPROFILE%\.openclaw\workspace\skills\symphony\config.py"
    echo [注意] 请编辑 config.py 填写API密钥
)

echo [4/4] 完成安装!
echo.
echo ========================================
echo  安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 编辑 config.py 填写API密钥
echo 2. 开始使用：呼叫"交响"即可
echo.
pause
