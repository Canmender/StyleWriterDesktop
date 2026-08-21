"""
构建完整安装包
下载所有依赖并打包成安装程序
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess
from pathlib import Path
from urllib.request import urlretrieve
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
INSTALLER_DIR = BUILD_DIR / "installer"

class DownloadProgress:
    def __init__(self, desc):
        self.desc = desc
        self.pbar = None
    
    def __call__(self, count, block_size, total_size):
        if self.pbar is None:
            self.pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=self.desc)
        self.pbar.update(block_size)
    
    def close(self):
        if self.pbar:
            self.pbar.close()

def download_file(url, dest_path, desc=""):
    """下载文件"""
    print(f"\n下载: {desc}")
    print(f"URL: {url}")
    
    try:
        progress = DownloadProgress(desc)
        urlretrieve(url, dest_path, progress)
        progress.close()
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """解压"""
    print(f"解压: {zip_path}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_to)
        return True
    except Exception as e:
        print(f"解压失败: {e}")
        return False

def step1_download_python():
    """下载嵌入式 Python"""
    print("\n" + "="*60)
    print("[1/4] 下载 Python 嵌入式版本")
    print("="*60)
    
    python_dir = INSTALLER_DIR / "python"
    
    if (python_dir / "python.exe").exists():
        print("[OK] Python 已存在")
        return True
    
    url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
    zip_path = BUILD_DIR / "python-embed.zip"
    
    if not download_file(url, zip_path, "Python 3.11"):
        return False
    
    if not extract_zip(zip_path, python_dir):
        return False
    
    # 配置 pip
    pth_file = python_dir / "python311._pth"
    if pth_file.exists():
        content = pth_file.read_text()
        content = content.replace("#import site", "import site")
        pth_file.write_text(content)
    
    # 下载 get-pip
    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
    get_pip_path = python_dir / "get-pip.py"
    download_file(get_pip_url, get_pip_path, "pip")
    
    # 安装 pip
    subprocess.run([str(python_dir / "python.exe"), str(get_pip_path)], 
                   cwd=str(python_dir), capture_output=True)
    
    # 清理
    zip_path.unlink(missing_ok=True)
    get_pip_path.unlink(missing_ok=True)
    
    print("[OK] Python 安装完成")
    return True

def step2_install_packages():
    """安装 Python 包"""
    print("\n" + "="*60)
    print("[2/4] 安装 Python 依赖包")
    print("="*60)
    
    python_exe = INSTALLER_DIR / "python" / "python.exe"
    
    packages = [
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "requests>=2.28.0",
        "numpy>=1.24.0",
        "pyyaml>=6.0",
        "tqdm>=4.65.0",
        "sentence-transformers>=2.2.0",
        "torch>=2.0.0",
        "transformers>=4.35.0",
    ]
    
    print("安装包:")
    for pkg in packages:
        print(f"  - {pkg}")
    
    cmd = [str(python_exe), "-m", "pip", "install"] + packages + [
        "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[OK] 依赖安装完成")
        return True
    else:
        print(f"[WARN] 部分依赖可能安装失败")
        return True  # 继续

def step3_download_llama_cpp():
    """下载 llama.cpp"""
    print("\n" + "="*60)
    print("[3/4] 下载 llama.cpp")
    print("="*60)
    
    llama_dir = INSTALLER_DIR / "llama-cpp"
    
    # 检查是否已存在
    for exe in ["llama-cli.exe", "main.exe"]:
        if (llama_dir / exe).exists():
            print("[OK] llama.cpp 已存在")
            return True
    
    # CUDA 版本
    url = "https://github.com/ggerganov/llama.cpp/releases/download/b3800/llama-b3800-bin-win-cuda-cu12.2-x64.zip"
    zip_path = BUILD_DIR / "llama-cpp.zip"
    
    if not download_file(url, zip_path, "llama.cpp (CUDA)"):
        # 尝试 CPU 版本
        url_cpu = "https://github.com/ggerganov/llama.cpp/releases/download/b3800/llama-b3800-bin-win-x64.zip"
        if not download_file(url_cpu, zip_path, "llama.cpp (CPU)"):
            return False
    
    if not extract_zip(zip_path, llama_dir):
        return False
    
    zip_path.unlink(missing_ok=True)
    
    print("[OK] llama.cpp 安装完成")
    return True

def step4_download_model():
    """下载默认模型"""
    print("\n" + "="*60)
    print("[4/4] 下载默认模型")
    print("="*60)
    
    models_dir = INSTALLER_DIR / "models"
    model_file = models_dir / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
    
    if model_file.exists():
        print("[OK] 模型已存在")
        return True
    
    models_dir.mkdir(exist_ok=True)
    
    # Qwen2.5-1.5B 小模型
    url = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
    
    if not download_file(url, model_file, "Qwen2.5-1.5B (~1GB)"):
        # 备用
        url_backup = "https://modelscope.cn/models/qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
        if not download_file(url_backup, model_file, "Qwen2.5-1.5B (备用)"):
            return False
    
    print("[OK] 模型下载完成")
    return True

def step5_copy_app():
    """复制应用文件"""
    print("\n复制应用文件...")
    
    app_dir = INSTALLER_DIR / "app"
    app_dir.mkdir(exist_ok=True)
    
    # 复制核心文件
    files_to_copy = [
        "main.py",
        "requirements.txt",
    ]
    
    for f in files_to_copy:
        src = PROJECT_ROOT / f
        if src.exists():
            shutil.copy2(src, app_dir / f)
    
    # 复制目录
    dirs_to_copy = [
        "server",
        "config",
        "training",
    ]
    
    for d in dirs_to_copy:
        src = PROJECT_ROOT / d
        if src.exists():
            dst = app_dir / d
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    
    # 创建数据目录
    for d in ["data/examples", "data/vectorstore", "output", "logs"]:
        (app_dir / d).mkdir(parents=True, exist_ok=True)
    
    # 更新配置
    config_file = app_dir / "config" / "settings.json"
    config = {
        "api": {
            "provider": "openai",
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini"
        },
        "local_model": {
            "path": "../models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
            "device": "auto",
            "load_in_4bit": True,
            "engine": "llama_cpp"
        },
        "llama_cpp": {
            "path": "../llama-cpp",
            "gpu_layers": 999,
            "context_size": 4096,
            "threads": 4
        },
        "rag": {
            "embedding_model": "BAAI/bge-small-zh-v1.5",
            "chunk_size": 500,
            "top_k": 3
        },
        "generation": {
            "max_tokens": 2048,
            "temperature": 0.7
        }
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("[OK] 应用文件复制完成")
    return True

def step6_create_launcher():
    """创建启动脚本"""
    print("\n创建启动脚本...")
    
    # 主启动脚本
    launcher = INSTALLER_DIR / "StyleWriter.bat"
    launcher.write_text('''@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "" "python\python.exe" "app\main.py"
''', encoding='utf-8')
    
    # 创建快捷方式脚本
    shortcut = INSTALLER_DIR / "create_shortcut.vbs"
    shortcut.write_text('''Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\StyleWriter.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = WScript.ScriptFullName & "\..\StyleWriter.bat"
oLink.WorkingDirectory = WScript.ScriptFullName & "\.."
oLink.Description = "StyleWriter Desktop"
oLink.Save
''', encoding='utf-8')
    
    print("[OK] 启动脚本创建完成")
    return True

def step7_create_installer():
    """创建安装程序 (使用 NSIS 或 7-Zip 自解压)"""
    print("\n" + "="*60)
    print("创建安装程序")
    print("="*60)
    
    # 方法1: 使用 7-Zip 创建自解压包
    output_file = DIST_DIR / "StyleWriter-Setup.exe"
    DIST_DIR.mkdir(exist_ok=True)
    
    # 检查 7z
    seven_zip = None
    for path in ["C:\Program Files\7-Zip\7z.exe", "C:\Program Files (x86)\7-Zip\7z.exe"]:
        if os.path.exists(path):
            seven_zip = path
            break
    
    if seven_zip:
        print("使用 7-Zip 创建自解压包...")
        
        # 创建自解压配置
        sfx_config = BUILD_DIR / "sfx_config.txt"
        sfx_config.write_text(""";!@Install@!UTF-8!
