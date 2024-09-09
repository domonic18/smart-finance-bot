@echo off
REM 获取当前脚本所在目录
SET SCRIPT_DIR=%~dp0

REM 设置 Python 脚本的路径
SET PYTHON_SCRIPT=%SCRIPT_DIR%..\app\entrypoint.py

REM 调用 entrypoint.py，传入参数
echo Running entrypoint.py to run test_question...
python "%PYTHON_SCRIPT%" --job test_question --start 0 --end 2
