"""
LoRA 训练脚本
在云端 Linux GPU 服务器运行
"""

import os
import yaml
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset

def load_config(config_path="configs/default.yaml"):
    """加载配置"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    # 加载配置
    config = load_config()
    
    print("="*50)
    print("StyleWriter LoRA 训练")
    print("="*50)
    print(f"模型: {config['model']['name']}")
    print(f"训练轮数: {config['training']['epochs']}")
    print(f"批次大小: {config['training']['batch_size']}")
    print(f"学习率: {config['training']['learning_rate']}")
    print(f"LoRA Rank: {config['lora']['r']}")
    print("="*50)
    
    # 检查 GPU
    if not torch.cuda.is_available():
        print("警告: 未检测到 GPU，训练将非常缓慢")
    else:
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # 量化配置
    bnb_config = None
    if config['quantization']['enabled']:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4"
        )
    
    # 加载模型
    print("\n加载模型...")
    model = AutoModelForCausalLM.from_pretrained(
        config['model']['name'],
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    tokenizer = AutoTokenizer.from_pretrained(
        config['model']['name'], 
        trust_remote_code=True
    )
    
    # 准备模型
    if bnb_config:
        model = prepare_model_for_kbit_training(model)
    
    # LoRA 配置
    lora_config = LoraConfig(
        r=config['lora']['r'],
        lora_alpha=config['lora']['alpha'],
        target_modules=config['lora']['target_modules'],
        lora_dropout=config['lora']['dropout'],
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # 加载数据
    print("\n加载训练数据...")
    data_file = "data/train.jsonl"
    if not os.path.exists(data_file):
        print(f"错误: 训练数据不存在: {data_file}")
        print("请将 train.jsonl 放到 data/ 目录")
        return
    
    dataset = load_dataset("json", data_files=data_file)
    print(f"训练样本数: {len(dataset['train'])}")
    
    # 训练参数
    training_args = TrainingArguments(
        output_dir=config['output']['dir'],
        num_train_epochs=config['training']['epochs'],
        per_device_train_batch_size=config['training']['batch_size'],
        gradient_accumulation_steps=config['training']['gradient_accumulation_steps'],
        learning_rate=config['training']['learning_rate'],
        warmup_ratio=config['training']['warmup_ratio'],
        lr_scheduler_type=config['training']['lr_scheduler'],
        logging_steps=10,
        save_strategy=config['output']['save_strategy'],
        fp16=True,
        optim="paged_adamw_8bit",
        report_to="none"
    )
    
    # 训练器
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        dataset_text_field="output",
        max_seq_length=config['model']['max_length'],
        tokenizer=tokenizer,
        args=training_args
    )
    
    # 开始训练
    print("\n开始训练...")
    trainer.train()
    
    # 保存模型
    print("\n保存模型...")
    output_dir = f"{config['output']['dir']}/final"
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print("\n" + "="*50)
    print("训练完成!")
    print(f"模型保存在: {output_dir}")
    print("="*50)

if __name__ == "__main__":
    main()

