@echo off
@REM REM 配置服务器 IP 和端口
@REM SET CHROMA_SERVER_IP=localhost
@REM SET CHROMA_SERVER_PORT=8000

REM 获取当前脚本所在目录
SET SCRIPT_DIR=%~dp0

REM 设置 Python 脚本的路径
SET PYTHON_SCRIPT=%SCRIPT_DIR%..\app\rag\pdf_processor.py

REM 调用 pdf_processor.py
echo Running pdf_processor.py ...
python "%PYTHON_SCRIPT%" 
pause
