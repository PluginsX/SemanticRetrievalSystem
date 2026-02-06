@echo off
REM 激活虚拟环境并安装依赖脚本
echo ================================
echo  激活虚拟环境并安装依赖
echo ================================

REM 1. 激活虚拟环境
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo [错误] 虚拟环境激活失败！
    echo 请检查 venv\Scripts\activate 是否存在
    pause
    exit /b 1
)

REM 2. 安装requirements.txt中的依赖
echo 正在使用PyPI官方源安装依赖...
pip install -r requirements.txt -i https://pypi.org/simple --trusted-host pypi.org
if %ERRORLEVEL% neq 0 (
    echo [警告] 部分依赖安装失败！
    pause
    exit /b 1
)

echo [成功] 所有依赖安装完成！请运行 start.bat 启动服务。
pause