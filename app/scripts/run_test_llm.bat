@echo off

REM 获取当前脚本所在目录
SET SCRIPT_DIR=%~dp0

REM 设置 Python 脚本的路径
SET PYTHON_SCRIPT=%SCRIPT_DIR%..\app\utils\util.py

REM 调用 util.py
echo Running util.py to test API-Key
python "%PYTHON_SCRIPT%"

pause
