"""
构建完整安装包
下载所有依赖并打包（不含模型，用户自选）
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
    print("[1/3] 下载 Python 嵌入式版本")
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
    
    subprocess.run([str(python_dir / "python.exe"), str(get_pip_path)], 
                   cwd=str(python_dir), capture_output=True)
    
    zip_path.unlink(missing_ok=True)
    get_pip_path.unlink(missing_ok=True)
    
    print("[OK] Python 安装完成")
    return True

def step2_install_packages():
    """安装 Python 包"""
    print("\n" + "="*60)
    print("[2/3] 安装 Python 依赖包")
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
    else:
        print("[WARN] 部分依赖可能安装失败，继续...")
    
    return True

def step3_download_llama_cpp():
    """下载 llama.cpp"""
    print("\n" + "="*60)
    print("[3/3] 下载 llama.cpp")
    print("="*60)
    
    llama_dir = INSTALLER_DIR / "llama-cpp"
    
    for exe in ["llama-cli.exe", "main.exe"]:
        if (llama_dir / exe).exists():
            print("[OK] llama.cpp 已存在")
            return True
    
    # CUDA 版本
    url = "https://github.com/ggerganov/llama.cpp/releases/download/b3800/llama-b3800-bin-win-cuda-cu12.2-x64.zip"
    zip_path = BUILD_DIR / "llama-cpp.zip"
    
    if not download_file(url, zip_path, "llama.cpp (CUDA)"):
        url_cpu = "https://github.com/ggerganov/llama.cpp/releases/download/b3800/llama-b3800-bin-win-x64.zip"
        if not download_file(url_cpu, zip_path, "llama.cpp (CPU)"):
            return False
    
    if not extract_zip(zip_path, llama_dir):
        return False
    
    zip_path.unlink(missing_ok=True)
    
    print("[OK] llama.cpp 安装完成")
    return True

def step4_copy_app():
    """复制应用文件"""
    print("\n复制应用文件...")
    
    app_dir = INSTALLER_DIR / "app"
    app_dir.mkdir(exist_ok=True)
    
    # 复制核心文件
    for f in ["main.py", "requirements.txt"]:
        src = PROJECT_ROOT / f
        if src.exists():
            shutil.copy2(src, app_dir / f)
    
    # 复制目录
    for d in ["server", "config", "training"]:
        src = PROJECT_ROOT / d
        if src.exists():
            dst = app_dir / d
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    
    # 创建数据目录
    for d in ["data/examples", "data/vectorstore", "models", "output", "logs"]:
        (app_dir / d).mkdir(parents=True, exist_ok=True)
    
    # 更新配置（不设置默认模型）
    config_file = app_dir / "config" / "settings.json"
    config = {
        "api": {
            "provider": "openai",
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini"
        },
        "local_model": {
            "path": "",
            "device": "auto",
            "load_in_4bit": True,
            "engine": "auto"
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

def step5_create_launcher():
    """创建启动脚本"""
    print("\n创建启动脚本...")
    
    # 主启动脚本
    launcher = INSTALLER_DIR / "StyleWriter.bat"
    launcher.write_text('''@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "" "python\python.exe" "app\main.py"
''', encoding='utf-8')
    
    # 模型下载说明
    readme = INSTALLER_DIR / "下载模型说明.txt"
    readme.write_text("""StyleWriter Desktop - 模型下载说明

========================================
首次使用请下载 GGUF 模型
========================================

推荐模型下载地址:
1. HuggingFace: https://huggingface.co/models?search=gguf
2. ModelScope: https://modelscope.cn/models?search=gguf

推荐模型:
- Qwen2.5-7B-Instruct-GGUF (约4GB，效果好)
- Qwen2.5-1.5B-Instruct-GGUF (约1GB，速度快)
- Llama-3.1-8B-Instruct-GGUF (约4.5GB，英文强)

========================================
使用方法
========================================

方法一: 放入 models 目录
1. 下载 .gguf 文件
2. 放入 app/models/ 目录
3. 启动程序，在设置中选择模型

方法二: 任意位置
1. 下载 .gguf 文件
2. 启动程序
3. 在设置中配置模型完整路径

========================================
""", encoding='utf-8')
    
    print("[OK] 启动脚本创建完成")
    return True

def step6_create_package():
    """创建安装包"""
    print("\n" + "="*60)
    print("创建安装包")
    print("="*60)
    
    DIST_DIR.mkdir(exist_ok=True)
    
    # 创建 ZIP 便携版
    zip_file = DIST_DIR / "StyleWriter-Portable.zip"
    
    print("打包中...")
    shutil.make_archive(
        str(DIST_DIR / "StyleWriter-Portable"),
        'zip',
        str(INSTALLER_DIR)
    )
    
    size_mb = zip_file.stat().st_size / (1024 * 1024)
    print(f"[OK] 便携版创建完成: {zip_file}")
    print(f"     大小: {size_mb:.1f} MB")
    
    return True

def main():
    """主函数"""
    print("="*60)
    print("StyleWriter Desktop - 构建安装包")
    print("="*60)
    print("\n构建内容:")
    print("  - Python 嵌入式版本")
    print("  - 依赖包 (PyTorch, transformers 等)")
    print("  - llama.cpp (CUDA版)")
    print("  - 应用程序")
    print("\n注意: 不包含模型，用户自行下载")
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
        ("复制应用", step4_copy_app),
        ("创建启动脚本", step5_create_launcher),
        ("创建安装包", step6_create_package),
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
    print(f"\n输出: {DIST_DIR / 'StyleWriter-Portable.zip'}")
    print("\n用户使用方法:")
    print("1. 解压 ZIP")
    print("2. 运行 StyleWriter.bat")
    print("3. 下载 GGUF 模型")
    print("4. 开始使用")

if __name__ == "__main__":
    main()

