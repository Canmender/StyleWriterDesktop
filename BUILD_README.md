# 构建安装包说明

## 快速构建

```
双击 build.bat
```

这将自动:
1. 下载 Python 嵌入式版本
2. 安装所有依赖包
3. 下载 llama.cpp (CUDA版)
4. 下载默认模型 (Qwen2.5-1.5B)
5. 打包成便携版

## 构建输出

构建完成后，在 `dist/` 目录会生成:

- `StyleWriter-Portable.zip` - 便携版（解压即用）

## 创建安装程序

### 方法1: 使用 NSIS

1. 安装 NSIS: https://nsis.sourceforge.io/Download
2. 右键 `installer.nsi` -> Compile NSIS Script
3. 生成 `dist\StyleWriter-Setup.exe`

### 方法2: 使用 Inno Setup

1. 安装 Inno Setup: https://jrsoftware.org/isinfo.php
2. 打开 `installer.iss`（需要创建）
3. 编译生成安装程序

## 用户使用

### 便携版
1. 解压 `StyleWriter-Portable.zip`
2. 运行 `StyleWriter.bat`

### 安装版
1. 运行 `StyleWriter-Setup.exe`
2. 按提示安装
3. 从桌面快捷方式启动

## 包含内容

| 组件 | 大小 | 说明 |
|------|------|------|
| Python | ~30MB | 嵌入式版本 |
| 依赖包 | ~500MB | PyTorch等 |
| llama.cpp | ~50MB | CUDA版本 |
| 模型 | ~1GB | Qwen2.5-1.5B |
| 应用 | ~1MB | StyleWriter |

总计约 1.6GB

## 自定义

### 更换模型

1. 下载其他 GGUF 模型
2. 替换 `models/` 目录中的文件
3. 修改 `app/config/settings.json` 中的模型路径

### 更换 llama.cpp

1. 下载其他版本的 llama.cpp
2. 替换 `llama-cpp/` 目录

