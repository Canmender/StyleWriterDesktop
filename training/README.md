# 云端训练指南

## 目录结构

```
training/
├── train_lora.py      # 训练脚本
├── export_gguf.py     # 导出 GGUF 格式
├── requirements.txt   # Python 依赖
├── configs/
│   └── default.yaml   # 训练配置
├── data/
│   └── train.jsonl    # 训练数据（从本地生成后放入）
└── output/            # 训练输出
```

## 使用步骤

### 1. 准备训练数据

在本地程序的"数据管理"中导入示例文章，然后点击"生成训练数据"。

将生成的 `train.jsonl` 上传到 `training/data/` 目录。

### 2. 上传到云端服务器

```bash
# 打包训练目录
tar -czf training.tar.gz training/

# 上传到服务器
scp training.tar.gz user@server:/path/to/

# 在服务器解压
ssh user@server
cd /path/to/
tar -xzf training.tar.gz
cd training
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 开始训练

```bash
python train_lora.py
```

### 5. 导出 GGUF（可选）

```bash
python export_gguf.py --model_dir ./output/final --output model.gguf
```

### 6. 下载模型

```bash
# 下载训练好的模型
scp -r user@server:/path/to/training/output/final ./models/

# 或下载 GGUF 文件
scp user@server:/path/to/training/model.gguf ./models/
```

## 推荐云服务器

| 服务商 | GPU | 价格 |
|--------|-----|------|
| AutoDL | RTX 4090 24GB | ~2元/小时 |
| 恒源云 | A100 40GB | ~4元/小时 |
| 阿里云 | V100 16GB | ~3元/小时 |

## 参数说明

编辑 `configs/default.yaml` 修改训练参数。

