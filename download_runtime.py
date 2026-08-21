"""
一键下载脚本
下载 llama.cpp 和默认模型到项目中
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
RUNTIME_DIR = PROJECT_ROOT / "runtime"
MODELS_DIR = PROJECT_ROOT / "models"

class DownloadProgress:
    """下载进度条"""
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
    print(f"\n正在下载: {desc or url}")
    print(f"目标: {dest_path}")
    
    try:
        progress = DownloadProgress(desc)
        urlretrieve(url, dest_path, progress)
        progress.close()
        print(f"[OK] 下载完成")
        return True
    except Exception as e:
        print(f"[ERROR] 下载失败: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """解压 ZIP"""
    print(f"\n正在解压: {zip_path}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_to)
        print(f"[OK] 解压完成")
        return True
    except Exception as e:
        print(f"[ERROR] 解压失败: {e}")
        return False

def download_llama_cpp():
    """下载 llama.cpp"""
    llama_dir = RUNTIME_DIR / "llama-cpp"
    
    # 检查是否已存在
    for exe in ["llama-cli.exe", "main.exe"]:
        if (llama_dir / exe).exists():
            print("[OK] llama.cpp 已存在")
            return True
    
    print("\n" + "="*50)
    print("下载 llama.cpp")
    print("="*50)
    
    # 下载 URL (Windows CUDA 版本)
    url = "https://github.com/ggerganov/llama.cpp/releases/download/b3800/llama-b3800-bin-win-cuda-cu12.2-x64.zip"
    zip_path = RUNTIME_DIR / "llama-cpp.zip"
    
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    
    if not download_file(url, zip_path, "llama.cpp (CUDA版)"):
        # 尝试 CPU 版本
        url_cpu = "https://github.com/ggerganov/llama.cpp/releases/download/b3800/llama-b3800-bin-win-x64.zip"
        if not download_file(url_cpu, zip_path, "llama.cpp (CPU版)"):
            return False
    
    if not extract_zip(zip_path, llama_dir):
        return False
    
    # 清理
    if zip_path.exists():
        zip_path.unlink()
    
    # 验证
    for exe in ["llama-cli.exe", "main.exe"]:
        if (llama_dir / exe).exists():
            print("[OK] llama.cpp 安装成功")
            return True
    
    print("[ERROR] llama.cpp 安装失败")
    return False

def download_model():
    """下载默认模型"""
    model_file = MODELS_DIR / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
    
    if model_file.exists():
        print("[OK] 默认模型已存在")
        return True
    
    print("\n" + "="*50)
    print("下载默认模型")
    print("="*50)
    print("模型: Qwen2.5-1.5B-Instruct (Q4_K_M, ~1GB)")
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 使用较小的模型作为默认
    url = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
    
    if not download_file(url, model_file, "Qwen2.5-1.5B-Instruct"):
        # 备用链接
        url_backup = "https://modelscope.cn/models/qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
        if not download_file(url_backup, model_file, "Qwen2.5-1.5B-Instruct (备用)"):
            return False
    
    print("[OK] 模型下载成功")
    return True

def update_config():
    """更新配置文件"""
    config_file = PROJECT_ROOT / "config" / "settings.json"
    
    # 读取现有配置
    config = {}
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # 更新 llama.cpp 路径
    llama_dir = RUNTIME_DIR / "llama-cpp"
    if llama_dir.exists():
        if "llama_cpp" not in config:
            config["llama_cpp"] = {}
        config["llama_cpp"]["path"] = str(llama_dir)
    
    # 更新模型路径
    model_file = MODELS_DIR / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
    if model_file.exists():
        if "local_model" not in config:
            config["local_model"] = {}
        config["local_model"]["path"] = str(model_file)
        config["local_model"]["engine"] = "llama_cpp"
    
    # 保存配置
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("[OK] 配置已更新")

def main():
    """主函数"""
    print("="*60)
    print("StyleWriter Desktop - 环境配置脚本")
    print("="*60)
    print("\n此脚本将下载以下组件:")
    print("1. llama.cpp (CUDA版, ~50MB)")
    print("2. Qwen2.5-1.5B-Instruct 模型 (~1GB)")
    print("\n注意: 首次下载需要网络连接")
    print("="*60)
    
    input("\n按 Enter 开始下载...")
    
    # 下载 llama.cpp
    print("\n[1/2] 下载 llama.cpp...")
    llama_ok = download_llama_cpp()
    
    # 下载模型
    print("\n[2/2] 下载模型...")
    model_ok = download_model()
    
    # 更新配置
    if llama_ok or model_ok:
        print("\n更新配置...")
        update_config()
    
    # 完成
    print("\n" + "="*60)
    print("配置完成!")
    print("="*60)
    
    if llama_ok:
        print("\n[OK] llama.cpp 已就绪")
    else:
        print("\n[WARN] llama.cpp 下载失败，请手动下载")
    
    if model_ok:
        print("[OK] 默认模型已就绪")
    else:
        print("[WARN] 模型下载失败，请手动下载 GGUF 模型")
    
    print("\n现在可以运行 run.bat 启动程序")

if __name__ == "__main__":
    main()

