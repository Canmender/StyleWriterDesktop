# 配置说明

配置文件位置: `config/settings.json`

## 完整配置示例

```json
{
  "api": {
    "provider": "openai",
    "api_key": "sk-xxx",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4o-mini"
  },
  "local_model": {
    "path": "models/qwen2.5-7b-instruct-q4_k_m.gguf",
    "device": "auto",
    "load_in_4bit": true,
    "engine": "auto"
  },
  "llama_cpp": {
    "path": "llama-cpp",
    "gpu_layers": 999,
    "context_size": 4096,
    "threads": 4
  },
  "rag": {
    "embedding_model": "BAAI/bge-small-zh-v1.5",
    "chunk_size": 500,
    "chunk_overlap": 50,
    "top_k": 3
  },
  "generation": {
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

## 配置项详解

### API 配置

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `provider` | string | API 提供商 | openai |
| `api_key` | string | API 密钥 | - |
| `base_url` | string | API 地址 | https://api.openai.com/v1 |
| `model` | string | 模型名称 | gpt-4o-mini |

### 本地模型配置

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `path` | string | 模型文件路径 | - |
| `device` | string | 计算设备 | auto |
| `load_in_4bit` | bool | 4bit 量化 | true |
| `engine` | string | 推理引擎 | auto |

**engine 选项：**
- `auto`: 自动选择（GGUF 用 llama.cpp，其他用 transformers）
- `llama_cpp`: 强制使用 llama.cpp
- `transformers`: 强制使用 transformers

### llama.cpp 配置

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `path` | string | llama.cpp 目录 | - |
| `gpu_layers` | int | GPU 层数 | 999 |
| `context_size` | int | 上下文大小 | 4096 |
| `threads` | int | CPU 线程数 | 4 |

**gpu_layers 说明：**
- `999`: 全部放 GPU（需要足够显存）
- `32`: 部分放 GPU
- `0`: 纯 CPU 推理

### RAG 配置

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `embedding_model` | string | Embedding 模型 | BAAI/bge-small-zh-v1.5 |
| `chunk_size` | int | 分块大小 | 500 |
| `chunk_overlap` | int | 重叠长度 | 50 |
| `top_k` | int | 检索数量 | 3 |

### 生成配置

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `max_tokens` | int | 最大生成长度 | 2048 |
| `temperature` | float | 温度（创造性） | 0.7 |
| `top_p` | float | Top P 采样 | 0.9 |

## 环境变量

也可以通过环境变量覆盖配置：

```bash
set STYLEWRITER_API_KEY=sk-xxx
set STYLEWRITER_MODEL=gpt-4
```

## 配置优先级

1. 环境变量
2. `config/settings.json`
3. 默认值

