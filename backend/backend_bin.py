#!/usr/bin/env python3
"""
PyInstaller 入口 — CPQ Agent 后端
被打包为独立可执行文件，Electron 在启动时调用它。
"""
import os
import sys
import uvicorn

# PyInstaller 打包后的资源路径
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 确保 backend 目录在 path 中
sys.path.insert(0, BASE_DIR)

# 导入 server 模块的 app 对象
from server import app

def main():
    port = int(os.environ.get("PORT", "58118"))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"[backend] Starting CPQ Agent service: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info", workers=1)

if __name__ == "__main__":
    main()
