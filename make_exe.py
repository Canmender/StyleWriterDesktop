"""
将安装文件夹打包成自解压 EXE
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
BUILD_DIR = PROJECT_ROOT / "build"
INSTALLER_DIR = BUILD_DIR / "installer"
DIST_DIR = PROJECT_ROOT / "dist"

def create_sfx():
    """创建自解压包"""
    
    # 方法: 使用 PowerShell 创建自解压包
    print("创建自解压安装包...")
    
    # 先创建 7z 压缩包
    archive = BUILD_DIR / "StyleWriter.7z"
    
    # 检查是否有 7z
    seven_zip = None
    for path in [
        "C:\\Program Files\\7-Zip\\7z.exe",
        "C:\\Program Files (x86)\\7-Zip\\7z.exe",
        shutil.which("7z")
    ]:
        if path and os.path.exists(path):
            seven_zip = path
            break
    
    if not seven_zip:
        print("7-Zip 未找到，尝试下载...")
        # 下载 7-Zip 便携版
        import urllib.request
        url = "https://www.7-zip.org/a/7zr.exe"
        seven_zip = str(BUILD_DIR / "7zr.exe")
        urllib.request.urlretrieve(url, seven_zip)
    
    # 压缩
    print("压缩文件...")
    subprocess.run([seven_zip, "a", "-mx=5", str(archive), str(INSTALLER_DIR) + "\\*"], 
                   capture_output=True)
    
    # 创建自解压脚本
    sfx_config = BUILD_DIR / "config.txt"
    sfx_config.write_text(""";!@Install@!UTF-8!
Title="StyleWriter Desktop"
BeginPrompt="是否安装 StyleWriter Desktop？"
ExecuteFile="install.bat"
ExecuteParameters=""
;!@InstallEnd@!
""", encoding='utf-8')
    
    # 合并成自解压包
    output = DIST_DIR / "StyleWriter-Setup.exe"
    
    # 使用 copy 命令合并
    sfx_module = BUILD_DIR / "7zS2.sfx"
    
    # 下载 SFX 模块
    if not sfx_module.exists():
        print("下载 SFX 模块...")
        import urllib.request
        sfx_url = "https://www.7-zip.org/a/7z2301-extra.7z"
        extra_7z = BUILD_DIR / "7z-extra.7z"
        urllib.request.urlretrieve(sfx_url, extra_7z)
        subprocess.run([seven_zip, "e", str(extra_7z), "-o" + str(BUILD_DIR), "7zS2.sfx"], 
                       capture_output=True)
    
    if sfx_module.exists():
        # 合并: SFX + config + archive
        with open(output, 'wb') as out:
            with open(sfx_module, 'rb') as f:
                out.write(f.read())
            with open(sfx_config, 'rb') as f:
                out.write(f.read())
            with open(archive, 'rb') as f:
                out.write(f.read())
        
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"\n安装包创建完成: {output}")
        print(f"大小: {size_mb:.1f} MB")
    else:
        print("SFX 模块下载失败")
        # 回退: 创建 ZIP
        print("创建 ZIP 便携版...")
        zip_file = DIST_DIR / "StyleWriter-Portable.zip"
        shutil.make_archive(str(DIST_DIR / "StyleWriter-Portable"), 'zip', str(INSTALLER_DIR))
        print(f"ZIP 创建完成: {zip_file}")

if __name__ == "__main__":
    DIST_DIR.mkdir(exist_ok=True)
    create_sfx()

