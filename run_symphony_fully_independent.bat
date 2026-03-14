@echo off
REM ========================================
REM 交响完全独立启动脚本
REM 不依赖任何OpenClaw文件，完全独立运行
REM ========================================

echo.
echo ========================================
echo   交响 Symphony 完全独立运行版
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 检查依赖...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo      安装requests库...
    pip install requests
)
echo      依赖 OK

echo [2/3] 加载独立配置...
python -c "from symphony_independent_config import *; print('      配置加载成功')"

echo [3/3] 启动交响...
echo.
echo ========================================
echo   交响已完全独立启动！
echo   不依赖任何OpenClaw配置文件
echo ========================================
echo.

REM 启动完全独立版本
python symphony_fully_independent.py

pause
