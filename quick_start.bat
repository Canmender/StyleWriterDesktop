@echo off
chcp 65001 >nul
echo ========================================
echo   StyleWriter Desktop - 快速开始
echo ========================================
echo.

echo [1/3] 安装 Python 依赖...
pip install -r requirements.txt -q
echo [OK] 依赖安装完成

echo.
echo [2/3] 下载运行环境...
python download_runtime.py

echo.
echo [3/3] 启动程序...
echo.
python main.py

