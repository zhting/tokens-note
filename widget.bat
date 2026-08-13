@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 查找可用的 Python 启动器（优先 pythonw，其次 py -3 -w，最后 python）
set "PY="
where pythonw >nul 2>&1 && set "PY=pythonw"
if not defined PY (
    where py >nul 2>&1 && set "PY=py -3 -w"
)
if not defined PY (
    where python >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo 未找到 Python，请先安装 Python 并勾选"Add Python to PATH"。
    pause
    exit /b 1
)

REM 用 start 异步启动，命令行窗口立即关闭
start "" %PY% "%~dp0widget.py"
