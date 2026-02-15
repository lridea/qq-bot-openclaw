@echo off
chcp 65001 >nul
echo ================================
echo   QQ Bot - OpenClaw
echo   正在启动机器人...
echo ================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到 Python
    echo 请先安装 Python 3.8 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\python.exe" (
    echo 📦 未检测到虚拟环境，正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖是否安装
pip show nonebot2 >nul 2>&1
if errorlevel 1 (
    echo 📥 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 安装依赖失败
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
)

REM 检查 .env 文件是否存在
if not exist ".env" (
    echo ⚠️  未找到 .env 配置文件
    echo 正在创建默认配置...
    copy .env.example .env >nul
    echo ✅ 已创建 .env 文件
    echo.
    echo ⚠️  请编辑 .env 文件，填写正确的配置：
    echo    - OPENCLAW_API_URL
    echo    - OPENCLAW_API_KEY
    echo    - SUPERUSERS
    echo.
    pause
    exit /b 0
)

REM 启动机器人
echo.
echo ================================
echo   正在启动机器人...
echo   按 Ctrl+C 停止
echo ================================
echo.

python bot.py

REM 如果机器人退出，暂停以显示错误信息
if errorlevel 1 (
    echo.
    echo ❌ 机器人启动失败
    pause
)
