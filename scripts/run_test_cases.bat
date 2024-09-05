@echo off
REM 获取当前脚本所在目录
SET SCRIPT_DIR=%~dp0

REM 设置 Python 脚本的路径
SET PYTHON_SCRIPT=%SCRIPT_DIR%..\app\entroy.py

REM 调用 entroy.py，传入参数
echo Running entroy.py to run test_question...
python "%PYTHON_SCRIPT%" --job test_question --start 0 --end 2
