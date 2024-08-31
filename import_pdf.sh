#!/bin/bash

# 配置服务器 IP 和端口
CHROMA_SERVER_IP="localhost"  # chromdb 服务器 IP
CHROMA_SERVER_PORT=8000       # chromdb 端口号

# 调用 pdf_processor.py
echo "Running pdf_processor.py with server IP: $CHROMA_SERVER_IP and port: $CHROMA_SERVER_PORT"
python app/rag/pdf_processor.py --host "$CHROMA_SERVER_IP" --port "$CHROMA_SERVER_PORT"
