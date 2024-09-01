#!/bin/bash


# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 设置 Python 脚本的路径
PYTHON_SCRIPT="$SCRIPT_DIR/../app/utils/util.py"

# 调用 pdf_processor.py
echo "Running util.py to test API-Key"
python "$PYTHON_SCRIPT" 
