"""
数据清洗模块
支持 txt, md, docx, pdf 等格式的自动清洗
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗器"""
    
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or str(Path(__file__).parent.parent.parent / "data" / "examples")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def clean_file(self, file_path: str) -> Dict:
        """清洗单个文件"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        content = self._read_file(file_path)
        cleaned = self._clean_text(content)
        paragraphs = self._split_paragraphs(cleaned)
        
        output_file = os.path.join(self.output_dir, f"{file_path.stem}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        
        return {
            "original_file": str(file_path),
            "output_file": output_file,
            "original_length": len(content),
            "cleaned_length": len(cleaned),
            "paragraphs": len(paragraphs),
            "status": "success"
        }
    
    def clean_directory(self, dir_path: str) -> List[Dict]:
        """清洗整个目录"""
        dir_path = Path(dir_path)
        results = []
        supported = ['.txt', '.md', '.docx', '.pdf', '.html', '.json']
        
        for file_path in dir_path.rglob("*"):
            if file_path.suffix.lower() in supported:
                try:
                    result = self.clean_file(str(file_path))
                    results.append(result)
                except Exception as e:
                    results.append({"original_file": str(file_path), "status": "error", "error": str(e)})
        
        return results
    
    def _read_file(self, file_path: Path) -> str:
        """读取文件"""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.txt', '.md']:
            return self._read_text(file_path)
        elif suffix == '.docx':
            return self._read_docx(file_path)
        elif suffix == '.pdf':
            return self._read_pdf(file_path)
        elif suffix == '.html':
            return self._read_html(file_path)
        elif suffix == '.json':
            return self._read_json(file_path)
        else:
            return self._read_text(file_path)
    
    def _read_text(self, file_path: Path) -> str:
        """读取文本文件"""
        for enc in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise ValueError(f"无法读取: {file_path}")
    
    def _read_docx(self, file_path: Path) -> str:
        """读取 Word"""
        try:
            import docx
            doc = docx.Document(file_path)
            return '\n\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
        except ImportError:
            raise ImportError("请安装: pip install python-docx")
    
    def _read_pdf(self, file_path: Path) -> str:
        """读取 PDF"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return '\n'.join([page.extract_text() for page in reader.pages])
        except ImportError:
            raise ImportError("请安装: pip install PyPDF2")
    
    def _read_html(self, file_path: Path) -> str:
        """读取 HTML"""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8') as f:
                return BeautifulSoup(f.read(), 'html.parser').get_text(separator='\n')
        except ImportError:
            raise ImportError("请安装: pip install beautifulsoup4")
    
    def _read_json(self, file_path: Path) -> str:
        """读取 JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, str):
                return data
            elif isinstance(data, list):
                return '\n'.join([str(item) for item in data])
            elif isinstance(data, dict):
                for key in ['content', 'text', 'body', 'article']:
                    if key in data:
                        return str(data[key])
                return json.dumps(data, ensure_ascii=False, indent=2)
            return str(data)
    
    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        if not text:
            return ""
        
        # 移除 URL
        text = re.sub(r'http[s]?://\S+', '', text)
        # 移除邮箱
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除 Markdown 格式
        text = re.sub(r'#+ ', '', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        # 移除特殊字符
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        # 规范化空白
        text = re.sub(r'\t', ' ', text)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 移除首尾空白
        text = text.strip()
        # 移除空行
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        
        return '\n'.join(lines)
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """分段"""
        if not text:
            return []
        paragraphs = re.split(r'\n\n+', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def split_into_chunks(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """分块"""
        if not text:
            return []
        
        chunks = []
        paragraphs = self._split_paragraphs(text)
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                if overlap > 0:
                    current_chunk = current_chunk[-overlap:] + "\n\n" + para
                else:
                    current_chunk = para
            else:
                current_chunk = current_chunk + "\n\n" + para if current_chunk else para
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

