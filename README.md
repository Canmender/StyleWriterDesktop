# StyleWriter Desktop

<p align="center">
  <strong>风格化文章生成器 - 混合智能体架构</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="Version">
</p>

---

## 📖 简介

StyleWriter Desktop 是一款基于混合智能体架构的风格化文章生成器。支持本地模型推理（llama.cpp + CUDA 加速）和云端 API 调用，通过 RAG 检索实现风格迁移。

## ✨ 功能特性

- 🤖 **混合智能体** - Agent RAG + 本地/云端模型
- ⚡ **CUDA 加速** - 自动检测 GPU，智能分配显存
- 🔧 **llama.cpp** - 支持 GGUF 模型本地推理
- 📊 **数据清洗** - 支持 txt/md/docx/pdf/html/json
- ☁️ **云端训练** - LoRA 微调脚本（Ubuntu）
- 🌐 **API 服务** - FastAPI 接口，支持外部调用

## 🚀 快速开始

### 方式一：安装包（推荐）

1. 下载 [`StyleWriter-Setup.exe`](https://github.com/Canmender/StyleWriterDesktop/releases)
2. 双击安装
3. 从桌面快捷方式启动

### 方式二：便携版

1. 下载 `StyleWriter-Portable.zip`
2. 解压到任意目录
3. 双击 `StyleWriter.bat`

### 方式三：源码运行

```bash
# 克隆仓库
git clone https://github.com/Canmender/StyleWriterDesktop.git
cd StyleWriterDesktop

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## 📥 下载模型

程序启动后需要配置模型才能使用本地推理：

| 模型 | 大小 | 说明 |
|------|------|------|
| [Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) | ~1GB | 轻量快速 |
| [Qwen2.5-7B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF) | ~4GB | 效果优秀 |
| [Llama-3.1-8B-Instruct-GGUF](https://huggingface.co/bartowski/Llama-3.1-8B-Instruct-GGUF) | ~4.5GB | 英文强大 |

**下载地址：**
- HuggingFace: https://huggingface.co/models?search=gguf
- ModelScope: https://modelscope.cn/models?search=gguf

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    客户端                                 │
│               (GUI / API / Web)                          │
└─────────────────────────────────────────────────────────┘
                        ↓ HTTP API
┌─────────────────────────────────────────────────────────┐
│                  API 网关 (FastAPI)                       │
│                  http://localhost:8000                    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              混合智能体服务 (HybridAgent)                  │
│  ┌─────────┐  ┌──────────┐  ┌─────────────┐            │
│  │ Agent   │→ │ 模型选择  │→ │ 后处理器    │            │
│  │ (RAG)   │  │ API/本地  │  │             │            │
│  └─────────┘  └──────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   存储层                                  │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ 向量数据库   │  │ 模型权重     │                     │
│  │ (FAISS)      │  │ (GGUF/LoRA)  │                     │
│  └──────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
StyleWriterDesktop/
├── main.py                    # 主程序入口
├── run.bat                    # 启动脚本
├── install.bat                # 安装依赖
├── build.bat                  # 构建安装包
├── requirements.txt           # 依赖列表
├── README.md                  # 项目文档
├── LICENSE                    # MIT 许可证
│
├── server/                    # 服务端
│   ├── api/
│   │   └── app.py             # FastAPI 服务
│   ├── agent/
│   │   └── hybrid_agent.py    # 混合智能体
│   ├── core/
│   │   ├── llama_engine.py    # llama.cpp 引擎
│   │   └── data_cleaner.py    # 数据清洗
│   └── gui/
│       └── main_window.py     # GUI 界面
│
├── config/
│   ├── settings.json          # 运行配置
│   └── settings.example.json  # 配置示例
│
├── data/
│   ├── examples/              # 示例文章
│   ├── vectorstore/           # 向量索引
│   └── models/                # 本地模型
│
├── training/                  # 云端训练
│   ├── train_lora.py          # LoRA 训练脚本
│   ├── export_gguf.py         # 导出 GGUF
│   ├── requirements.txt       # 训练依赖
│   └── configs/
│       └── default.yaml       # 训练配置
│
├── build/                     # 构建目录
├── dist/                      # 输出目录
│   └── StyleWriter-Setup.exe  # 安装包
│
└── docs/                      # 文档
    └── wiki/                  # Wiki
```

## ⚙️ 配置说明

配置文件: `config/settings.json`

```json
{
  "api": {
    "provider": "openai",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4o-mini"
  },
  "local_model": {
    "path": "models/your-model.gguf",
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
    "top_k": 3
  },
  "generation": {
    "max_tokens": 2048,
    "temperature": 0.7
  }
}
```

### 配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `api.provider` | API 提供商 | openai |
| `api.api_key` | API 密钥 | - |
| `api.base_url` | API 地址 | https://api.openai.com/v1 |
| `local_model.path` | 模型路径 | - |
| `local_model.engine` | 推理引擎 | auto |
| `llama_cpp.gpu_layers` | GPU 层数 | 999 |
| `llama_cpp.context_size` | 上下文大小 | 4096 |
| `rag.embedding_model` | Embedding 模型 | BAAI/bge-small-zh-v1.5 |
| `rag.top_k` | 检索数量 | 3 |

## 🔌 API 接口

启动后访问: http://localhost:8000

### 生成文章

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "人工智能的未来发展",
    "length": 1000,
    "requirements": "通俗易懂",
    "use_model": "api"
  }'
