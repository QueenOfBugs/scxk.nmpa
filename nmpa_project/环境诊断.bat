@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo      正在诊断 Python 环境...
echo ==========================================
echo.

echo [1] 检查 python 命令:
python --version 2>nul
if %errorlevel% neq 0 (
    echo   未找到 python 命令
) else (
    echo   找到 python 命令
)
echo.

echo [2] 检查 py 启动器:
py --version 2>nul
if %errorlevel% neq 0 (
    echo   未找到 py 启动器
) else (
    echo   找到 py 启动器
)
echo.

echo [3] 检查 pip 命令:
pip --version 2>nul
if %errorlevel% neq 0 (
    echo   未找到 pip 命令 (这是你报错的原因)
) else (
    echo   找到 pip 命令
)
echo.

echo ==========================================
echo      诊断结果与建议
echo ==========================================
echo 如果上面显示“未找到”，说明 Python 安装时没勾选 "Add to PATH"。
echo.
echo 强烈建议：
echo 1. 打开“设置” -> “应用” -> “安装的应用”。
echo 2. 找到 Python，点击卸载。
echo 3. 去 python.org 下载最新版。
echo 4. 安装时，**一定要勾选界面最底下的 Add Python to PATH**。
echo.
pause
