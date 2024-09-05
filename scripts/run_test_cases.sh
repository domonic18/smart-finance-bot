#!/bin/bash

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 设置 Python 脚本的路径
PYTHON_SCRIPT="$SCRIPT_DIR/../app/entroy.py"

# 调用 entroy.py，传入参数
echo "Running entroy.py to run test_question..."
python "$PYTHON_SCRIPT" --job test_question --start 0 --end 100