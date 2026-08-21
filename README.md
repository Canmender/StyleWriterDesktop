# StyleWriter Desktop

风格化文章生成器 - 混合智能体架构

## 快速开始

### 1. 安装依赖

```
双击 install.bat
```

### 2. 下载运行环境（首次）

```
双击 download.bat
```

这将自动下载:
- llama.cpp (CUDA版，支持 GPU 加速)
- Qwen2.5-1.5B 默认模型 (约 1GB)

### 3. 启动程序

```
双击 run.bat
```

## 功能特性

- **混合智能体**: Agent RAG + 本地/云端模型
- **CUDA 加速**: 自动检测 GPU，智能分配
- **llama.cpp**: 支持 GGUF 模型本地推理
- **数据清洗**: 支持 txt/md/docx/pdf/html/json
- **云端训练**: LoRA 微调脚本

## 项目结构

```
StyleWriterDesktop/
├── main.py              # 主程序
├── run.bat              # 启动程序
├── install.bat          # 安装依赖
├── download.bat         # 下载运行环境
├── download_runtime.py  # 下载脚本
├── server/
│   ├── api/app.py       # FastAPI 服务
│   ├── agent/           # 混合智能体
│   ├── core/            # 核心模块
│   │   ├── llama_engine.py   # llama.cpp 引擎
│   │   └── data_cleaner.py   # 数据清洗
│   └── gui/             # GUI 界面
├── runtime/             # 运行时（自动下载）
│   └── llama-cpp/       # llama.cpp
├── models/              # 模型目录（自动下载）
│   └── *.gguf           # GGUF 模型
├── training/            # 云端训练脚本
└── data/
    ├── examples/        # 示例文章
    └── vectorstore/     # 向量索引
```

## 使用说明

### 生成文章

1. 启动程序
2. 输入文章主题
3. 选择模型（API 或本地）
4. 点击生成

### 数据清洗

1. 切换到"数据清洗"标签
2. 选择文件或文件夹
3. 点击开始清洗
4. 自动创建向量索引

### 使用自己的模型

1. 下载 GGUF 格式模型
2. 在设置中配置模型路径
3. 或将模型放入 `models/` 目录

## 推荐模型

| 模型 | 大小 | 说明 |
|------|------|------|
| Qwen2.5-1.5B | ~1GB | 默认模型，速度快 |
| Qwen2.5-7B | ~4GB | 效果更好 |
| Llama-3.1-8B | ~4.5GB | 英文优秀 |

下载地址: https://huggingface.co/models?search=gguf

## 系统要求

- Windows 10/11 64-bit
- Python 3.8+
- NVIDIA GPU（推荐，用于加速）
- 4GB+ 内存
- 2GB+ 磁盘空间

## 常见问题

**Q: 下载很慢？**
A: 使用代理或从镜像站下载模型

**Q: 没有 GPU 能用吗？**
A: 可以，llama.cpp 支持 CPU 推理

**Q: 如何使用更大的模型？**
A: 下载 GGUF 模型放入 models/ 目录

## 许可证

MIT License

