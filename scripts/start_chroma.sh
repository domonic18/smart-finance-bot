#!/bin/bash

# 启动 Chroma 数据库
echo "Starting Chroma database..."
python "app/entrypoint.py" --job startchroma --path chroma_db --port 8000