```

### 检索参考

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "科技风格", "top_k": 3}'
```

### 服务状态

```bash
curl http://localhost:8000/api/status
```

## ☁️ 云端训练

训练脚本在 `training/` 目录，可上传到 Ubuntu GPU 服务器执行。

### 快速步骤

```bash
# 1. 本地生成训练数据
# 在 GUI 的"数据管理"中导出

# 2. 上传到服务器
scp -r training/ user@server:/path/to/

# 3. 在服务器执行
ssh user@server
cd training
pip install -r requirements.txt
python train_lora.py

# 4. 下载训练好的模型
scp -r user@server:/path/to/training/output/final ./models/
```

### 训练参数

编辑 `training/configs/default.yaml`:

```yaml
model:
  name: "Qwen/Qwen2.5-7B-Instruct"

training:
  epochs: 3
  batch_size: 4
  learning_rate: 2e-4

lora:
  r: 16
  alpha: 32
```

## 🛠️ 开发指南

### 环境搭建

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install pytest black flake8
```

### 运行测试

```bash
pytest tests/
```

### 构建安装包

```bash
# 方式一: 便携版
python build_simple.py

# 方式二: EXE 安装包
python build_installer.py
```

### 代码规范

```bash
# 格式化
black .

# 检查
flake8 .
```

## 📋 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 系统 | Windows 10 64-bit | Windows 11 |
| Python | 3.8+ | 3.11+ |
| 内存 | 4GB | 16GB+ |
| 磁盘 | 2GB | 10GB+ |
| GPU | 无（CPU可用） | NVIDIA 8GB+ |

## ❓ 常见问题

### Q: 启动报错 "No module named xxx"

```bash
pip install -r requirements.txt
```

### Q: CUDA 不可用

1. 检查 NVIDIA 驱动: `nvidia-smi`
2. 安装 CUDA Toolkit: https://developer.nvidia.com/cuda-downloads

### Q: 模型加载失败

1. 确认模型格式为 GGUF
2. 检查模型路径是否正确
3. 尝试减少 `gpu_layers`

### Q: 生成速度慢

1. 使用 GPU 加速
2. 选择更小的模型（如 1.5B）
3. 减少 `max_tokens`

### Q: API 调用失败

1. 检查 API Key 是否正确
2. 检查网络连接
3. 确认 Base URL 格式

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/xxx`
3. 提交更改: `git commit -m 'feat: add xxx'`
4. 推送分支: `git push origin feature/xxx`
5. 提交 Pull Request

### 提交规范

- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `test:` 测试
- `chore:` 构建/工具

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 🔗 相关链接

- [GitHub 仓库](https://github.com/Canmender/StyleWriterDesktop)
- [问题反馈](https://github.com/Canmender/StyleWriterDesktop/issues)
- [Wiki 文档](https://github.com/Canmender/StyleWriterDesktop/wiki)

## 📞 联系方式

- GitHub: [@Canmender](https://github.com/Canmender)

---

<p align="center">
  如果觉得有用，请给个 ⭐ Star 支持一下！
</p>

