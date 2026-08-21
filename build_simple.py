"""
构建安装包（简化版）
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
INSTALLER_DIR = BUILD_DIR / "installer"

def download_file(url, dest_path, desc=""):
    """下载文件"""
    print(f"\n下载: {desc}")
    try:
        from urllib.request import urlretrieve
        from tqdm import tqdm
        
        class Progress:
            def __init__(self):
                self.pbar = None
            def __call__(self, count, block_size, total_size):
                if self.pbar is None:
                    self.pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=desc)
                self.pbar.update(block_size)
            def close(self):
                if self.pbar:
                    self.pbar.close()
        
        p = Progress()
        urlretrieve(url, dest_path, p)
        p.close()
        print(f"[OK] 下载完成")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

def extract_zip(zip_path, extract_to):
    """解压"""
    print(f"解压: {zip_path}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_to)
        print("[OK] 解压完成")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

def main():
    print("="*60)
    print("StyleWriter Desktop - 构建安装包")
    print("="*60)
    
    # 清理
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir()
    INSTALLER_DIR.mkdir(parents=True)
    
    # Step 1: 下载 Python
    print("\n[1/3] 下载 Python...")
    python_dir = INSTALLER_DIR / "python"
    
    if not (python_dir / "python.exe").exists():
        url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
        zip_path = BUILD_DIR / "python.zip"
        
        if download_file(url, zip_path, "Python 3.11"):
            extract_zip(zip_path, python_dir)
            
            # 配置 pip
            pth = python_dir / "python311._pth"
            if pth.exists():
                pth.write_text(pth.read_text().replace("#import site", "import site"))
            
            # 安装 pip
            get_pip = python_dir / "get-pip.py"
            download_file("https://bootstrap.pypa.io/get-pip.py", get_pip, "pip")
            subprocess.run([str(python_dir / "python.exe"), str(get_pip)], 
                          cwd=str(python_dir), capture_output=True)
            
            zip_path.unlink(missing_ok=True)
            get_pip.unlink(missing_ok=True)
    else:
        print("[OK] Python 已存在")
    
    # Step 2: 安装依赖
    print("\n[2/3] 安装依赖...")
    python_exe = python_dir / "python.exe"
    
    packages = [
        "fastapi", "uvicorn", "pydantic", "requests", 
        "numpy", "pyyaml", "tqdm", "sentence-transformers",
        "torch", "transformers"
    ]
    
    cmd = [str(python_exe), "-m", "pip", "install"] + packages + [
        "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "-q"
    ]
    subprocess.run(cmd, capture_output=True)
    print("[OK] 依赖安装完成")
    
    # Step 3: 复制应用
    print("\n[3/3] 复制应用...")
    app_dir = INSTALLER_DIR / "app"
    app_dir.mkdir(exist_ok=True)
    
    # 复制文件
    for f in ["main.py", "requirements.txt"]:
        src = PROJECT_ROOT / f
        if src.exists():
            shutil.copy2(src, app_dir / f)
    
    for d in ["server", "config", "training"]:
        src = PROJECT_ROOT / d
        if src.exists():
            dst = app_dir / d
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    
    # 创建目录
    for d in ["data/examples", "data/vectorstore", "models", "output", "logs"]:
        (app_dir / d).mkdir(parents=True, exist_ok=True)
    
    # 配置
    config = {
        "api": {"provider": "openai", "api_key": "", "base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
        "local_model": {"path": "", "device": "auto", "load_in_4bit": True, "engine": "auto"},
        "llama_cpp": {"path": "", "gpu_layers": 999, "context_size": 4096, "threads": 4},
        "rag": {"embedding_model": "BAAI/bge-small-zh-v1.5", "chunk_size": 500, "top_k": 3},
        "generation": {"max_tokens": 2048, "temperature": 0.7}
    }
    
    with open(app_dir / "config" / "settings.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # 创建启动脚本
    launcher = INSTALLER_DIR / "StyleWriter.bat"
    launcher.write_text('@echo off\ncd /d "%~dp0"\nstart "" "python\\python.exe" "app\\main.py"\n', encoding='utf-8')
    
    # 创建模型下载说明
    readme = INSTALLER_DIR / "README.txt"
    readme.write_text("""StyleWriter Desktop

1. 双击 StyleWriter.bat 启动
2. 在设置中配置 API 或下载 GGUF 模型

模型下载:
https://huggingface.co/models?search=gguf
https://modelscope.cn/models?search=gguf
""", encoding='utf-8')
    
    print("[OK] 应用复制完成")
    
    # 打包
    print("\n打包中...")
    DIST_DIR.mkdir(exist_ok=True)
    
    zip_file = DIST_DIR / "StyleWriter-Portable.zip"
    shutil.make_archive(str(DIST_DIR / "StyleWriter-Portable"), 'zip', str(INSTALLER_DIR))
    
    size_mb = zip_file.stat().st_size / (1024 * 1024)
    
    print("\n" + "="*60)
    print("构建完成!")
    print("="*60)
    print(f"\n输出: {zip_file}")
    print(f"大小: {size_mb:.1f} MB")
    print("\n用户使用:")
    print("1. 解压 ZIP")
    print("2. 双击 StyleWriter.bat")

if __name__ == "__main__":
    main()

