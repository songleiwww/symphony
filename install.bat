@echo off
REM Symphony v2.1.2 Windows Install
echo.
echo ========================================
echo  Symphony v2.1.2 Installing...
echo ========================================
echo.
echo [1/2] Creating directory...
if not exist "%USERPROFILE%\.openclaw\workspace\skills\symphony" (
    mkdir "%USERPROFILE%\.openclaw\workspace\skills\symphony"
)
echo [2/2] Copying files...
copy /Y * "%USERPROFILE%\.openclaw\workspace\skills\symphony\"
echo.
echo ========================================
echo  Done!
echo ========================================
echo Next step: Edit config.py with your API key
echo.
pause
