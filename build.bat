@echo off
chcp 65001 >nul
echo ========================================
echo   StyleWriter Desktop - 构建安装包
echo ========================================
echo.
echo 此脚本将:
echo   1. 下载 Python 嵌入式版本
echo   2. 安装所有依赖包
echo   3. 下载 llama.cpp (CUDA版)
echo   4. 下载默认模型 (Qwen2.5-1.5B)
echo   5. 打包成安装程序
echo.
echo 预计需要 2-3GB 磁盘空间
echo 首次构建需要下载约 2GB 文件
echo.
pause
python build_installer.py
pause

