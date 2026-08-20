"""
主窗口 GUI - 包含数据清洗功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "config" / "settings.json"

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("StyleWriter Desktop - 风格化文章生成器")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        self.config = self._load_config()
        self.agent = None
        self.is_generating = False
        
        # 数据清洗相关
        self.selected_files = []
        
        self._create_ui()
        self._init_agent()
    
    def _load_config(self):
        default = {
            "api": {"provider": "openai", "api_key": "", "base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
            "local_model": {"path": "", "device": "auto", "load_in_4bit": True},
            "rag": {"embedding_model": "BAAI/bge-small-zh-v1.5", "chunk_size": 500, "top_k": 3},
            "generation": {"max_tokens": 2048, "temperature": 0.7}
        }
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    for k in default:
                        if k in saved:
                            default[k].update(saved[k])
                    return default
            except:
                pass
        return default
    
    def _save_config(self):
        os.makedirs(CONFIG_FILE.parent, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _create_ui(self):
        # 菜单
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 选项卡
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 生成区
        self.generate_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.generate_frame, text="  生成区  ")
        self._create_generate_tab()
        
        # 数据清洗
        self.clean_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.clean_frame, text="  数据清洗  ")
        self._create_clean_tab()
        
        # 数据管理
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="  数据管理  ")
        self._create_data_tab()
        
        # 设置区
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="  设置区  ")
        self._create_settings_tab()
        
        # 状态栏
        status_frame = ttk.Frame(self.root, padding="2")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = ttk.Label(status_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT)
        self.agent_status = ttk.Label(status_frame, text="Agent: 未初始化")
        self.agent_status.pack(side=tk.RIGHT)
    
    # ==================== 生成区 ====================
    def _create_generate_tab(self):
        left = ttk.Frame(self.generate_frame, padding="10")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, width=400)
        
        ttk.Label(left, text="文章主题", font=('Microsoft YaHei', 10, 'bold')).pack(anchor=tk.W)
        self.topic_entry = ttk.Entry(left, font=('Microsoft YaHei', 11))
        self.topic_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(left, text="目标字数", font=('Microsoft YaHei', 10, 'bold')).pack(anchor=tk.W)
        self.length_var = tk.IntVar(value=1000)
        length_frame = ttk.Frame(left)
        length_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Scale(length_frame, from_=200, to=5000, variable=self.length_var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.length_label = ttk.Label(length_frame, text="1000字", width=8)
        self.length_label.pack(side=tk.LEFT, padx=5)
        self.length_var.trace_add('write', lambda *a: self.length_label.config(text=f"{self.length_var.get()}字"))
        
        ttk.Label(left, text="写作要求", font=('Microsoft YaHei', 10, 'bold')).pack(anchor=tk.W)
        self.requirements_text = scrolledtext.ScrolledText(left, height=4, font=('Microsoft YaHei', 9))
        self.requirements_text.pack(fill=tk.X, pady=(0, 10))
        self.requirements_text.insert(tk.END, "通俗易懂，有条理")
        
        ttk.Label(left, text="使用模型", font=('Microsoft YaHei', 10, 'bold')).pack(anchor=tk.W)
        self.use_model_var = tk.StringVar(value="api")
        ttk.Radiobutton(left, text="云端 API", variable=self.use_model_var, value="api").pack(anchor=tk.W)
        ttk.Radiobutton(left, text="本地微调模型", variable=self.use_model_var, value="local").pack(anchor=tk.W)
        
        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        self.generate_btn = tk.Button(left, text="生成文章", font=('Microsoft YaHei', 12, 'bold'),
                                      bg="#4CAF50", fg="white", command=self._generate_article, height=2)
        self.generate_btn.pack(fill=tk.X)
        
        self.progress = ttk.Progressbar(left, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
        
        right = ttk.Frame(self.generate_frame, padding="10")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        toolbar = ttk.Frame(right)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(toolbar, text="复制", command=self._copy_output).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="保存", command=self._save_output).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="清空", command=self._clear_output).pack(side=tk.LEFT, padx=2)
        self.word_count_label = ttk.Label(toolbar, text="字数: 0")
        self.word_count_label.pack(side=tk.RIGHT)
        
        self.output_text = scrolledtext.ScrolledText(right, font=('Microsoft YaHei', 11), wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    # ==================== 数据清洗 ====================
    def _create_clean_tab(self):
        # 顶部：文件选择
        file_frame = ttk.LabelFrame(self.clean_frame, text="选择文件", padding="10")
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="选择文件", command=self._select_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="选择文件夹", command=self._select_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="清空列表", command=self._clear_file_list).pack(side=tk.LEFT, padx=2)
        
        self.file_count_label = ttk.Label(btn_frame, text="已选择: 0 个文件")
        self.file_count_label.pack(side=tk.RIGHT)
        
        # 文件列表
        list_frame = ttk.LabelFrame(self.clean_frame, text="文件列表", padding="10")
        list_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_listbox = tk.Listbox(list_frame, height=4, font=('Consolas', 9))
        self.file_listbox.pack(fill=tk.X)
        
        # 清洗选项
        options_frame = ttk.LabelFrame(self.clean_frame, text="清洗选项", padding="10")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        options_grid = ttk.Frame(options_frame)
        options_grid.pack(fill=tk.X)
        
        ttk.Label(options_grid, text="分块大小:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.chunk_size_var = tk.IntVar(value=500)
        ttk.Spinbox(options_grid, from_=100, to=2000, increment=100, textvariable=self.chunk_size_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(options_grid, text="重叠长度:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.overlap_var = tk.IntVar(value=50)
        ttk.Spinbox(options_grid, from_=0, to=200, increment=10, textvariable=self.overlap_var, width=10).grid(row=0, column=3, padx=5)
        
        self.auto_index_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_grid, text="清洗后自动创建向量索引", variable=self.auto_index_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5)
        
        # 开始清洗按钮
        btn_frame2 = ttk.Frame(self.clean_frame)
        btn_frame2.pack(fill=tk.X, padx=10, pady=5)
        
        self.clean_btn = tk.Button(btn_frame2, text="开始清洗", font=('Microsoft YaHei', 11, 'bold'),
                                   bg="#2196F3", fg="white", command=self._start_clean)
        self.clean_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(btn_frame2, text="查看结果", command=self._view_clean_result).pack(side=tk.LEFT, padx=2)
        
        self.clean_progress = ttk.Progressbar(btn_frame2, mode='determinate')
        self.clean_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # 清洗日志
        log_frame = ttk.LabelFrame(self.clean_frame, text="清洗日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.clean_log = scrolledtext.ScrolledText(log_frame, height=8, font=('Consolas', 9))
        self.clean_log.pack(fill=tk.BOTH, expand=True)
    
    # ==================== 数据管理 ====================
    def _create_data_tab(self):
        import_frame = ttk.LabelFrame(self.data_frame, text="导入示例文章", padding="10")
        import_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_frame = ttk.Frame(import_frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="导入文件", command=self._import_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="导入文件夹", command=self._import_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="清空", command=self._clear_data).pack(side=tk.LEFT, padx=2)
        self.data_count_label = ttk.Label(btn_frame, text="已导入: 0 篇")
        self.data_count_label.pack(side=tk.RIGHT)
        
        list_frame = ttk.LabelFrame(self.data_frame, text="文章列表", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.data_listbox = tk.Listbox(list_frame, font=('Microsoft YaHei', 9))
        self.data_listbox.pack(fill=tk.BOTH, expand=True)
        
        vector_frame = ttk.LabelFrame(self.data_frame, text="向量库", padding="10")
        vector_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(vector_frame, text="创建向量索引", command=self._create_index).pack(side=tk.LEFT, padx=2)
        ttk.Button(vector_frame, text="测试检索", command=self._test_search).pack(side=tk.LEFT, padx=2)
        self.index_status = ttk.Label(vector_frame, text="状态: 未创建")
        self.index_status.pack(side=tk.RIGHT)
        
        self._refresh_list()
    
    # ==================== 设置区 ====================
    def _create_settings_tab(self):
        # API 设置
        api_frame = ttk.LabelFrame(self.settings_frame, text="API 设置", padding="10")
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        row1 = ttk.Frame(api_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="API Key:", width=10).pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar(value=self.config["api"]["api_key"])
        ttk.Entry(row1, textvariable=self.api_key_var, width=50, show="*").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        row2 = ttk.Frame(api_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Base URL:", width=10).pack(side=tk.LEFT)
        self.base_url_var = tk.StringVar(value=self.config["api"]["base_url"])
        ttk.Entry(row2, textvariable=self.base_url_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        row3 = ttk.Frame(api_frame)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="模型:", width=10).pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value=self.config["api"]["model"])
        ttk.Entry(row3, textvariable=self.model_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # 本地模型设置
        local_frame = ttk.LabelFrame(self.settings_frame, text="本地模型设置", padding="10")
        local_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 模型路径
        row4 = ttk.Frame(local_frame)
        row4.pack(fill=tk.X, pady=2)
        ttk.Label(row4, text="模型路径:", width=10).pack(side=tk.LEFT)
        self.local_model_var = tk.StringVar(value=self.config["local_model"]["path"])
        ttk.Entry(row4, textvariable=self.local_model_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(row4, text="浏览", command=self._browse_model).pack(side=tk.LEFT, padx=5)
        
        # 引擎选择
        row5 = ttk.Frame(local_frame)
        row5.pack(fill=tk.X, pady=2)
        ttk.Label(row5, text="推理引擎:", width=10).pack(side=tk.LEFT)
        self.engine_var = tk.StringVar(value=self.config["local_model"].get("engine", "auto"))
        ttk.Combobox(row5, textvariable=self.engine_var, values=["auto", "llama_cpp", "transformers"], width=15, state='readonly').pack(side=tk.LEFT, padx=5)
        ttk.Label(row5, text="(auto: GGUF用llama.cpp, 其他用transformers)").pack(side=tk.LEFT, padx=5)
        
        # llama.cpp 设置
        llama_frame = ttk.LabelFrame(self.settings_frame, text="llama.cpp 设置", padding="10")
        llama_frame.pack(fill=tk.X, padx=10, pady=5)
        
        row6 = ttk.Frame(llama_frame)
        row6.pack(fill=tk.X, pady=2)
        ttk.Label(row6, text="llama.cpp路径:", width=12).pack(side=tk.LEFT)
        self.llama_path_var = tk.StringVar(value=self.config.get("llama_cpp", {}).get("path", ""))
        ttk.Entry(row6, textvariable=self.llama_path_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(row6, text="浏览", command=self._browse_llama).pack(side=tk.LEFT, padx=5)
        
        row7 = ttk.Frame(llama_frame)
        row7.pack(fill=tk.X, pady=2)
        ttk.Label(row7, text="GPU层数:", width=12).pack(side=tk.LEFT)
        self.gpu_layers_var = tk.IntVar(value=self.config.get("llama_cpp", {}).get("gpu_layers", 999))
        ttk.Spinbox(row7, from_=0, to=999, textvariable=self.gpu_layers_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(row7, text="(999=全部GPU, 0=纯CPU)").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row7, text="上下文大小:", width=12).pack(side=tk.LEFT, padx=(20, 0))
        self.context_var = tk.IntVar(value=self.config.get("llama_cpp", {}).get("context_size", 4096))
        ttk.Spinbox(row7, from_=512, to=32768, increment=512, textvariable=self.context_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        btn_frame = ttk.Frame(self.settings_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="保存设置", command=self._save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="检查环境", command=self._check_env).pack(side=tk.LEFT, padx=5)
        
        # 环境状态
        env_frame = ttk.LabelFrame(self.settings_frame, text="环境状态", padding="10")
        env_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.env_status = scrolledtext.ScrolledText(env_frame, height=8, font=('Consolas', 9))
        self.env_status.pack(fill=tk.BOTH, expand=True)

    def _init_agent(self):
        def init():
            try:
                from server.agent.hybrid_agent import HybridAgent
                self.agent = HybridAgent()
                self.agent.initialize()
                self.root.after(0, lambda: self.agent_status.config(text="Agent: 已就绪"))
            except Exception as e:
                self.root.after(0, lambda: self.agent_status.config(text=f"Agent: 错误"))
                print(f"Agent init error: {e}")
        threading.Thread(target=init, daemon=True).start()
    
    # ==================== 生成功能 ====================
    def _generate_article(self):
        topic = self.topic_entry.get().strip()
        if not topic:
            messagebox.showwarning("提示", "请输入主题")
            return
        
        if self.is_generating:
            return
        
        self.is_generating = True
        self.generate_btn.config(state=tk.DISABLED)
        self.progress.start()
        
        def generate():
            try:
                result = self.agent.generate(
                    topic=topic,
                    length=self.length_var.get(),
                    requirements=self.requirements_text.get("1.0", tk.END).strip(),
                    use_model=self.use_model_var.get()
                )
                self.root.after(0, lambda: self._update_output(result["content"]))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
            finally:
                self.root.after(0, self._generate_complete)
        threading.Thread(target=generate, daemon=True).start()
    
    def _update_output(self, text):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)
        self.word_count_label.config(text=f"字数: {len(text)}")
    
    def _generate_complete(self):
        self.is_generating = False
        self.generate_btn.config(state=tk.NORMAL)
        self.progress.stop()
        self.status_label.config(text="生成完成")
    
    def _copy_output(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
    
    def _save_output(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _clear_output(self):
        self.output_text.delete("1.0", tk.END)
        self.word_count_label.config(text="字数: 0")
    
    # ==================== 数据清洗功能 ====================
    def _select_files(self):
        file_paths = filedialog.askopenfilenames(
            title="选择文件",
            filetypes=[
                ("所有支持格式", "*.txt *.md *.docx *.pdf *.html *.json"),
                ("文本文件", "*.txt"),
                ("Markdown", "*.md"),
                ("Word 文档", "*.docx"),
                ("PDF 文件", "*.pdf"),
                ("HTML 文件", "*.html"),
                ("JSON 文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_paths:
            self.selected_files = list(file_paths)
            self._update_file_list()
    
    def _select_folder(self):
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            supported = ['.txt', '.md', '.docx', '.pdf', '.html', '.json']
            self.selected_files = []
            
            for ext in supported:
                self.selected_files.extend([str(f) for f in Path(folder).rglob(f"*{ext}")])
            
            self._update_file_list()
    
    def _update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for f in self.selected_files:
            self.file_listbox.insert(tk.END, Path(f).name)
        
        self.file_count_label.config(text=f"已选择: {len(self.selected_files)} 个文件")
    
    def _clear_file_list(self):
        self.selected_files = []
        self.file_listbox.delete(0, tk.END)
        self.file_count_label.config(text="已选择: 0 个文件")
    
    def _start_clean(self):
        if not self.selected_files:
            messagebox.showwarning("提示", "请先选择文件")
            return
        
        self.clean_btn.config(state=tk.DISABLED)
        
        def clean():
            try:
                from server.core.data_cleaner import DataCleaner
                
                cleaner = DataCleaner()
                total = len(self.selected_files)
                success = 0
                
                self._clean_log(f"开始清洗 {total} 个文件...")
                self._clean_log("-" * 50)
                
                for i, file_path in enumerate(self.selected_files):
                    try:
                        self._clean_log(f"[{i+1}/{total}] {Path(file_path).name}")
                        
                        result = cleaner.clean_file(file_path)
                        
                        self._clean_log(f"  原始: {result['original_length']} 字符")
                        self._clean_log(f"  清洗后: {result['cleaned_length']} 字符")
                        self._clean_log(f"  段落: {result['paragraphs']}")
                        self._clean_log(f"  状态: 成功")
                        
                        success += 1
                        
                    except Exception as e:
                        self._clean_log(f"  状态: 失败 - {str(e)}")
                    
                    self.root.after(0, lambda v=(i+1)/total*100: self.clean_progress.config(value=v))
                
                self._clean_log("-" * 50)
                self._clean_log(f"清洗完成: {success}/{total} 成功")
                
                # 自动创建索引
                if self.auto_index_var.get() and success > 0:
                    self._clean_log("\n正在创建向量索引...")
                    if self.agent:
                        self.agent.create_index()
                        self._clean_log("向量索引创建完成")
                
                self.root.after(0, lambda: messagebox.showinfo("完成", f"清洗完成: {success}/{total}"))
                
            except Exception as e:
                self._clean_log(f"错误: {str(e)}")
            finally:
                self.root.after(0, lambda: self.clean_btn.config(state=tk.NORMAL))
                self._refresh_list()
        
        threading.Thread(target=clean, daemon=True).start()
    
    def _clean_log(self, message):
        def update():
            self.clean_log.insert(tk.END, message + "\n")
            self.clean_log.see(tk.END)
        self.root.after(0, update)
    
    def _view_clean_result(self):
        examples_dir = PROJECT_ROOT / "data" / "examples"
        if examples_dir.exists():
            os.startfile(str(examples_dir))
    
    # ==================== 数据管理功能 ====================
    def _import_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("文本", "*.txt")])
        if file_paths:
            examples_dir = PROJECT_ROOT / "data" / "examples"
            examples_dir.mkdir(exist_ok=True)
            count = 0
            for path in file_paths:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    with open(examples_dir / Path(path).name, 'w', encoding='utf-8') as f:
                        f.write(content)
                    count += 1
                except:
                    pass
            self._refresh_list()
            messagebox.showinfo("成功", f"导入 {count} 篇")
    
    def _import_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            examples_dir = PROJECT_ROOT / "data" / "examples"
            examples_dir.mkdir(exist_ok=True)
            count = 0
            for f in Path(folder).glob("*.txt"):
                try:
                    with open(f, 'r', encoding='utf-8') as content:
                        text = content.read()
                    with open(examples_dir / f.name, 'w', encoding='utf-8') as out:
                        out.write(text)
                    count += 1
                except:
                    pass
            self._refresh_list()
            messagebox.showinfo("成功", f"导入 {count} 篇")
    
    def _clear_data(self):
        if messagebox.askyesno("确认", "清空所有数据？"):
            examples_dir = PROJECT_ROOT / "data" / "examples"
            if examples_dir.exists():
                for f in examples_dir.glob("*.txt"):
                    f.unlink()
            self._refresh_list()
    
    def _refresh_list(self):
        self.data_listbox.delete(0, tk.END)
        examples_dir = PROJECT_ROOT / "data" / "examples"
        count = 0
        if examples_dir.exists():
            for f in sorted(examples_dir.glob("*.txt")):
                self.data_listbox.insert(tk.END, f.name)
                count += 1
        self.data_count_label.config(text=f"已导入: {count} 篇")
    
    def _create_index(self):
        if self.agent:
            def create():
                try:
                    self.root.after(0, lambda: self.index_status.config(text="状态: 创建中..."))
                    self.agent.create_index()
                    self.root.after(0, lambda: self.index_status.config(text="状态: 已创建"))
                    self.root.after(0, lambda: messagebox.showinfo("成功", "索引创建完成"))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
            threading.Thread(target=create, daemon=True).start()
    
    def _test_search(self):
        if not self.agent:
            return
        query = tk.simpledialog.askstring("测试", "输入关键词:")
        if query:
            results = self.agent.search(query)
            messagebox.showinfo("结果", f"找到 {len(results)} 条")
    
    def _browse_model(self):
        path = filedialog.askdirectory()
        if path:
            self.local_model_var.set(path)
    
    def _save_settings(self):
        self.config["api"]["api_key"] = self.api_key_var.get()
        self.config["api"]["base_url"] = self.base_url_var.get()
        self.config["api"]["model"] = self.model_var.get()
        self.config["local_model"]["path"] = self.local_model_var.get()
        self.config["local_model"]["engine"] = self.engine_var.get()
        self.config["llama_cpp"]["path"] = self.llama_path_var.get()
        self.config["llama_cpp"]["gpu_layers"] = self.gpu_layers_var.get()
        self.config["llama_cpp"]["context_size"] = self.context_var.get()
        self._save_config()
        messagebox.showinfo("成功", "设置已保存")
        self._init_agent()



