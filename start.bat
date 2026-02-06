@echo off
chcp 65001 >nul
echo ========================================
echo    启动脚本
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 未找到虚拟环境！
    pause
    exit /b 1
)

REM 激活虚拟环境
echo 正在激活虚拟环境...
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo [错误] 虚拟环境激活失败！
    pause
    exit /b 1
)

call python main.py