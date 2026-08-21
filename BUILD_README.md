# 构建安装包说明

## 快速构建

```
双击 build.bat
```

## 构建内容

| 组件 | 大小 | 说明 |
|------|------|------|
| Python | ~30MB | 嵌入式版本 |
| 依赖包 | ~500MB | PyTorch等 |
| llama.cpp | ~50MB | CUDA版本 |
| 应用 | ~1MB | StyleWriter |

**注意: 不包含模型，用户自行下载**

## 构建输出

```
dist/
└── StyleWriter-Portable.zip  # 便携版（约 600MB）
```

## 用户使用

### 1. 解压
解压 `StyleWriter-Portable.zip`

### 2. 启动
双击 `StyleWriter.bat`

### 3. 下载模型
从以下地址下载 GGUF 模型:
- HuggingFace: https://huggingface.co/models?search=gguf
- ModelScope: https://modelscope.cn/models?search=gguf

推荐模型:
- Qwen2.5-7B-Instruct-GGUF (~4GB)
- Qwen2.5-1.5B-Instruct-GGUF (~1GB)

### 4. 配置模型
- 将 .gguf 文件放入 `app/models/` 目录
- 或在设置中配置模型完整路径

### 5. 开始使用
输入主题，生成文章

## 创建安装程序（可选）

### 使用 NSIS

1. 安装 NSIS: https://nsis.sourceforge.io/Download
2. 右键 `installer.nsi` -> Compile
3. 生成 `dist\StyleWriter-Setup.exe`

### 使用 Inno Setup

1. 安装 Inno Setup: https://jrsoftware.org/isinfo.php
2. 创建脚本并编译

