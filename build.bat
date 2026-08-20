@echo off
chcp 65001 >nul
echo ========================================
echo   打包 EXE
echo ========================================
echo.
pip install pyinstaller -q
pyinstaller --name=StyleWriterDesktop --windowed --onedir --clean --noconfirm main.py
echo.
echo 打包完成: dist\StyleWriterDesktop
pause

