@echo off
cd /d "%~dp0"
chcp 65001 >nul

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
%PY_CMD% -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo.
    echo [安装失败] 无法安装依赖。
    pause
    exit /b
)

echo.
echo ==========================================
echo      正在安装浏览器内核...
echo      (尝试方案 1: 国内镜像源)
echo ==========================================
:: 注意：去掉结尾的斜杠
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
%PY_CMD% -m playwright install
if %errorlevel% equ 0 goto :RUN_SPIDER

echo.
echo ==========================================
echo      方案 1 失败，正在尝试方案 2...
echo      (尝试方案 2: 官方源)
echo ==========================================
:: 清除环境变量，使用默认源
set PLAYWRIGHT_DOWNLOAD_HOST=
%PY_CMD% -m playwright install
if %errorlevel% neq 0 (
    echo.
    echo [严重错误] 浏览器内核安装彻底失败。
    echo 请检查网络连接，或者稍后再试。
    pause
    exit /b
)

:RUN_SPIDER
echo.
echo ==========================================
echo      准备就绪，启动爬虫！
echo ==========================================
%PY_CMD% nmpa_spider.py

pause
