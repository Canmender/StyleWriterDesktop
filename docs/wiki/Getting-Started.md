# 快速开始

## 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 操作系统 | Windows 10 64-bit | Windows 11 |
| Python | 3.8+ | 3.11+ |
| 内存 | 4GB | 16GB+ |
| 磁盘空间 | 2GB | 10GB+ |
| GPU | 无（CPU可用） | NVIDIA 8GB+ |

## 安装方式

### 方式一：EXE 安装包（推荐）

1. 从 [Releases](https://github.com/Canmender/StyleWriterDesktop/releases) 下载 `StyleWriter-Setup.exe`
2. 双击运行安装程序
3. 选择安装目录
4. 完成安装，从桌面快捷方式启动

### 方式二：便携版

1. 下载 `StyleWriter-Portable.zip`
2. 解压到任意目录（如 `D:\StyleWriter`）
3. 双击 `StyleWriter.bat` 启动

### 方式三：源码安装

```bash
# 1. 克隆仓库
git clone https://github.com/Canmender/StyleWriterDesktop.git
cd StyleWriterDesktop

# 2. 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行程序
python main.py
```

## 首次配置

### 1. 配置 API（可选）

如果使用云端 API，在设置中配置：

- **API Key**: 你的 API 密钥
- **Base URL**: API 地址
- **Model**: 模型名称

支持的 API 提供商：
| 提供商 | Base URL |
|--------|----------|
| OpenAI | https://api.openai.com/v1 |
| DeepSeek | https://api.deepseek.com/v1 |
| 智谱 | https://open.bigmodel.cn/api/paas/v4 |
| 通义千问 | https://dashscope.aliyuncs.com/compatible-mode/v1 |

### 2. 下载本地模型（可选）

如果使用本地推理，下载 GGUF 格式模型：

1. 访问 https://huggingface.co/models?search=gguf
2. 下载模型文件（如 `qwen2.5-7b-instruct-q4_k_m.gguf`）
3. 将模型放入 `models/` 目录
4. 在设置中配置模型路径

### 3. 导入示例文章

1. 切换到"数据清洗"标签
2. 选择包含示例文章的文件或文件夹
3. 点击"开始清洗"
4. 清洗完成后自动创建向量索引

## 下一步

- [基本使用](Basic-Usage.md) - 学习如何生成文章
- [配置说明](Configuration.md) - 详细配置选项
- [模型指南](Model-Guide.md) - 选择合适的模型

