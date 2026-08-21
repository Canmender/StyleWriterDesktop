# 常见问题 (FAQ)

## 安装问题

### Q: 安装包无法运行？

**A:** 
1. 确认系统为 Windows 10/11 64-bit
2. 以管理员身份运行
3. 检查杀毒软件是否拦截

### Q: Python 版本不兼容？

**A:** 
- 安装包自带 Python，无需额外安装
- 源码运行需要 Python 3.8+

## 模型问题

### Q: 模型下载很慢？

**A:**
1. 使用镜像站: https://modelscope.cn/models?search=gguf
2. 使用下载工具（如 IDM）
3. 使用代理

### Q: 模型加载失败？

**A:**
1. 确认模型格式为 `.gguf`
2. 检查文件是否完整（未损坏）
3. 检查路径是否正确
4. 尝试减少 `gpu_layers`

### Q: 显存不足？

**A:**
1. 使用更小的模型（如 1.5B）
2. 减少 `gpu_layers`（如设为 32）
3. 使用 4bit 量化模型
4. 设置 `gpu_layers: 0` 使用 CPU

### Q: 生成速度慢？

**A:**
1. 使用 GPU 加速
2. 选择更小的模型
3. 减少 `max_tokens`
4. 减少 `context_size`

## API 问题

### Q: API 调用失败？

**A:**
1. 检查 API Key 是否正确
2. 检查 Base URL 格式
3. 检查网络连接
4. 检查账户余额

### Q: 支持哪些 API？

**A:**
- OpenAI（GPT-4, GPT-3.5）
- DeepSeek
- 智谱（GLM-4）
- 通义千问
- 其他兼容 OpenAI 格式的 API

## 数据问题

### Q: 如何导入数据？

**A:**
1. 切换到"数据清洗"标签
2. 选择文件或文件夹
3. 支持格式: txt, md, docx, pdf, html, json
4. 点击"开始清洗"

### Q: 向量索引创建失败？

**A:**
1. 确认已导入示例文章
2. 检查网络（首次需要下载 Embedding 模型）
3. 减少 `chunk_size`

## 训练问题

### Q: 如何训练自己的模型？

**A:**
1. 在"数据管理"中导出训练数据
2. 上传到 GPU 服务器
3. 运行 `training/train_lora.py`
4. 下载训练好的模型

### Q: 训练需要什么配置？

**A:**
- GPU: NVIDIA 16GB+ 显存
- 推荐: RTX 4090, A100
- 云端: AutoDL, 恒源云

## 其他问题

### Q: 如何更新程序？

**A:**
- 安装包: 下载新版本覆盖安装
- 源码: `git pull` 然后 `pip install -r requirements.txt`

### Q: 如何卸载？

**A:**
- 安装包: 控制面板 -> 卸载程序
- 便携版: 直接删除文件夹

### Q: 数据保存在哪里？

**A:**
- 配置: `config/settings.json`
- 示例: `data/examples/`
- 向量库: `data/vectorstore/`
- 模型: `models/`
- 输出: `output/`

## 获取帮助

- [GitHub Issues](https://github.com/Canmender/StyleWriterDesktop/issues)
- [讨论区](https://github.com/Canmender/StyleWriterDesktop/discussions)

