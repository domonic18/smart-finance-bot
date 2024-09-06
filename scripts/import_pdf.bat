@echo off
@REM 配置服务器 IP 和端口
@REM SET CHROMA_SERVER_IP=localhost
@REM SET CHROMA_SERVER_PORT=8000

REM 获取当前脚本所在目录
SET SCRIPT_DIR=%~dp0

REM 设置 Python 脚本的路径
SET PYTHON_SCRIPT=%SCRIPT_DIR%..\app\entroy.py

REM 设置 PDF 文件目录
SET PDF_DIR=%SCRIPT_DIR%..\app\dataset\pdf

REM 调用 entroy.py，传入参数
echo Running entroy.py to import PDF files...
python "%PYTHON_SCRIPT%" --job importpdf --dir "%PDF_DIR%" --db_type chroma
pause
