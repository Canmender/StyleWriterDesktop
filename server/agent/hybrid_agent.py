"""
混合智能体 - 支持本地模型和云端 API
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "config" / "settings.json"

class HybridAgent:
    """混合智能体"""
    
    def __init__(self):
        self.config = self._load_config()
        self.examples = []
        self.vectorstore = None
        self.embeddings = None
        self.local_model = None
        self.local_tokenizer = None
        self.api_configured = bool(self.config.get("api", {}).get("api_key"))
    
    def _load_config(self) -> dict:
        """加载配置"""
        default = {
            "api": {
                "provider": "openai",
                "api_key": "",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o-mini"
            },
            "local_model": {
                "path": "",
                "device": "auto",
                "load_in_4bit": True
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
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    for key in default:
                        if key in saved:
                            default[key].update(saved[key])
                    return default
            except:
                pass
        return default
    
    def save_config(self):
        """保存配置"""
        os.makedirs(CONFIG_FILE.parent, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def initialize(self):
        """初始化"""
        logger.info("初始化 HybridAgent...")
        
        # 加载示例文章
        self._load_examples()
        
        # 尝试加载向量索引
        self._load_vectorstore()
        
        # 如果配置了本地模型，尝试加载
        local_path = self.config.get("local_model", {}).get("path", "")
        if local_path and os.path.exists(local_path):
            self._load_local_model(local_path)
        
        logger.info("HybridAgent 初始化完成")
    
    def reload(self):
        """重新加载"""
        self.config = self._load_config()
        self.api_configured = bool(self.config.get("api", {}).get("api_key"))
        self.initialize()
    
    def _load_examples(self):
        """加载示例文章"""
        examples_dir = PROJECT_ROOT / "data" / "examples"
        if not examples_dir.exists():
            return
        
        self.examples = []
        for f in examples_dir.glob("*.txt"):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
                    if content:
                        self.examples.append({
                            "filename": f.name,
                            "content": content
                        })
            except Exception as e:
                logger.error(f"加载 {f.name} 失败: {e}")
        
        logger.info(f"加载了 {len(self.examples)} 篇示例文章")
    
    def _load_vectorstore(self):
        """加载向量索引"""
        index_dir = PROJECT_ROOT / "data" / "vectorstore"
        vectors_file = index_dir / "vectors.npy"
        chunks_file = index_dir / "chunks.json"
        
        if vectors_file.exists() and chunks_file.exists():
            try:
                import numpy as np
                vectors = np.load(str(vectors_file))
                with open(chunks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.vectorstore = {
                    "vectors": vectors,
                    "chunks": data["chunks"],
                    "metadatas": data["metadatas"]
                }
                logger.info("向量索引加载成功")
            except Exception as e:
                logger.error(f"加载向量索引失败: {e}")
    
    def _load_local_model(self, model_path: str):
        """加载本地模型"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            import torch
            
            logger.info(f"加载本地模型: {model_path}")
            
            # 量化配置
            bnb_config = None
            if self.config["local_model"].get("load_in_4bit"):
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4"
                )
            
            self.local_tokenizer = AutoTokenizer.from_pretrained(
                model_path, trust_remote_code=True
            )
            self.local_model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=bnb_config,
                device_map=self.config["local_model"].get("device", "auto"),
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            logger.info("本地模型加载成功")
            
        except Exception as e:
            logger.error(f"加载本地模型失败: {e}")
            self.local_model = None
    
    def create_index(self):
        """创建向量索引"""
        if not self.examples:
            raise ValueError("没有示例文章")
        
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            
            model_name = self.config["rag"]["embedding_model"]
            logger.info(f"加载 embedding 模型: {model_name}")
            self.embeddings = SentenceTransformer(model_name)
            
            chunk_size = self.config["rag"]["chunk_size"]
            chunks = []
            metadatas = []
            
            for example in self.examples:
                content = example["content"]
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i + chunk_size]
                    if len(chunk) > 50:
                        chunks.append(chunk)
                        metadatas.append({"filename": example["filename"]})
            
            if not chunks:
                raise ValueError("没有有效的文本块")
            
            logger.info(f"编码 {len(chunks)} 个文本块...")
            vectors = self.embeddings.encode(chunks, show_progress_bar=True)
            
            index_dir = PROJECT_ROOT / "data" / "vectorstore"
            index_dir.mkdir(exist_ok=True)
            
            np.save(str(index_dir / "vectors.npy"), vectors)
            with open(index_dir / "chunks.json", 'w', encoding='utf-8') as f:
                json.dump({"chunks": chunks, "metadatas": metadatas}, f, ensure_ascii=False)
            
            self.vectorstore = {
                "vectors": vectors,
                "chunks": chunks,
                "metadatas": metadatas
            }
            
            logger.info(f"向量索引创建完成，共 {len(chunks)} 个文本块")
            
        except ImportError:
            raise ImportError("请安装 sentence-transformers")
    
    def search(self, query: str, top_k: int = None) -> List[dict]:
        """检索相似内容"""
        if top_k is None:
            top_k = self.config["rag"]["top_k"]
        
        if self.vectorstore is None:
            return [{"content": ex["content"][:500], "filename": ex["filename"]} for ex in self.examples[:top_k]]
        
        try:
            import numpy as np
            
            if self.embeddings is None:
                from sentence_transformers import SentenceTransformer
                self.embeddings = SentenceTransformer(self.config["rag"]["embedding_model"])
            
            query_vector = self.embeddings.encode([query])[0]
            vectors = self.vectorstore["vectors"]
            similarities = np.dot(vectors, query_vector) / (
                np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vector)
            )
            
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                results.append({
                    "content": self.vectorstore["chunks"][idx],
                    "filename": self.vectorstore["metadatas"][idx]["filename"],
                    "score": float(similarities[idx])
                })
            
            return results
            
        except Exception as e:
            logger.error(f"检索失败: {e}")
            return [{"content": ex["content"][:500], "filename": ex["filename"]} for ex in self.examples[:top_k]]
    
    def generate(self, topic: str, length: int = 1000, requirements: str = "", 
                 style: str = "default", use_model: str = "api") -> dict:
        """生成文章"""
        # 获取参考内容
        references = self.search(topic)
        
        # 构建 prompt
        prompt = self._build_prompt(topic, length, requirements, references)
        
        # 选择模型生成
        if use_model == "local" and self.local_model:
            content = self._generate_local(prompt)
            model_used = "local"
        else:
            content = self._generate_api(prompt)
            model_used = "api"
        
        return {
            "content": content,
            "word_count": len(content),
            "style_score": 8.0,  # 简化评分
            "model_used": model_used
        }
    
    def _build_prompt(self, topic: str, length: int, requirements: str, references: List[dict]) -> str:
        """构建 prompt"""
        ref_text = ""
        if references:
            ref_text = "\n\n## 参考风格\n"
            for i, ref in enumerate(references[:3], 1):
                ref_text += f"\n### 示例 {i}\n{ref['content'][:300]}...\n"
        
        return f"""你是一位风格化写作专家。请参考以下示例文章的写作风格，撰写一篇新文章。

{ref_text}

## 写作任务
- 主题：{topic}
- 目标字数：约 {length} 字
- 写作要求：{requirements or '通俗易懂，有条理'}

请直接输出文章内容，不要添加任何说明。"""
    
    def _generate_local(self, prompt: str) -> str:
        """使用本地模型生成"""
        try:
            import torch
            
            inputs = self.local_tokenizer(prompt, return_tensors="pt").to(self.local_model.device)
            
            with torch.no_grad():
                outputs = self.local_model.generate(
                    **inputs,
                    max_new_tokens=self.config["generation"]["max_tokens"],
                    temperature=self.config["generation"]["temperature"],
                    do_sample=True,
                    top_p=0.9
                )
            
            response = self.local_tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response[len(prompt):].strip()
            
        except Exception as e:
            logger.error(f"本地生成失败: {e}")
            raise
    
    def _generate_api(self, prompt: str) -> str:
        """使用云端 API 生成"""
        import requests
        
        api_config = self.config["api"]
        api_key = api_config.get("api_key", "")
        
        if not api_key:
            raise ValueError("请先配置 API Key")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": api_config["model"],
            "messages": [
                {"role": "system", "content": "你是一位风格化写作专家。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config["generation"]["max_tokens"],
            "temperature": self.config["generation"]["temperature"]
        }
        
        response = requests.post(
            f"{api_config['base_url']}/chat/completions",
            headers=headers,
            json=data,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"API 调用失败: {response.status_code}")
        
        return response.json()["choices"][0]["message"]["content"]

