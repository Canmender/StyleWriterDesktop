"""
导出 GGUF 格式脚本
"""

import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="导出模型为 GGUF 格式")
    parser.add_argument("--model_dir", type=str, required=True, help="模型目录")
    parser.add_argument("--output", type=str, default="model.gguf", help="输出文件名")
    parser.add_argument("--outtype", type=str, default="q4_0", help="量化类型")
    args = parser.parse_args()
    
    print("="*50)
    print("导出 GGUF 格式")
    print("="*50)
    print(f"模型目录: {args.model_dir}")
    print(f"输出文件: {args.output}")
    print(f"量化类型: {args.outtype}")
    
    # 克隆 llama.cpp（如果不存在）
    if not os.path.exists("llama.cpp"):
        print("\n克隆 llama.cpp...")
        subprocess.run(["git", "clone", "https://github.com/ggerganov/llama.cpp.git"])
    
    # 转换
    print("\n转换模型...")
    cmd = [
        sys.executable,
        "llama.cpp/convert_hf_to_gguf.py",
        args.model_dir,
        "--outfile", args.output,
        "--outtype", args.outtype
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"\n导出成功: {args.output}")
    else:
        print("\n导出失败")
        sys.exit(1)

if __name__ == "__main__":
    main()

