@echo off
REM ========================================
REM 交响 Symphony 独立运行启动脚本
REM ========================================

echo.
echo ========================================
echo   交响 Symphony 独立运行
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查Python环境...
python --version

echo [2/3] 加载配置文件...
python -c "from config import CONFIG; print('      主模型:', CONFIG['primary_model'])"
echo      配置加载成功

echo [3/3] 启动交响...
echo.
python symphony.py

pause
