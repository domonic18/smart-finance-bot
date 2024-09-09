#!/bin/bash

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 设置 Python 脚本的路径
PYTHON_SCRIPT="$SCRIPT_DIR/../app/entrypoint.py"

# 调用 entrypoint.py，传入参数
echo "Running entrypoint.py to renametables to DB..."
python "$PYTHON_SCRIPT" --job renametables

echo "Running entrypoint.py to addindexes to DB..."
python "$PYTHON_SCRIPT" --job addindexes