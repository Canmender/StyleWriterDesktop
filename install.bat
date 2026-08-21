@echo off
chcp 65001 >nul
echo ========================================
echo   StyleWriter Desktop - 安装
echo ========================================
echo.

echo [1/2] 安装 Python 依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo [OK] 依赖安装完成

echo.
echo [2/2] 是否下载运行环境？
echo   - llama.cpp (CUDA版)
echo   - 默认模型 (Qwen2.5-1.5B)
echo.
set /p download="下载运行环境? (y/n): "
if /i "%download%"=="y" (
    python download_runtime.py
)

echo.
echo ========================================
echo 安装完成!
echo 运行 run.bat 启动程序
echo ========================================
pause

