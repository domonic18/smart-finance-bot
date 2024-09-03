#!/bin/bash

# 配置服务器 IP 和端口
# CHROMA_SERVER_IP="localhost"  # chromdb 服务器 IP
# CHROMA_SERVER_PORT=8000       # chromdb 端口号

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 设置 Python 脚本的路径
PYTHON_SCRIPT="$SCRIPT_DIR/../app/rag/pdf_processor.py"

# 调用 pdf_processor.py
echo "Running pdf_processor.py ..."
python "$PYTHON_SCRIPT" 
