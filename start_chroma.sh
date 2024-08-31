#!/bin/bash

# 启动 Chroma 数据库
echo "Starting Chroma database..."
chroma run --path chroma_db --port 8000
