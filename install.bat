@echo off
chcp 65001 >nul
echo ========================================
echo   安装依赖
echo ========================================
echo.
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
echo 安装完成!
pause