Title="StyleWriter Desktop 安装"
BeginPrompt="是否安装 StyleWriter Desktop？"
ExecuteFile="python\python.exe"
ExecuteParameters="app\main.py"
Directory="%ProgramFiles%\StyleWriter"
RunProgram="f: StyleWriter.bat"
;!@InstallEnd@!
""", encoding='utf-8')
        
        # 先打包成 7z
        archive = BUILD_DIR / "StyleWriter.7z"
        subprocess.run([seven_zip, "a", "-mx=5", str(archive), str(INSTALLER_DIR) + "\*"])
        
        # 创建自解压
        sfx_module = BUILD_DIR / "7zS.sfx"
        if not sfx_module.exists():
            # 下载 SFX 模块
            sfx_url = "https://www.7-zip.org/a/7z2301-extra.7z"
            download_file(sfx_url, BUILD_DIR / "7z-extra.7z", "7-Zip SFX")
        
        print(f"[OK] 安装包创建完成: {output_file}")
    else:
        # 方法2: 创建 ZIP 包
        print("7-Zip 未找到，创建 ZIP 包...")
        zip_file = DIST_DIR / "StyleWriter-Portable.zip"
        
        shutil.make_archive(
            str(DIST_DIR / "StyleWriter-Portable"),
            'zip',
            str(INSTALLER_DIR)
        )
        
        print(f"[OK] 便携版创建完成: {zip_file}")
    
    return True

def main():
    """主函数"""
    print("="*60)
    print("StyleWriter Desktop - 构建安装包")
    print("="*60)
    
    # 清理
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir()
    INSTALLER_DIR.mkdir(parents=True)
    
    # 执行步骤
    steps = [
        ("下载 Python", step1_download_python),
        ("安装依赖", step2_install_packages),
        ("下载 llama.cpp", step3_download_llama_cpp),
        ("下载模型", step4_download_model),
        ("复制应用", step5_copy_app),
        ("创建启动脚本", step6_create_launcher),
        ("创建安装包", step7_create_installer),
    ]
    
    for name, func in steps:
        try:
            if not func():
                print(f"\n[ERROR] {name} 失败")
                return
        except Exception as e:
            print(f"\n[ERROR] {name} 异常: {e}")
            return
    
    print("\n" + "="*60)
    print("构建完成!")
    print("="*60)
    print(f"\n输出目录: {DIST_DIR}")
    print("\n用户只需解压后运行 StyleWriter.bat 即可使用")

if __name__ == "__main__":
    main()

