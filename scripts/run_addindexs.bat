@echo off
REM 获取当前脚本所在目录
SET SCRIPT_DIR=%~dp0

REM 设置 Python 脚本的路径
SET PYTHON_SCRIPT=%SCRIPT_DIR%..\app\entrypoint.py

REM 调用 entrypoint.py，传入参数
echo Running entrypoint.py to renametables to DB...
python "%PYTHON_SCRIPT%" --job renametables

echo Running entrypoint.py to addindexes to DB...
python "%PYTHON_SCRIPT%" --job addindexes
