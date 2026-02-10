@echo off
cd /d "%~dp0"
chcp 65001 >nul

echo ==========================================
echo      正在设置 VPN 代理模式...
echo ==========================================
:: 设置 HTTP 和 HTTPS 代理 (使用你提供的端口)
set HTTP_PROXY=http://127.0.0.1:33210
set HTTPS_PROXY=http://127.0.0.1:33210
echo 代理已设置为: 127.0.0.1:33210
echo.

echo ==========================================
echo      正在尝试检测 Python...
echo ==========================================

:: 优先使用 py 启动器
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=py -3
    goto :START_INSTALL
)

:: 其次尝试 python 命令
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=python
    goto :START_INSTALL
)

echo.
echo [严重错误] 电脑上找不到 Python！
echo.
pause
exit /b

:START_INSTALL
echo 使用 Python 引擎: %PY_CMD%
echo.

echo ==========================================
echo      正在安装依赖 (Pandas)...
echo ==========================================
:: VPN 模式下直接连接官方源，通常更稳定
%PY_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [安装失败] 无法安装依赖。
    echo 请确认你的 VPN 软件已经开启，并且端口号确实是 33210。
    pause
    exit /b
)

echo.
echo ==========================================
echo      正在安装浏览器内核...
echo      (VPN 模式 - 连接官方服务器)
echo ==========================================
:: 清除可能存在的国内源设置，强制走官方
set PLAYWRIGHT_DOWNLOAD_HOST=
%PY_CMD% -m playwright install
if %errorlevel% neq 0 (
    echo.
    echo [安装失败] 无法安装浏览器内核。
    echo 请确认你的 VPN 软件已经开启，并且端口号确实是 33210。
    pause
    exit /b
)

echo.
echo ==========================================
echo      准备就绪，启动爬虫！
echo ==========================================
%PY_CMD% nmpa_spider.py

pause
