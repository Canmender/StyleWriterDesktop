"""
StyleWriter Desktop - 主程序入口
启动 FastAPI 服务 + GUI 管理界面
"""

import sys
import os
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def start_api_server():
    """启动 API 服务"""
    import uvicorn
    from server.api.app import app
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

def main():
    """主函数"""
    import tkinter as tk
    from server.gui.main_window import MainWindow
    
    # 在后台线程启动 API 服务
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # 启动 GUI
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()

