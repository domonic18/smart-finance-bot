#!/bin/bash

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 设置 Python 脚本的路径
PYTHON_SCRIPT="$SCRIPT_DIR/../entroy.py"

# 设置 PDF 文件目录
PDF_DIR="$SCRIPT_DIR/../dataset/pdf"

# 调用 entroy.py，传入参数
echo "Running entroy.py to import PDF files..."
python "$PYTHON_SCRIPT" --job importpdf --dir "$PDF_DIR"
