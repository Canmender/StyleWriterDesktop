@echo off
chcp 65001 >nul
echo ========================================
echo   StyleWriter Desktop - 环境配置
echo ========================================
echo.
echo 此脚本将下载:
echo   1. llama.cpp (CUDA版)
echo   2. 默认模型 (Qwen2.5-1.5B)
echo.
echo 首次下载约需 1GB 流量
echo.
pause
python download_runtime.py
pause

