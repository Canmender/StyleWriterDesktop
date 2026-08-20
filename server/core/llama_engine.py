"""
llama.cpp 推理引擎
支持 CUDA 加速和 GGUF 模型
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent

class LlamaCppEngine:
    """llama.cpp 推理引擎"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.llama_dir = self._find_llama_cpp()
        self.model_path = None
        self.is_loaded = False
        self.gpu_layers = self.config.get("gpu_layers", 999)
        self.context_size = self.config.get("context_size", 4096)
        self.threads = self.config.get("threads", 4)
    
    def _find_llama_cpp(self) -> Optional[Path]:
        """查找 llama.cpp"""
        # 检查配置路径
        config_path = self.config.get("llama_cpp_path", "")
        if config_path and Path(config_path).exists():
            return Path(config_path)
        
        # 检查常见位置
        possible_paths = [
            PROJECT_ROOT / "runtime" / "llama-cpp",
            PROJECT_ROOT / "llama.cpp",
            Path("C:/llama.cpp"),
            Path(os.environ.get("LLAMA_CPP_PATH", "")),
        ]
        
        for path in possible_paths:
            if path.exists():
                # 检查是否有可执行文件
                for exe in ["llama-cli.exe", "main.exe", "llama-cli", "main"]:
                    if (path / exe).exists():
                        return path
        
        return None
    
    def get_executable(self) -> Optional[Path]:
        """获取可执行文件路径"""
        if not self.llama_dir:
            return None
        
        # 按优先级查找
        for exe in ["llama-cli.exe", "main.exe", "llama-cli", "main"]:
            path = self.llama_dir / exe
            if path.exists():
                return path
        
        return None
    
    def is_available(self) -> bool:
        """检查是否可用"""
        return self.get_executable() is not None
    
    def load_model(self, model_path: str) -> bool:
        """加载模型"""
        model_path = Path(model_path)
        
        if not model_path.exists():
            logger.error(f"模型文件不存在: {model_path}")
            return False
        
        if not model_path.suffix.lower() == '.gguf':
            logger.error(f"不支持的模型格式: {model_path.suffix}")
            return False
        
        self.model_path = model_path
        self.is_loaded = True
        logger.info(f"模型已加载: {model_path.name}")
        return True
    
    def generate(self, prompt: str, max_tokens: int = 1024, 
                 temperature: float = 0.7, top_p: float = 0.9,
                 stop: List[str] = None) -> str:
        """生成文本"""
        if not self.is_loaded or not self.model_path:
            raise ValueError("模型未加载")
        
        exe = self.get_executable()
        if not exe:
            raise FileNotFoundError("llama.cpp 未找到")
        
        # 构建命令
        cmd = [
            str(exe),
            "-m", str(self.model_path),
            "-p", prompt,
            "-n", str(max_tokens),
            "--temp", str(temperature),
            "--top-p", str(top_p),
            "--no-display-prompt",
            "-ngl", str(self.gpu_layers),
            "-c", str(self.context_size),
            "-t", str(self.threads),
        ]
        
        # 添加停止词
        if stop:
            for s in stop:
                cmd.extend(["--reverse-prompt", s])
        
        try:
            logger.info(f"开始生成，max_tokens={max_tokens}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                cwd=str(self.llama_dir)
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                # 移除 prompt 回显
                if output.startswith(prompt):
                    output = output[len(prompt):].strip()
                return output
            else:
                error = result.stderr[:500] if result.stderr else "Unknown error"
                logger.error(f"生成失败: {error}")
                raise RuntimeError(f"llama.cpp 错误: {error}")
                
        except subprocess.TimeoutExpired:
            raise TimeoutError("生成超时")
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        if not self.model_path:
            return {}
        
        return {
            "name": self.model_path.name,
            "path": str(self.model_path),
            "size_mb": self.model_path.stat().st_size / (1024 * 1024),
            "gpu_layers": self.gpu_layers,
            "context_size": self.context_size
        }


class CUDAManager:
    """CUDA 管理器"""
    
    @staticmethod
    def is_available() -> bool:
        """检查 CUDA 是否可用"""
        try:
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def get_gpu_info() -> Dict:
        """获取 GPU 信息"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                gpus = []
                for line in lines:
                    parts = line.split(", ")
                    if len(parts) >= 3:
                        gpus.append({
                            "name": parts[0].strip(),
                            "memory_total": parts[1].strip(),
                            "memory_free": parts[2].strip()
                        })
                return {"available": True, "gpus": gpus}
        except:
            pass
        
        return {"available": False, "gpus": []}
    
    @staticmethod
    def get_optimal_gpu_layers(model_size_mb: float) -> int:
        """根据显存计算最优 GPU 层数"""
        gpu_info = CUDAManager.get_gpu_info()
        
        if not gpu_info["available"] or not gpu_info["gpus"]:
            return 0
        
        # 获取可用显存
        free_mem = gpu_info["gpus"][0]["memory_free"]
        if "MiB" in free_mem:
            free_mb = int(free_mem.replace("MiB", "").strip())
        elif "GiB" in free_mem:
            free_mb = int(float(free_mem.replace("GiB", "").strip()) * 1024)
        else:
            free_mb = 8192  # 默认 8GB
        
        # 估算需要的显存（粗略）
        # 4bit 量化模型大约需要模型大小的 0.5-0.6 倍显存
        required_mb = model_size_mb * 0.6
        
        if free_mb > required_mb:
            return 999  # 全部放 GPU
        elif free_mb > required_mb * 0.5:
            return 32  # 部分放 GPU
        else:
            return 0  # 纯 CPU

